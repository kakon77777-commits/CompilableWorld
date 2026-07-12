"""Structural validation for a WorldSeed — generic, declarative, per the
manifest's own `id_field`/`required_fields`/`references` declarations (see
seed.py's module docstring). Deliberately does NOT validate worldbuilding
semantics (is this axiom actually true of the setting, does this character's
level make sense) — that's Canon-quality judgment for a human or a much
higher-level pass, not structural validation. This only checks what a
computer can check for certain: required fields present, IDs unique, declared
references resolve to something that exists.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .seed import NA_SENTINEL, WorldSeed


@dataclass
class SeedReport:
    ok: bool
    seed_id: str
    seed_version: str
    table_counts: dict[str, int] = field(default_factory=dict)
    document_names: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)
    duplicate_ids: list[str] = field(default_factory=list)
    unresolved_references: list[str] = field(default_factory=list)
    na_field_summary: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "seed_report": {
                "seed_id": self.seed_id,
                "seed_version": self.seed_version,
                "tables": self.table_counts,
                "documents": self.document_names,
            },
            "validation": {
                "missing_required_fields": self.missing_required_fields,
                "duplicate_ids": self.duplicate_ids,
                "unresolved_references": self.unresolved_references,
            },
            "provenance": {
                # NA count per table isn't an error — paper 06's whole point is
                # that "we don't know yet" must stay visible, not silently
                # filled in. This just surfaces how much of each table is gaps.
                "na_field_counts_by_table": self.na_field_summary,
            },
        }


def validate_seed(seed: WorldSeed) -> SeedReport:
    missing_required = []
    duplicate_ids = []
    unresolved_refs = []
    table_counts = {}
    na_summary = {}

    for name, table in seed.tables.items():
        table_counts[name] = len(table.records)

        seen_ids = set()
        na_count = 0
        for i, record in enumerate(table.records):
            for req in table.required_fields:
                val = record.get(req)
                if val is None or val == "":
                    missing_required.append(f"{name}[{i}] missing required field '{req}'")

            if table.id_field:
                rid = record.get(table.id_field)
                if rid:
                    if rid in seen_ids:
                        duplicate_ids.append(f"{name}: duplicate id '{rid}'")
                    seen_ids.add(rid)

            na_count += sum(1 for v in record.values() if v == NA_SENTINEL)
        if na_count:
            na_summary[name] = na_count

    # Cross-table reference resolution: table X's column C is declared to
    # reference table Y — every non-NA, non-empty value in column C should be
    # a real id in Y. This is deliberately lenient about *which* values count
    # as "no reference" (NA and empty both mean "not applicable here"), since
    # real seed data legitimately has characters with no faction, items with
    # no owner, etc. — that's not a structural error, just an absent edge.
    id_indexes = {name: table.by_id() for name, table in seed.tables.items()}
    for name, table in seed.tables.items():
        for column, target_table_name in table.references.items():
            target_ids = id_indexes.get(target_table_name)
            if target_ids is None:
                unresolved_refs.append(
                    f"{name}.{column} declares a reference to undefined table '{target_table_name}'"
                )
                continue
            for i, record in enumerate(table.records):
                val = record.get(column)
                if not val or val == NA_SENTINEL:
                    continue
                if val not in target_ids:
                    unresolved_refs.append(
                        f"{name}[{i}].{column} = '{val}' not found in '{target_table_name}'"
                    )

    ok = not missing_required and not duplicate_ids and not unresolved_refs

    return SeedReport(
        ok=ok,
        seed_id=seed.seed_id,
        seed_version=seed.seed_version,
        table_counts=table_counts,
        document_names=sorted(seed.documents.keys()),
        missing_required_fields=missing_required,
        duplicate_ids=duplicate_ids,
        unresolved_references=unresolved_refs,
        na_field_summary=na_summary,
    )
