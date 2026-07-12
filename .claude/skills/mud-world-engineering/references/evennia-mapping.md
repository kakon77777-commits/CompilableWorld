# World IR → Evennia mapping

The World IR compiles to Evennia through a real, deterministic Python compiler — `world_ir/compile_evennia.py` in the CompilableWorld project — not by having an agent hand-author batch-commands per world. This doc explains what that compiler does, why it's structured that way, and its known limitations, so you can read its output critically instead of trusting it blindly.

Its output format is an **Evennia batch-command file** (`.ev`): a plain-text script of in-game builder commands that Evennia's batch processor runs in order (`@batchcommand` in-game, or `evennia batchcommand <path>` from the shell). It's human-readable, diffable, and re-runnable — properties that matter more here than raw performance.

## Why a real compiler instead of LLM freehand generation

The founding whitepaper (`compilable-world-architecture.md`, §1) opens with exactly this failure mode: letting an AI directly generate game code is unpredictable, hard to track, and skips the "AI proposes, system validates" separation the whole architecture is built on. A validated World IR is reviewable YAML; a hand-authored `.ev` file is one more place for the same mistakes (a mistyped room id, a forgotten teleport) to sneak back in *after* validation already passed. So compilation is ordinary Python: same World IR in, same `.ev` out, every run.

## Batch-command semantics the compiler relies on

Verified against the actual command implementations in `D:\Ai\external-repos\evennia\evennia\commands\default\building.py` — not assumed from general MU* knowledge, because getting this wrong produces a script that silently builds exits and drops NPCs in the wrong room:

- `@dig <name>;<alias>` with no `=` clause creates a room with no exits and doesn't touch the caller's current location — safe to run for every room up front, in any order.
- `@open <exit> = <destination>` and `@create/drop <obj>` both act on **the caller's current location**, not on any room named in the command itself. There is no "from room" argument to `@open`.
- `@teleport` (alias `@tel`) moves the caller. So the compiler digs every room first, then for each room that needs an exit, character, or item, emits one `@tel <room>` followed by everything that belongs there — see the compiler module's own docstring for the exact phase breakdown.
- Rooms are dug as `<title>;<id>` (or just `<id>` if there's no title) so the World IR's stable `id` stays a searchable alias throughout the script regardless of the human-readable title — `@tel` and `@open ... = <dest>` always target the `id`, never the title.

If you're ever tempted to "simplify" this by using `@tunnel` (which digs and links in one step) — don't, unless the room graph is a strict tree. `@tunnel` assumes the target room doesn't already exist; a world with a loop (room B reachable from both A and C) needs the room dug once and linked separately from each side, which is exactly what the phase-1/phase-2 split does generically.

## What the compiler flags instead of guessing

- **Typeclasses.** NPCs are created as `DefaultCharacter` — the compiler has no way to know whether the target project has a real NPC typeclass, so it emits a comment next to every `@create/drop` saying so rather than inventing a class path (e.g. `characters.NPC`) that might not exist.
- **Locks (`locked_until`).** An exit or item's `locked_until` (see `world-ir-schema.md`) has no direct Evennia primitive — it's a lockfunc call the compiler can only guess at (`quest.find_the_key.completed` → `quest_completed(find_the_key)`), always emitted as a comment, never as a live `@lock` command. A lock nobody can pass because the lockfunc doesn't exist is worse than no lock at all, because it reads as "working" until a player actually tries it.
- **Items carried by a character** (an item whose `location` is a character id, not a room id) aren't auto-placed — batch mode has no reliable way to "give" an item to an NPC without a live dbref to reference. The compiler lists these under "entities it could not place" for manual handling.
- **`role: player_start` characters** aren't instantiated at all. They represent where a *player* begins, not an NPC — Evennia's own account/character creation flow handles spawning a real player character at `world.start_room`. If the source material gives this character beliefs, items, or traits worth preserving, that belongs in the world report as "starting character concept," not as a generated object.

## Quests

Evennia has no built-in quest system — this is the one place "compiling" means "scaffolding a convention," not translating to an engine primitive. The compiler emits quest *data* as a plain Python dict (`quests.py`) for the target project's own quest-tracking code to consume. Quest *logic* (tracking progress, firing rewards, unlocking exits on completion) needs a scripted system already present in the target codebase — that's out of scope for this compiler and should be said plainly in the world report.

## What NOT to do

- Don't hand-author a `.ev` file yourself in place of running the compiler — that reintroduces exactly the unpredictability this design avoids. If the compiler's output is wrong, fix the compiler (or the World IR), don't patch around it by writing batch-commands freehand for this one world.
- Don't run the generated `.ev` against a live Evennia server as an automatic part of this skill. Producing the files is the deliverable; actually executing them against a real running game is a separate, higher-stakes action — confirm with the user first, since it mutates real game state.
- Don't skip straight to compilation before the World IR has passed validation (`scripts/validate_world_ir.py` or `world_ir.validate_world`) — an unreachable room or a quest cycle becomes a much harder-to-diagnose bug once it's live Evennia objects instead of a YAML file. The compiler itself refuses to run on an unvalidated world for this reason.
