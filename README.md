# CompilableWorld

An AI-driven pipeline that turns novels, world-bibles, and worldbuilding notes into validated, playable text-based multiplayer worlds (MUDs) — and, longer-term, other runtime targets built from the same world data. MUD is the first Runtime Adapter, not the ceiling.

```
Source text → World Understanding → World IR → Validation → World Compiler → Runtime → AI test-player → Patch → Versioned Release
```

AI proposes; the system validates; version control protects. No single AI pass both authors unreviewed world content and marks it approved.

## Layout

```
CompilableWorld/
├── docs/whitepapers/       — the 5 design documents this project is built from, read in order
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

1. **`01-mssp-scale-skill.md`** — the general Mother-Set/Subset Paradigm (MSSP) for organizing large AI Agent skill systems. This project's own directory structure and the Skill's internal organization follow it.
2. **`02-mud-world-engineering-mssp.md`** — MSSP applied specifically to MUD world engineering: FMS/SCL/SMS/TMS/DMS/Router mapped onto source-intake, world-understanding, World IR, compilation, persistence, agent governance, and testing.
3. **`03-compilable-world-architecture.md`** — reframes MUD as just the first Runtime Adapter for a "Compilable World Platform," and adds detail the earlier two don't have: risk-graded world mutation levels (L0 narrative-only through L4 core/engine), event-sourced world state (Snapshot + Event Log, not snapshot-only), AI-player test metrics (room/quest/branch coverage, soft-lock detection), and copyright/provenance handling for user-uploaded source text. Supersedes #2 where they conflict.
4. **`04-authoring-layer-json-csv-manifest.md`** ([English](04-authoring-layer-json-csv-manifest.md)) — defines an "Authoring Layer" of JSON/CSV/Manifest sitting between raw source text and the World IR, for data too large or tabular to hand-author as YAML (hundreds of characters, cities, economy parameters). Written after real friction hit this exact wall on the first large-scale World IR build. Pipeline: source → JSON/CSV Authoring Layer → normalized → validated → World IR → compiled world → runtime.
5. **`05-hierarchical-state-machine-mud.md`** ([English](05-hierarchical-state-machine-mud.md)) — a further-out architecture: natural-language player actions compiled by AI into a structured, validated "Action IR," executed by hierarchical (world/region/scene/entity/system) finite state machines, with event sourcing and separated narrative rendering. Aspirational/roadmap-stage, not yet implemented — the MVP loop in this repo is still classic verb-target commands.

## Current status

Phase 0 / MVP-0.1 in progress: source → World IR → validation → Evennia output → single-player playable world, per `03-compilable-world-architecture.md` §14. Multiplayer, dynamic NPCs, AI GM, and further runtime targets are explicitly out of scope until this loop is proven on a real (not toy) source text.

## Running it

The `mud-world-engineering` skill under `.claude/skills/` drives the pipeline end to end when invoked from Claude Code. See its `SKILL.md` for the stage-by-stage procedure, and `world_ir/README.md` (once built) for using the World IR tooling directly.
