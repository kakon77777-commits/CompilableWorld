#!/usr/bin/env python3
"""Validate a World Seed Package manifest — structural checks only (required
fields, id uniqueness, cross-table references). See world_ir/SEED_FORMAT.md
for the manifest format and docs/whitepapers/06-novel-to-mud-world-adaptation.md
for the design this implements.

Usage:
    python validate_seed.py <manifest.json>

A World Seed is NOT a World IR — see world_ir/seed.py's module docstring.
Don't feed the output of this straight into compile_evennia.py; a Seed still
needs gameplay adaptation (paper 06 ch.9) before it's MUD-playable.

Thin CLI wrapper around world_ir/seed.py + seed_validate.py, same pattern as
validate_world_ir.py in this folder — project root resolved the same way.
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from world_ir import load_seed, validate_seed
except ImportError as e:
    print(json.dumps({
        "ok": False,
        "fatal_error": (
            f"Could not import world_ir from {PROJECT_ROOT}. Run using the "
            f"CompilableWorld project's venv. Original error: {e}"
        ),
    }, indent=2))
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_seed.py <manifest.json>")
        sys.exit(1)

    try:
        seed = load_seed(sys.argv[1])
    except Exception as e:
        print(json.dumps({"ok": False, "fatal_error": f"Could not load seed: {e}"}, indent=2))
        sys.exit(1)

    report = validate_seed(seed)
    print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
    sys.exit(0 if report.ok else 1)


if __name__ == "__main__":
    main()
