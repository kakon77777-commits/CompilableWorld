# World IR — minimal schema

World IR (World Intermediate Representation) is the single source of truth that everything else — validation, Evennia output, the AI test-player pass, the world report — reads from. Author it as one YAML document per world. Keep it engine-agnostic: nothing in here should mention Evennia, rooms-as-Python-objects, or any runtime detail. That separation is what lets the same World IR later target a different engine without redoing world design.

## Top-level shape

```yaml
world:
  id: black_tide_city          # snake_case, stable identifier, never renamed once referenced
  version: 0.1.0
  title: "Black Tide City"
  genre: dark-fantasy
  start_room: south_gate       # id of the room a new character spawns in — required, drives reachability checks

axioms:                        # things that are TRUE in this world, not merely believed by a character
  - id: magic_memory_cost
    statement: "Casting a memory spell costs the caster real memories."
    enforcement: hard          # hard = rules must respect this; soft = flavor/lore only

regions:
  - id: gray_crown
    title: "The Gray Crown District"
    rooms:
      - id: south_gate
        title: "South Gate"
        description: "..."
      - id: market
        title: "The Market"
        description: "..."
    exits:
      - from: south_gate
        to: market
        direction: north       # must have a return path unless one_way: true is explicit and intentional

characters:
  - id: old_maren
    title: "Old Maren"
    role: npc                  # npc | player_start | quest_giver
    location: market
    beliefs:                   # what THIS character thinks is true — may contradict axioms or other characters
      - "believes the king is still alive"

factions:
  - id: harbor_guild

items:
  - id: rusted_key
    location: south_gate       # room id, or character id if carried
    locked_until: null         # optional — same convention as exits.locked_until, e.g. "quest.find_the_key.completed"
                                # use this instead of narrating a lock in the description; a lock only the prose
                                # knows about doesn't validate and won't survive translation to Evennia output

abilities:
  - id: cast_memory_spell

resources:
  - id: memory

rules:
  - id: cast_memory_spell_cost
    when: "spell.school == memory"
    apply: "actor.memory -= 3"

quests:
  - id: find_the_key
    giver: old_maren
    prerequisites: []          # ids of quests that must be completed first — must form a DAG, no cycles
    steps:
      - "pick up rusted_key from south_gate"
      - "return rusted_key to old_maren"
    reward: "unlocks: gray_crown_vault"

events:
  - id: gate_collapse
    trigger: "quest.find_the_key.completed"

timeline: []
economy: {}

provenance:                     # required — this is what lets the world report say "N rooms came from the source text vs were AI-invented"
  source_type: novel            # freeform — novel, short-story, world-bible, notes, ai-generated, mixed, etc.
                                 # pick whatever honestly describes the input; don't force-fit one of a fixed list
  source_ref: "user-provided text, chapter 1-3"

version: 0.1.0
patch: null                     # set when this document represents a patch against a prior world_version, see below
```

## The axiom vs. belief rule

This is the one modeling mistake that quietly wrecks a world: promoting something a character *says* or *thinks* to a fact the rule engine or plot enforces. "Old Maren believes the king is dead" belongs under `characters[].beliefs`. Only put something under `axioms` if the world itself behaves as though it's true regardless of who's looking — spell costs, physics, what happens when a resource hits zero. When extracting from a novel, an unreliable narrator or a character with wrong information is a beliefs entry, not an axiom, even if it reads as stated fact in the prose. When unsure, default to belief — it's the reversible choice; promoting a belief to an axiom later is easy, walking back an axiom that broke half the rule set is not.

## Patches (world expansion after v0.1.0 exists)

Don't re-author the whole World IR to add content. Express the change as a patch:

```yaml
patch:
  id: northern_expansion_001
  base_world_version: 0.4.2
  target_world_version: 0.5.0
  reason: "Add the northern district requested by the user"
operations:
  - add_region: { id: northern_district, ... }
  - add_rooms: [...]
  - add_quests: [...]
```

Run the same validation pass (`scripts/validate_world_ir.py`) against the merged result before treating the patch as accepted. See SKILL.md step 6 for why a patch must never be self-approved by the same pass that authored it.
