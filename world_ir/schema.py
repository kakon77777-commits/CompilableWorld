"""World IR data model and loader.

This is a thin structural wrapper around the YAML shape documented in
`.claude/skills/mud-world-engineering/references/world-ir-schema.md` — it does not
re-validate correctness (see `validate.py` for that). Its job is to give the rest
of the pipeline (the validator, the Evennia compiler) a consistent Python object
to walk instead of everyone re-parsing raw dicts their own way.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Room:
    id: str
    region_id: str
    title: str = ""
    description: str = ""


@dataclass
class Exit:
    from_room: str
    to_room: str
    direction: str
    locked_until: str | None = None
    one_way: bool = False


@dataclass
class Character:
    id: str
    title: str = ""
    role: str = ""  # npc | player_start | quest_giver
    location: str | None = None
    beliefs: list[str] = field(default_factory=list)


@dataclass
class Item:
    id: str
    location: str | None = None
    locked_until: str | None = None


@dataclass
class Quest:
    id: str
    giver: str | None = None
    prerequisites: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    reward: str | None = None


@dataclass
class WorldIR:
    """Structured view over a World IR document. `.raw` keeps the untouched dict
    for anything this wrapper doesn't (yet) model explicitly — axioms, rules,
    factions, abilities, resources, events, economy, provenance, etc. — so
    nothing is silently dropped just because a Python field wasn't written for it.
    """

    id: str
    version: str
    title: str
    start_room: str | None
    rooms: dict[str, Room]
    exits: list[Exit]
    characters: dict[str, Character]
    items: dict[str, Item]
    quests: dict[str, Quest]
    raw: dict

    @property
    def room_ids(self) -> set[str]:
        return set(self.rooms.keys())


def load_world(path: str | Path) -> WorldIR:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}

    world_meta = doc.get("world") or {}

    rooms: dict[str, Room] = {}
    exits: list[Exit] = []
    for region in doc.get("regions") or []:
        region_id = region.get("id", "<unknown-region>")
        for room in region.get("rooms") or []:
            rid = room.get("id")
            if not rid:
                continue
            rooms[rid] = Room(
                id=rid,
                region_id=region_id,
                title=room.get("title", ""),
                description=room.get("description", ""),
            )
        for exit_ in region.get("exits") or []:
            exits.append(Exit(
                from_room=exit_.get("from"),
                to_room=exit_.get("to"),
                direction=exit_.get("direction", "somewhere"),
                locked_until=exit_.get("locked_until"),
                one_way=bool(exit_.get("one_way", False)),
            ))

    characters: dict[str, Character] = {}
    for char in doc.get("characters") or []:
        cid = char.get("id")
        if not cid:
            continue
        characters[cid] = Character(
            id=cid,
            title=char.get("title", ""),
            role=char.get("role", "npc"),
            location=char.get("location"),
            beliefs=list(char.get("beliefs") or []),
        )

    items: dict[str, Item] = {}
    for item in doc.get("items") or []:
        iid = item.get("id")
        if not iid:
            continue
        items[iid] = Item(
            id=iid,
            location=item.get("location"),
            locked_until=item.get("locked_until"),
        )

    quests: dict[str, Quest] = {}
    for quest in doc.get("quests") or []:
        qid = quest.get("id")
        if not qid:
            continue
        quests[qid] = Quest(
            id=qid,
            giver=quest.get("giver"),
            prerequisites=list(quest.get("prerequisites") or []),
            steps=list(quest.get("steps") or []),
            reward=quest.get("reward"),
        )

    return WorldIR(
        id=world_meta.get("id", path.stem),
        version=world_meta.get("version", "0.0.0"),
        title=world_meta.get("title", world_meta.get("id", path.stem)),
        start_room=world_meta.get("start_room"),
        rooms=rooms,
        exits=exits,
        characters=characters,
        items=items,
        quests=quests,
        raw=doc,
    )
