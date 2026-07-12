#!/usr/bin/env python3
"""Compile game/locale/*/LC_MESSAGES/django.po into django.mo.

Evennia's game-dir .gitignore excludes *.mo (compiled translation binaries,
same convention as *.pyc — regenerate, don't commit) so this file must be run
once after cloning the repo, and again any time a .po file is hand-edited.

Normally you'd use Django's `compilemessages` management command for this,
but that shells out to GNU gettext's `msgfmt`, which isn't installed on every
dev machine (wasn't on the one this locale was built on). `polib` compiles
.po -> .mo in pure Python, no external gettext toolchain needed — same
approach used to originally generate this locale (see its own README).

Usage (from the CompilableWorld project root, with its venv active):
    python game/locale/compile_locale.py
"""
from pathlib import Path

import polib

LOCALE_DIR = Path(__file__).parent

for po_path in LOCALE_DIR.glob("*/LC_MESSAGES/django.po"):
    mo_path = po_path.with_suffix(".mo")
    po = polib.pofile(str(po_path))
    po.save_as_mofile(str(mo_path))
    print(f"Compiled {po_path.relative_to(LOCALE_DIR.parent.parent)} -> {mo_path.name}")
