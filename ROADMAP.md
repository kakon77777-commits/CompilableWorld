# CompilableWorld-Evennia-Prototype — Status & Roadmap

**2026-07-13: this repo is now the prototype/reference implementation, not the main line of development.** Paper 07 (`docs/whitepapers/07-evennia-to-mssp-runtime.md`) is Neo's own decision to pivot to a self-built MSSP Modular World Runtime, with Evennia demoted to reference implementation / compatibility adapter. The successor project lives in a new, separate folder (not yet linked here — check with Neo for its location before assuming this repo is where new Runtime work happens). Everything below describes this repo's own history and is still accurate for what it covers; it's just no longer where the canonical engine work continues.

Seven design documents now exist (`docs/whitepapers/`), covering a wide arc from general methodology to aspirational natural-language gameplay to the pivot away from this repo's own engine choice. This file exists so nobody — including a future session — has to reread all seven to answer "what's actually real right now, and where does it live." Updated 2026-07-13.

## What's actually built and working

- **`world_ir/`** — a real Python package: `schema.py` (World IR data model), `validate.py` (schema/reachability/quest-DAG checks), `compile_evennia.py` (deterministic World IR → Evennia batch-command compiler), and now **`seed.py`/`seed_validate.py`** (World Seed Package loading + structural validation — manifest-driven, generic across any JSON/CSV tables, not hardcoded to specific worldbuilding concepts; see `world_ir/SEED_FORMAT.md`). A World Seed is Canon-tier data (papers 04/06), deliberately kept separate from World IR (MUD-ready, gameplay-adapted data) — turning a validated Seed into a World IR is still a Stage-2 judgment call (linear plot → quest graph, ability prose → rule numbers), not yet automated, and shouldn't be without real design input on how a given setting's Canon becomes gameplay.
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
| 04 — Authoring Layer (JSON/CSV/Manifest) | A JSON/CSV/Manifest layer between raw source and World IR, for data too large for hand-authored YAML | **Implemented as part of 06's Seed loader** (see below) — the two papers proposed near-identical mechanisms; building one covered both. |
| 05 — Hierarchical State-Machine MUD | Natural-language player actions → AI-compiled Action IR → hierarchical FSMs → event sourcing | **Not implemented, aspirational.** The MVP is still classic verb-target commands (get/drop/look/etc.). No near-term work planned here. |
| 06 — Novel-to-MUD World Adaptation | Two-stage AI (offline novel→World Seed Package adaptation, vs. in-game local generation), Canon tiers (Source/Adapted/Generated), entity resolution, timeline reconstruction | **Structural loading + validation implemented** (`world_ir/seed.py`, `seed_validate.py`, manifest format in `world_ir/SEED_FORMAT.md`) and **validated read-only against the real `mingyun_zhiyu` data** (2026-07-13) — see findings below. **Not yet implemented**: entity resolution/alias merging, timeline reconstruction, and the gameplay-adaptation step (Seed → World IR) — those still need real design judgment on how this specific setting's Canon becomes a MUD, not just structural plumbing. |
| 07 — Evennia → MSSP Runtime | Demote Evennia to reference/prototype/adapter; self-build a World Kernel + MSSP mechanism modules + UI-decoupled Runtime | **This is the paper that ended this repo's role as the main project** (2026-07-13). Not implemented here and not meant to be — it's built in the successor project. This repo's `world_ir/` (Seed loader, World IR schema/validator/compiler) is a plausible reference/input for that Runtime's `compiler/` layer, and the Evennia integration is a plausible `adapters/evennia/` target per paper 07 ch.11.3 — but that's the new project's call, not decided here. |

## Real findings from validating `mingyun_zhiyu` (2026-07-13, read-only — nothing written to that folder)

Built a scratch manifest (kept outside the repo, in the session's scratchpad) pointing at the real `worlds/mingyun_zhiyu/data/*` files and ran it through the new validator. Loaded counts matched the data's own `README.md` exactly (48 characters, 16 cities, 18 factions, 15 axioms, etc. — good cross-check that parsing is correct). Two genuine, non-trivial findings surfaced:

1. **`species_coefficients.csv`'s `species` column has 3 values that don't resolve against `species.csv`'s ids** — one of them, `angel(天使)`, is the *exact same conflict* `gaps.json.cross_document_conflicts_found` already flags by hand (doc3's coefficient table includes angels; doc1 never lists them as a real species). Independent confirmation the generic reference-check catches real cross-document inconsistencies, not just structural noise.
2. **`characters.csv`'s `faction` column holds descriptive text, not clean ids** (e.g. `"議和派(領袖)"`, `"天穹之翼(已解散)"`) — it doesn't match `factions.csv`'s id scheme (e.g. `yihe_pai`). Not necessarily a bug — may be intentional prose annotation rather than a strict foreign key — but worth Neo's eyes if characters↔factions is ever meant to be a real queryable link.

## The actual gap, stated plainly

`world_ir/schema.py` (the MUD-ready World IR) only parses a single flat YAML file — that half of the gap is unchanged. What's now closed: `world_ir/seed.py` reads a Canon-tier World Seed (manifest + JSON/CSV tables) and validates it structurally. What's still open: turning a validated Seed into a compilable World IR (paper 06 ch.9's "gameplay adaptation operator" — linear plot → quest graph, ability prose → rule numbers, geography → rooms) is real design work, not yet started, and probably shouldn't be automated blindly — it's where Neo's actual creative judgment about `mingyun_zhiyu` belongs.

## Suggested priority order — superseded by the paper-07 pivot

The order below was this repo's own plan before paper 07. Kept for the historical record; **priority decisions now belong to the successor Runtime project**, not this repo. If picking up this repo's world_ir work as an input to that project, gameplay adaptation (Seed → World IR) is still the most-immediately-useful unfinished piece.

1. ~~Gameplay adaptation (Seed → World IR)~~ — still not built; still needs Neo's input on which slice of a 48-character, 16-city setting becomes a first playable region.
2. ~~Patch/event-sourcing~~ (paper 03's unbuilt half) — now paper 07's Event Bus / Transition Engine territory instead.
3. ~~Action IR / hierarchical state machines~~ (paper 05) — now paper 07's Action Runtime / Kernel territory instead.

This file should get updated whenever a paper moves from "designed" to "implemented," or when priorities change — it's meant to stay short and honest, not to become another whitepaper.
