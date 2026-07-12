"""Structural validation for a WorldIR: schema shape, map reachability, quest DAG.

This is the same set of checks the mud-world-engineering skill's
`scripts/validate_world_ir.py` runs, refactored into an importable function so
both the skill and this real pipeline (and the Evennia compiler, which refuses
to run on an unvalidated world) share one implementation instead of two
copies drifting apart.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .schema import WorldIR

REQUIRED_TOP_LEVEL = ["world", "regions", "provenance"]


@dataclass
class WorldReport:
    ok: bool
    world_id: str
    world_version: str
    regions: int
    rooms: int
    characters: int
    quests: int
    schema_errors: list[str] = field(default_factory=list)
    dangling_exits: list[dict] = field(default_factory=list)
    unreachable_rooms: list[str] = field(default_factory=list)
    reachability_rate: float = 1.0
    quest_dependency_errors: list[str] = field(default_factory=list)
    start_room_defined: bool | None = None

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "world_report": {
                "world_id": self.world_id,
                "world_version": self.world_version,
                "regions": self.regions,
                "rooms": self.rooms,
                "characters": self.characters,
                "quests": self.quests,
            },
            "validation": {
                "schema_errors": self.schema_errors,
                "dangling_exits": self.dangling_exits,
                "start_room_defined": self.start_room_defined,
                "unreachable_rooms": self.unreachable_rooms,
                "reachability_rate": round(self.reachability_rate, 3),
                "quest_dependency_errors": self.quest_dependency_errors,
            },
        }


def _build_graph(world: WorldIR):
    """Builds a strictly-directed graph from declared exits — one exit entry is one
    direction of travel. A two-way connection needs two exit entries (see
    world-ir-schema.md). This is deliberate: auto-adding a reverse edge would hide
    the exact authoring mistake reachability checking exists to catch (a room the
    author can walk into but never declared a way back out of).
    """
    graph: dict[str, list[str]] = {rid: [] for rid in world.rooms}
    dangling = []
    for ex in world.exits:
        if ex.from_room not in world.rooms:
            dangling.append({"exit_from": ex.from_room, "exit_to": ex.to_room, "problem": "from room not defined"})
            continue
        if ex.to_room not in world.rooms:
            dangling.append({"exit_from": ex.from_room, "exit_to": ex.to_room, "problem": "to room not defined"})
            continue
        graph[ex.from_room].append(ex.to_room)
    return graph, dangling


def _reachable_from(graph: dict[str, list[str]], start: str | None) -> set[str]:
    if not start or start not in graph:
        return set()
    seen = {start}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in graph.get(cur, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen


def _quest_dag_errors(world: WorldIR) -> list[str]:
    ids = set(world.quests.keys())
    errors = []
    for qid, quest in world.quests.items():
        for p in quest.prerequisites:
            if p not in ids:
                errors.append(f"quest '{qid}' has undefined prerequisite '{p}'")

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {qid: WHITE for qid in ids}

    def visit(qid, stack):
        if color.get(qid) == GRAY:
            errors.append(f"quest dependency cycle: {' -> '.join(stack + [qid])}")
            return
        if color.get(qid) == BLACK:
            return
        color[qid] = GRAY
        for p in world.quests[qid].prerequisites:
            if p in ids:
                visit(p, stack + [qid])
        color[qid] = BLACK

    for qid in ids:
        if color.get(qid) == WHITE:
            visit(qid, [])
    return errors


def validate_world(world: WorldIR) -> WorldReport:
    schema_errors = [f"missing required top-level key: {k}" for k in REQUIRED_TOP_LEVEL if k not in world.raw]

    graph, dangling = _build_graph(world)
    reachable = _reachable_from(graph, world.start_room)
    unreachable = sorted(world.room_ids - reachable)
    start_room_defined = (world.start_room in world.room_ids) if world.rooms else None

    quest_errors = _quest_dag_errors(world)

    total_rooms = len(world.rooms)
    reachability_rate = (len(reachable) / total_rooms) if total_rooms else 1.0

    ok = (
        not schema_errors
        and not dangling
        and not quest_errors
        and (start_room_defined is not False)
        and not unreachable
    )

    return WorldReport(
        ok=ok,
        world_id=world.id,
        world_version=world.version,
        regions=len({r.region_id for r in world.rooms.values()}),
        rooms=total_rooms,
        characters=len(world.characters),
        quests=len(world.quests),
        schema_errors=schema_errors,
        dangling_exits=dangling,
        unreachable_rooms=unreachable,
        reachability_rate=reachability_rate,
        quest_dependency_errors=quest_errors,
        start_room_defined=start_room_defined,
    )
