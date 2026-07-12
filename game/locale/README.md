# Locale

`zh_Hant/` — Traditional Chinese (Taiwan). Not hand-translated: machine-converted from Evennia's own bundled Simplified Chinese locale (`evennia/locale/zh/`) via [OpenCC](https://github.com/BYVoid/OpenCC)'s `s2twp` profile (Simplified → Traditional, Taiwan phrasing — e.g. "登录" becomes "登入", not just a naive character swap to "登錄"). Covers ~200 of Evennia's own system/login/account-flow messages; it does **not** cover every in-game command's feedback text, since Evennia's own translators didn't wrap every string in `gettext()` to begin with — command *keys* (what you type) are handled separately via Traditional-Chinese aliases in `game/commands/chinese_aliases.py`, not by this locale.

`.mo` files are compiled binaries and are gitignored (same convention as `.pyc` — regenerate, don't commit). After cloning this repo, or after hand-editing a `.po` file, run:

```
python game/locale/compile_locale.py
```

This needs `polib` (`pip install polib`) — deliberately not GNU gettext's `msgfmt`, which isn't guaranteed to be installed on every dev machine. Regenerating the *conversion* from Evennia's Simplified source (rather than hand-editing the `.po` directly) additionally needs `opencc-python-reimplemented` (`pip install opencc-python-reimplemented`); see the git history of this directory for the one-off conversion script if that's ever needed again — day-to-day, editing `zh_Hant/LC_MESSAGES/django.po` directly and recompiling is simpler than reconverting from scratch.
