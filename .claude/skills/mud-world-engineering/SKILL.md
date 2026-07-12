---
name: mud-world-engineering
description: Turns a novel, world-bible, or worldbuilding notes into a validated, playable MUD (text-based multiplayer world) — extracts world understanding from the source, produces a structured World IR, validates map reachability and quest-dependency integrity, generates Evennia-target world data, runs an AI test-player pass, and reports a finished world with region/room/quest counts and any unresolved issues. Use this whenever the user wants to turn a novel, short story, or setting into a MUD, text adventure, or Evennia world; asks to design, generate, expand, or patch a MUD world from a world-bible or lore notes; mentions "World IR", "world compiler", an AI Game Master world, or validating a MUD for unreachable rooms / broken quest chains; or hands over prose and asks "can you make this into a game." Also trigger for narrower asks that are clearly a step in this pipeline — e.g. "check if this MUD world's map is fully connected" or "does this quest chain have a dependency cycle" — even without a full end-to-end build request. Do not trigger for a single throwaway room or NPC description with no larger world context; just write it directly.
---

# MUD World Engineering

Turns source material into a playable text-based multiplayer world through one pipeline: **Source → World Understanding → World IR → Validation → Evennia output → AI test-player pass → World Report.** Each stage's output is the next stage's input, and the World IR (a YAML document, schema in `references/world-ir-schema.md`) is the single source of truth everything else reads from — never generate Evennia content or a world report from anything else.

This skill is deliberately scoped to that one loop. It does not attempt full multiplayer worlds, dynamic NPCs, AI Game Masters, or engines beyond Evennia — those are real follow-on projects, not something a skill file can respectably promise. If the user asks for one of those, say so and treat this pipeline as the foundation to build on, not something to stretch to cover it.

## Why the stages don't collapse

It's tempting to go straight from "here's my novel" to "here's your Evennia world" in one pass — the model can do that in principle. The reason not to: a World IR that's never separately validated hides its mistakes inside working-looking Evennia code, where an unreachable room or a quest that can never be completed is much harder to spot than it is in a 40-line YAML file. Each stage exists to catch a specific class of error before it compounds into the next stage. Skipping straight to output is the single most common way this kind of pipeline produces a "finished" world that quietly doesn't work.

## Stage 1 — Source intake

Read whatever the user hands over: novel text, a world-bible document, scattered notes, or "just make something up" with a genre/vibe. Note explicitly in your own working notes what's user-provided vs. what you're about to invent — this feeds `provenance` in the World IR and the report at the end, and it's the difference between "I extracted this from your text" and "I made this up to fill a gap," which the user needs to be able to tell apart.

If the source is large (a full novel), don't try to hold all of it in working memory at once — read it in chapters/sections and accumulate world-understanding notes as you go, the same way you'd take notes reading a book you intend to summarize accurately rather than from memory afterward.

## Stage 2 — World understanding

Extract, from the source (or invent, if generating from scratch): axioms, entities (characters, factions, items, abilities, resources), regions and rooms, rules, quests, events. Read `references/world-ir-schema.md` now if you haven't already — it defines exactly what each of these means in this pipeline and, critically, the **axiom vs. character-belief distinction**: something a character in the source believes or claims is not automatically true of the world. An unreliable narrator, a liar, or a character who's simply wrong is common in fiction and gets misread as world-fact constantly if you don't separate the two. When genuinely unsure whether something is a hard world-rule or one character's take on things, record it as a belief — that's the reversible choice.

Surface gaps and conflicts you find (a character in two places at once, a rule implied but never stated, a map that doesn't cohere) rather than silently resolving them — the user may want to fix the source, not have you paper over it.

## Stage 3 — Write the World IR

Author the World IR as YAML following `references/world-ir-schema.md`. Look at `templates/world-ir.example.yaml` for the shape. Every room needs a stable `id`; every exit needs a real destination; `world.start_room` must point at a room that actually exists — the validator in the next stage checks all of this mechanically, so don't hand-verify it, just write it.

If this is an expansion of an existing world rather than a new one, write a patch document (see the "Patches" section of the schema reference) instead of re-authoring the whole thing.

## Stage 4 — Validate

Run the bundled validator:

```
python scripts/validate_world_ir.py <path-to-world-ir.yaml>
```

It checks schema shape, dangling exits, map reachability from `start_room`, and whether the quest-prerequisite graph is a genuine DAG (no cycles, no references to undefined quests) — see the script's own docstring for exact output shape. It exits non-zero when `ok` is false. Do not proceed to Stage 5 until this passes. If it fails, that's Stage 3's job to fix, not something to route around — go back, fix the World IR, and re-run. Requires PyYAML (`pip install pyyaml` if the environment doesn't have it).

