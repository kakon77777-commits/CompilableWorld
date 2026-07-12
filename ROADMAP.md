# CompilableWorld — Status & Roadmap

Six design documents now exist (`docs/whitepapers/`), covering a wide arc from general methodology to aspirational natural-language gameplay. This file exists so nobody — including a future session — has to reread all six to answer "what's actually real right now." Updated 2026-07-13.

## What's actually built and working

- **`world_ir/`** — a real Python package: `schema.py` (World IR data model), `validate.py` (schema/reachability/quest-DAG checks), `compile_evennia.py` (deterministic World IR → Evennia batch-command compiler). World IR today is **plain hand-authored YAML only** — no JSON/CSV/Manifest ingestion yet (see gap below).
- **A real, running Evennia game** (`game/`), forked engine as a git submodule (`engine/evennia`), Python 3.14.5, verified end-to-end over a live telnet connection.
- **Traditional Chinese localization**: command aliases, the object/room display layer (via Evennia's own under-used gettext catalog), the login/connection screen, and the `help` command's structural chrome. Individual command feedback text (get/drop/give's success messages) is a known, described gap — not attempted, needs its own Chinese-aware verb-conjugation logic.
- **The `mud-world-engineering` Claude Code Skill** (`.claude/skills/`) — orchestrates the MVP loop (source → World Understanding → World IR → Validate → Compile → AI test-player → Report) and calls the real compiler, not LLM freehand generation.
- **One toy world proven end-to-end**: `black_tide_city` (3 rooms, 1 NPC, 1 quest) — compiled, loaded into the live server, walked, verified correct.
- **One real-scale world in progress** (a separate, parallel conversation): `worlds/mingyun_zhiyu/` — a genuine novel (命運之欲) being adapted, currently as a hand-built `data/` folder of JSON/CSV files plus a `world-ir.yaml` slice. This is the first real stress test of the whole pipeline, and it's exactly what surfaced the gap below.

## What's designed but not built

| Paper | Proposes | Status |
|---|---|---|
| 01 — MSSP-Scale Skill | General methodology for organizing large AI skill systems | **Applied**, not "implemented" — this project's own structure and the Skill's internal org follow it. No further work needed unless building another large skill system. |
| 02 — MUD World Engineering MSSP | MSSP applied to MUD engineering specifically | **Applied** — informed the Skill's 7-stage structure. Superseded on overlapping ground by 03. |
| 03 — Compilable World Architecture | The core pipeline + risk-graded mutation (L0–L4) + event-sourced state (snapshot + event log) + AI-player test metrics | **Partially implemented.** The core pipeline is real (see above). Risk-graded mutation levels and event-sourced state (patches, snapshots, event log, rollback) are **not built** — the compiler today only does one-shot fresh world creation, no patching an existing live world. |
| 04 — Authoring Layer (JSON/CSV/Manifest) | A JSON/CSV/Manifest layer between raw source and World IR, for data too large for hand-authored YAML | **Not implemented.** Largely **superseded by 06** (World Seed Package is a superset of this idea) — read 06 first. |
| 05 — Hierarchical State-Machine MUD | Natural-language player actions → AI-compiled Action IR → hierarchical FSMs → event sourcing | **Not implemented, aspirational.** The MVP is still classic verb-target commands (get/drop/look/etc.). No near-term work planned here. |
| 06 — Novel-to-MUD World Adaptation | Two-stage AI (offline novel→World Seed Package adaptation, vs. in-game local generation), Canon tiers (Source/Adapted/Generated), entity resolution, timeline reconstruction | **Not implemented in `world_ir/`**, but this is precisely the gap the parallel session's `mingyun_zhiyu` work is hitting *right now*, by hand. This is the highest-leverage next engineering target. |

## The actual gap, stated plainly

`world_ir/schema.py` only parses a single flat YAML file. Papers 04 and 06 both point at the same real problem: a novel-scale world doesn't fit in one hand-authored YAML file — it needs a proper multi-file Authoring Layer (JSON for nested/structured data, CSV for large flat tables like hundreds of characters, a Manifest as the single compile entry point), plus (per paper 06) a two-stage split between *offline* world adaptation and *in-game* local generation, plus Canon-tier tracking so a novel's stated fact, a gameplay adaptation of that fact, and an AI's later invention never get silently conflated.

The parallel session's `worlds/mingyun_zhiyu/data/` folder is already, informally, most of a World Seed Package — CSVs for characters/cities/factions/species, JSON for axioms/timeline/magic system. It just isn't validated, manifested, or loaded by `world_ir/` yet, because `world_ir/` doesn't know how to read anything but one YAML file.

## Suggested priority order (Neo's call, not decided here)

1. **World Seed Package ingestion in `world_ir/`** (papers 04+06) — a `manifest.json` loader, JSON/CSV parsers, a normalization step producing the same `WorldIR` object `validate.py`/`compile_evennia.py` already consume. This unblocks the in-progress `mingyun_zhiyu` world directly and is the most concrete, already-justified-by-real-need next step.
2. **Patch/event-sourcing** (paper 03's unbuilt half) — needed once a world needs to be *expanded* rather than built fresh each time; not urgent while everything is still first-build.
3. **Action IR / hierarchical state machines** (paper 05) — genuinely long-term; no current work depends on it.

This file should get updated whenever a paper moves from "designed" to "implemented," or when priorities change — it's meant to stay short and honest, not to become another whitepaper.
