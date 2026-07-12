# World Seed manifest format

A World Seed is the pre-gameplay-adaptation Canon layer — see `seed.py`'s module docstring for why this is a different thing from a World IR, and `docs/whitepapers/06-novel-to-mud-world-adaptation.md` for the full design this implements.

## Manifest

```json
{
  "seed_id": "mingyun_zhiyu",
  "seed_version": "0.1.0",
  "schema_version": "0.1.0",
  "source_work": {"title": "命運之欲", "rights_status": "user_owned"},
  "tables": {
    "characters": {
      "file": "data/characters.csv",
      "id_field": "id",
      "required_fields": ["id", "name"],
      "references": {"faction": "factions"}
    }
  },
  "documents": {
    "axioms": {
      "file": "data/axioms.json",
      "record_path": "axioms",
      "id_field": "id",
      "required_fields": ["id", "statement"]
    },
    "timeline": {
      "file": "data/timeline.json"
    }
  }
}
```

- **`tables`** — CSV files. Each becomes a `SourceTable`: a flat list of dict records, `id_field` names which column is the unique key (use `null` for tables with no natural id, e.g. `level_curve.csv`), `required_fields` are checked non-empty on every row, `references` declares that column `X` should contain an id that exists in table/document `Y` (both are checked by `validate_seed()` — see below).
- **`documents`** — JSON files. Omit `record_path` to load the whole file as one opaque document (e.g. `timeline.json`, which isn't a flat record list — nobody's iterating "timeline entries" generically). Set `record_path` (dotted, e.g. `"axioms"` or `"a.b.c"`) to point at a list *inside* the JSON that should behave exactly like a CSV table — same `id_field`/`required_fields`/`references` options apply, and it shows up under `seed.tables`, not `seed.documents`.

## Why generic instead of per-domain dataclasses

`world_ir` does not define a `Character` or `City` class. A real seed in active development keeps adding new CSV/JSON files as the setting grows (species subtypes, hybrid rules, item drafts...) — hardcoding Python classes per worldbuilding concept would go stale every time that happens. The manifest is the schema; `SourceTable` is just records + the declared rules to check against them.

## What `validate_seed()` checks (and what it deliberately doesn't)

Checked, because a computer can check these for certain:
- every declared file exists and parses;
- every `required_fields` entry is non-empty on every row;
- every `id_field` value is unique within its table;
- every declared `references` value either resolves to a real id in the target table, or is empty/`NA` (absent references — e.g. a character with no faction — are not errors).

Not checked, because it's Canon-quality judgment, not structure: whether an axiom is actually true of the setting, whether a character's stated level is balanced, whether a description is good writing. That's for a human (or a much later, much smarter pass) to judge — this layer only proves the data is internally consistent enough to build on.

## The `NA` convention

Real seed data (see `worlds/mingyun_zhiyu/data/README.md`'s own field convention, independently converged on before this loader existed) uses the literal string `NA` to mean "the source material doesn't say" — distinct from an empty cell, which usually means "not applicable here." `validate_seed()` counts `NA` cells per table in its report (`provenance.na_field_counts_by_table`) rather than treating them as errors — the whole point of paper 06's Canon-tier model is that "we don't know yet" has to stay visible, not get silently papered over.

## CSV multi-value cells

Seed CSVs don't use commas to separate multiple values *within* a cell (the comma is already the column delimiter) — they use `、` or `/` for enumeration and `;` for clause separation, so the file stays editable in a plain spreadsheet without comma-escaping headaches. `seed.py`'s `split_multi_value()` helper splits on all three; call it explicitly on whichever column you know is multi-value — this module doesn't guess which columns need it.