## Stage 5 — Evennia output

Once validation passes, compile with the real compiler — don't hand-author the Evennia batch-code yourself:

```
python -c "from world_ir import load_world; from world_ir.compile_evennia import compile_world; compile_world(load_world('<path-to-world-ir.yaml>'), '<out-dir>')"
```

This is deterministic Python (`world_ir/compile_evennia.py`), not LLM freehand generation — same World IR in, same `.ev` file out, every time, with its teleport/dig/open ordering verified against Evennia's actual command source (not assumed from memory; see the compiler's own module docstring). That determinism is the whole point: whitepaper 03 opens with exactly the failure mode of letting an AI freehand-generate game code — unpredictable, hard to track, hard to review. Your job is producing and revising the World IR; the compiler's job is turning validated World IR into Evennia artifacts without reinterpreting anything. Read `references/evennia-mapping.md` for what the compiler does and doesn't handle (typeclass assumptions, lockfunc guesses, items carried by characters) — it flags its own assumptions as comments in the generated `.ev` file rather than silently guessing.

This stage produces files for the user to review and merge into their own Evennia project. It does not start, connect to, or mutate a live Evennia server on its own — running the generated `.ev` against a live game is a separate, higher-stakes action the user (or an explicit later step) takes deliberately.

## Stage 6 — AI test-player pass

Before calling the world done, walk it the way a first-time player would: start at `world.start_room`, follow the room graph the World IR describes, and check that the quest(s) are actually completable in that order (pick up the item where the IR says it is, deliver it where the IR says to). This is a sanity read of the World IR content itself, not a live Evennia playtest — you're checking that what you authored in Stage 3 actually plays the way it reads, the same category of check as re-reading a recipe by literally following it step by step rather than skimming it. Note anything that reads as a soft-lock, a dead end, or a quest step that doesn't match what Stage 5 actually built.

## Stage 7 — World report

Report to the user using the validator's `world_report` JSON as the factual backbone (room/quest/character counts, reachability rate, any validation errors), plus:
- what came from their source material vs. what you invented to fill gaps (from Stage 1's provenance notes)
- what Stage 6's test-player pass found, if anything
- exactly which files were generated and where, and what the user needs to do to actually get them into a running Evennia game (this skill doesn't do that step itself)

A world that "looks done" with no validation numbers and no list of what's still rough is not a finished report — the whole point of this pipeline over a single freehand pass is that the user gets to see where the seams are.

## Hard rule: don't self-approve

If the user is iterating on an existing world (Stage 3 as a patch against a prior version) and asks you to also "approve" or "mark it production" as part of the same request, do the validation and report honestly, but don't fold review-and-approval into the same breath as authoring the content — say plainly that you generated and validated the patch, and that accepting it into whatever they're calling "production" is their call to make after reading the report, not something this pass decides for them. This mirrors why code review and code-writing are usually different passes: the author is the worst-positioned party to catch their own mistakes.

## Reference material

- `references/world-ir-schema.md` — the full World IR schema and the axiom/belief distinction, read before Stage 3
- `references/evennia-mapping.md` — World IR → Evennia batch-command mapping, read before Stage 5
- `references/mud-world-engineering-theory.md` — the whitepaper this pipeline is distilled from (roles/permissions for multi-agent operation, multi-engine targets beyond Evennia, versioning, later phases) — read if the user wants to go beyond this MVP loop
- `references/compilable-world-architecture.md` — a later, more refined whitepaper covering the same ground with more detail on risk-graded world mutation (L0-L4), event-sourced world state (snapshot + event log, not just snapshots), AI-player test metrics, and copyright/provenance handling for uploaded novels — prefer this one over `mud-world-engineering-theory.md` when the two disagree, it's the newer pass
- `references/mssp-scale-skill.md` — the general "Mother-Set and Subset Paradigm" methodology paper this skill's own structure follows; read if the user wants to apply the same organizing pattern to a different large skill system, not specifically MUD-related
