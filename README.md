# CompilableWorld

An AI-driven pipeline that turns novels, world-bibles, and worldbuilding notes into validated, playable text-based multiplayer worlds (MUDs) — and, longer-term, other runtime targets built from the same world data. MUD is the first Runtime Adapter, not the ceiling.

```
Source text → World Understanding → World IR → Validation → World Compiler → Runtime → AI test-player → Patch → Versioned Release
```

AI proposes; the system validates; version control protects. No single AI pass both authors unreviewed world content and marks it approved.

## Layout

```
CompilableWorld/
├── docs/whitepapers/       — the 6 design documents this project is built from, read in order
│                             (Traditional Chinese originals; 04/05 also have English translations)
├── world_ir/               — Python package: World IR schema, validator, provenance tracking
├── worlds/                 — generated World IR documents (one subfolder per world)
├── engine/evennia/         — the Evennia engine, as a git submodule (see below)
├── game/                   — an actual initialized Evennia game dir using the engine above
└── .claude/skills/mud-world-engineering/  — the Claude Code Skill that runs the pipeline
```

The Evennia engine fork lives at `engine/evennia` as a **git submodule** (`origin` = `kakon77777-commits/evennia`, `upstream` = `evennia/evennia`) — not vendored/copied in, so upstream Evennia updates can still be pulled and diffed cleanly, but tracked inside this repo rather than scattered elsewhere in the workspace. After cloning this repo, run `git submodule update --init` to pull it, then `pip install -e ./engine/evennia` into your venv.

## Design documents

Read in this order — each supersedes/refines the previous on overlapping ground, but earlier ones still have detail the later ones don't:

1. **`01-mssp-scale-skill.md`** (Chinese only) — the general Mother-Set/Subset Paradigm (MSSP) for organizing large AI Agent skill systems. This project's own directory structure and the Skill's internal organization follow it.
2. **`02-mud-world-engineering-mssp.md`** (Chinese only) — MSSP applied specifically to MUD world engineering: FMS/SCL/SMS/TMS/DMS/Router mapped onto source-intake, world-understanding, World IR, compilation, persistence, agent governance, and testing.
3. **`03-compilable-world-architecture.md`** (Chinese only) — reframes MUD as just the first Runtime Adapter for a "Compilable World Platform," and adds detail the earlier two don't have: risk-graded world mutation levels (L0 narrative-only through L4 core/engine), event-sourced world state (Snapshot + Event Log, not snapshot-only), AI-player test metrics (room/quest/branch coverage, soft-lock detection), and copyright/provenance handling for user-uploaded source text. Supersedes #2 where they conflict.
4. **`04-authoring-layer-json-csv-manifest.md`** (English; [Chinese original](CompilableWorld前置資料層_JSON_CSV_Manifest與可維護世界資料架構_v0.1.md)) — defines an "Authoring Layer" of JSON/CSV/Manifest sitting between raw source text and the World IR, for data too large or tabular to hand-author as YAML (hundreds of characters, cities, economy parameters). Written after real friction hit this exact wall on the first large-scale World IR build. Pipeline: source → JSON/CSV Authoring Layer → normalized → validated → World IR → compiled world → runtime. Superseded by #6's World Seed Package on overlapping ground — read #6 first if choosing between them.
5. **`05-hierarchical-state-machine-mud.md`** (English; [Chinese original](超大型階層式有限狀態世界MUD_AI驅動複合行為與事件轉導架構_v0.1.md)) — a further-out architecture: natural-language player actions compiled by AI into a structured, validated "Action IR," executed by hierarchical (world/region/scene/entity/system) finite state machines, with event sourcing and separated narrative rendering. Aspirational/roadmap-stage, not yet implemented — the MVP loop in this repo is still classic verb-target commands.
6. **`06-novel-to-mud-world-adaptation.md`** (Chinese only) — the direct answer to real friction hit adapting a real novel (命運之欲) into World IR: re-reading a whole novel every time the game needs context is expensive, slow, and drifts. Splits AI use into two stages — offline world adaptation (novel → entity/timeline/geography extraction → a versioned, provenance-tracked **World Seed Package** of JSON/CSV/EML/Manifest) and in-game local generation (only load the current region/scene/actors' slice of the seed, never the whole novel). Defines three Canon tiers (Source Canon / Adapted Canon / Generated Expansion) so narrative fact, gameplay adaptation, and runtime invention never get conflated. Not yet implemented in `world_ir/`.

## Current status

See **[ROADMAP.md](ROADMAP.md)** for the honest state of the project: what's actually built vs. what each of the 6 whitepapers still only designs, and the suggested next priority. Short version: the core MVP loop (source → World IR → validate → compile → Evennia → AI test-player → report) is real and proven on a toy world; a real novel-scale world is in progress and already surfacing the next real gap (papers 04/06's Authoring Layer / World Seed Package, not yet implemented).

## Running it

The `mud-world-engineering` skill under `.claude/skills/` drives the pipeline end to end when invoked from Claude Code. See its `SKILL.md` for the stage-by-stage procedure, and `world_ir/README.md` (once built) for using the World IR tooling directly.
