# CompilableWorld

An AI-driven pipeline that turns novels, world-bibles, and worldbuilding notes into validated, playable text-based multiplayer worlds (MUDs) — and, longer-term, other runtime targets built from the same world data. MUD is the first Runtime Adapter, not the ceiling.

```
Source text → World Understanding → World IR → Validation → World Compiler → Runtime → AI test-player → Patch → Versioned Release
```

AI proposes; the system validates; version control protects. No single AI pass both authors unreviewed world content and marks it approved.

## Layout

```
CompilableWorld/
├── docs/whitepapers/       — the 3 design documents this project is built from, read in order
├── world_ir/               — Python package: World IR schema, validator, provenance tracking
├── worlds/                 — generated World IR documents (one subfolder per world)
├── .claude/skills/mud-world-engineering/  — the Claude Code Skill that runs the pipeline
└── (engine lives separately — see below)
```

The Evennia engine fork is **not** vendored into this repo. It lives at `D:\Ai\external-repos\evennia` (git remote `origin` = `kakon77777-commits/evennia`, `upstream` = `evennia/evennia`), matching how other forked external tools are kept in this workspace (e.g. `tandem-browser`). This project installs it in editable mode rather than copying it in, so upstream Evennia updates can still be pulled and diffed cleanly.

## Design documents

Read in this order — each supersedes/refines the previous on overlapping ground, but earlier ones still have detail the later ones don't:

1. **`01-mssp-scale-skill.md`** — the general Mother-Set/Subset Paradigm (MSSP) for organizing large AI Agent skill systems. This project's own directory structure and the Skill's internal organization follow it.
2. **`02-mud-world-engineering-mssp.md`** — MSSP applied specifically to MUD world engineering: FMS/SCL/SMS/TMS/DMS/Router mapped onto source-intake, world-understanding, World IR, compilation, persistence, agent governance, and testing.
3. **`03-compilable-world-architecture.md`** — the most refined pass. Reframes MUD as just the first Runtime Adapter for a "Compilable World Platform," and adds detail the earlier two don't have: risk-graded world mutation levels (L0 narrative-only through L4 core/engine), event-sourced world state (Snapshot + Event Log, not snapshot-only), AI-player test metrics (room/quest/branch coverage, soft-lock detection), and copyright/provenance handling for user-uploaded source text. **Treat this one as authoritative where it conflicts with #2.**

## Current status

Phase 0 / MVP-0.1 in progress: source → World IR → validation → Evennia output → single-player playable world, per `03-compilable-world-architecture.md` §14. Multiplayer, dynamic NPCs, AI GM, and further runtime targets are explicitly out of scope until this loop is proven on a real (not toy) source text.

## Running it

The `mud-world-engineering` skill under `.claude/skills/` drives the pipeline end to end when invoked from Claude Code. See its `SKILL.md` for the stage-by-stage procedure, and `world_ir/README.md` (once built) for using the World IR tooling directly.
