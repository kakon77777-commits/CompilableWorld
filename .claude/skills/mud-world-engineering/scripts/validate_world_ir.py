#!/usr/bin/env python3
"""Validate a World IR YAML file: schema shape, map reachability, quest dependency graph.

Usage:
    python validate_world_ir.py <world-ir.yaml> [--start-room <room_id>]

Thin CLI wrapper around the project's real `world_ir` package (four directories
up from this file: mud-world-engineering/scripts -> skills -> .claude ->
CompilableWorld project root, where world_ir/ lives). This exists so the skill
can be invoked with a plain `python scripts/validate_world_ir.py` without the
caller needing to know the package layout; the actual validation logic lives in
exactly one place (world_ir/validate.py) so the skill and the rest of the
pipeline can't drift out of sync with each other over time.

Exits 0 with a JSON report on stdout if the world is structurally sound
(report.ok == true), exits 1 with the same JSON report if not.
"""
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from world_ir import load_world, validate_world
except ImportError as e:
    print(json.dumps({
        "ok": False,
        "fatal_error": (
            f"Could not import the world_ir package from {PROJECT_ROOT}. "
            f"Run this using the CompilableWorld project's venv "
            f"(D:\\Ai\\work together\\CompilableWorld\\.venv\\Scripts\\python.exe), "
            f"or run 'python -m world_ir validate <path>' directly from the project root. "
            f"Original error: {e}"
        ),
    }, indent=2))
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("world_ir_path")
    ap.add_argument("--start-room", default=None, help="Override world.start_room for reachability check")
    args = ap.parse_args()

    try:
        world = load_world(args.world_ir_path)
    except Exception as e:
        print(json.dumps({"ok": False, "fatal_error": f"Could not parse YAML: {e}"}, indent=2))
        sys.exit(1)

    if args.start_room:
        world.start_room = args.start_room

    report = validate_world(world)
    print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
    sys.exit(0 if report.ok else 1)


if __name__ == "__main__":
    main()
