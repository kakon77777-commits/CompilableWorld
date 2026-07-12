"""World Seed Package loading — papers 04 (Authoring Layer) and 06 (Novel-to-MUD
World Adaptation), which paper 06 subsumes on overlapping ground.

A World Seed is NOT a World IR. It's the layer *before* gameplay adaptation:
canonical facts about a setting (characters, factions, cities, axioms, economy,
timeline...) as extracted/authored from source material, with provenance kept
all the way through. A World IR (schema.py) is downstream of this — the result
of *adapting* a Seed's Canon into MUD-playable rooms/quests/rules (paper 06
ch.9's "gameplay adaptation operator"). Conflating the two is exactly the
mistake paper 06 ch.6.2 warns about (character belief vs. world fact) one
layer up: Seed data is "what's true/claimed about the setting," not "what a
MUD session is." Don't feed a WorldSeed straight into compile_evennia.py.

Deliberately generic, not hardcoded to specific table names. A real seed in
active development (see worlds/mingyun_zhiyu/data/ — not owned by this module,
read-only reference) keeps adding new CSV/JSON files as the setting grows
(demon subspecies, hybrid rules, item drafts...); hardcoding a `Character` or
`City` dataclass here would go stale every time that happens. Instead each
table/document is loaded as plain records, and a lightweight manifest declares
per-source structure (id field, required fields, cross-references) so
validation stays generic and declarative rather than one-Python-class-per-
worldbuilding-concept.

Manifest shape (see SEED_FORMAT.md in this directory for the full spec):

    {
      "seed_id": "...", "seed_version": "0.1.0", "schema_version": "0.1.0",
      "source_work": {"title": "...", "rights_status": "user_owned"},
      "tables": {
        "characters": {"file": "data/characters.csv", "id_field": "id",
                        "required_fields": ["id", "name"],
                        "references": {"faction": "factions"}}
      },
      "documents": {
        "axioms": {"file": "data/axioms.json", "record_path": "axioms", "id_field": "id"}
      }
    }

`tables` are CSV-backed (list of flat records). `documents` are JSON-backed —
`record_path` (dotted, optional) points at a list within the JSON to treat the
same way as a table; omit it to load the whole JSON as one opaque document
(e.g. timeline.json, which isn't a flat record list).
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

NA_SENTINEL = "NA"


@dataclass
class SourceTable:
    """One manifest-declared CSV table or JSON record-list, loaded as plain dicts.
    `raw_field_values` are kept as-is (strings from CSV, whatever JSON gave for
    documents) — this module does not interpret domain semantics like the
    "、"/"/"/";" multi-value cell convention real seed authors use; see
    `split_multi_value()` for callers that need to unpack a cell on demand."""

    name: str
    records: list[dict]
    id_field: str | None
    required_fields: list[str] = field(default_factory=list)
    references: dict[str, str] = field(default_factory=dict)  # column -> target table/document name
    source_file: str = ""

    def by_id(self) -> dict[str, dict]:
        if not self.id_field:
            return {}
        return {r[self.id_field]: r for r in self.records if r.get(self.id_field)}


@dataclass
class WorldSeed:
    seed_id: str
    seed_version: str
    schema_version: str
    source_work: dict
    tables: dict[str, SourceTable]
    documents: dict[str, object]  # name -> parsed JSON (dict/list), for non-record documents
    manifest_path: Path
    raw_manifest: dict


def split_multi_value(cell: str) -> list[str]:
    """Real seed CSVs (see worlds/mingyun_zhiyu/data/README.md's own field
    convention) deliberately don't use commas to separate multi-value cells —
    a plain comma is reserved for the CSV column delimiter itself, so cell
    content uses '、' or '/' for enumeration and ';' for clause separation.
    This lets a human open the file in Excel/Numbers without commas inside
    Chinese content shifting columns. Splits on any of the three; callers who
    need finer control (e.g. only ';' clauses, not '/' items) should split
    the raw string themselves instead of calling this."""
    if cell is None or cell == NA_SENTINEL:
        return []
    import re
    parts = re.split(r"[、/;]", cell)
    return [p.strip() for p in parts if p.strip()]


def _get_path(doc, dotted_path: str):
    cur = doc
    for part in dotted_path.split("."):
        cur = cur[part]
    return cur


def load_seed(manifest_path: str | Path) -> WorldSeed:
    manifest_path = Path(manifest_path)
    seed_root = manifest_path.parent
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    tables: dict[str, SourceTable] = {}
    for name, spec in (manifest.get("tables") or {}).items():
        file_path = seed_root / spec["file"]
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            records = list(csv.DictReader(f))
        tables[name] = SourceTable(
            name=name,
            records=records,
            id_field=spec.get("id_field"),
            required_fields=list(spec.get("required_fields") or []),
            references=dict(spec.get("references") or {}),
            source_file=spec["file"],
        )

    documents: dict[str, object] = {}
    for name, spec in (manifest.get("documents") or {}).items():
        file_path = seed_root / spec["file"]
        with open(file_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        record_path = spec.get("record_path")
        if record_path:
            records = _get_path(doc, record_path)
            tables[name] = SourceTable(
                name=name,
                records=records,
                id_field=spec.get("id_field"),
                required_fields=list(spec.get("required_fields") or []),
                references=dict(spec.get("references") or {}),
                source_file=spec["file"],
            )
        else:
            documents[name] = doc

    return WorldSeed(
        seed_id=manifest.get("seed_id", manifest_path.stem),
        seed_version=manifest.get("seed_version", "0.0.0"),
        schema_version=manifest.get("schema_version", "0.0.0"),
        source_work=manifest.get("source_work") or {},
        tables=tables,
        documents=documents,
        manifest_path=manifest_path,
        raw_manifest=manifest,
    )
