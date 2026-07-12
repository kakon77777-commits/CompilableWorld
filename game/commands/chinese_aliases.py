"""Traditional-Chinese aliases for the most-used default commands.

Evennia's i18n (see server/conf/settings.py) translates the game's own
system/help/error MESSAGES into Traditional Chinese, but it does not — and
structurally cannot — translate command KEYS: `look`, `get`, `inventory` etc.
are hardcoded ASCII strings on Command classes, not gettext-wrapped, because
they're player-typed input, not displayed text. So a Chinese-first player
still has to type English verbs unless something adds Chinese aliases
alongside them.

That's what this module does: subclass each default command and extend its
`aliases` (never replace `key`, so `look` etc. keep working for anyone who
prefers them — this is additive, not a swap). These get merged into
CharacterCmdSet / AccountCmdSet in default_cmdsets.py, which overrides the
same-keyed default command with this version.

Movement (north/south/etc.) is NOT handled here — in Evennia, directions
aren't commands at all, they're the `key`/`aliases` of Exit *objects*, which
are data, not code. A World IR-compiled world can just use Chinese direction
words directly (e.g. `direction: 北`) and it works with zero changes here —
see world_ir/compile_evennia.py and docs/whitepapers's World IR schema.
"""

from evennia import default_cmds


class CmdLook(default_cmds.CmdLook):
    aliases = default_cmds.CmdLook.aliases + ["看", "看看", "查看"]


class CmdInventory(default_cmds.CmdInventory):
    aliases = default_cmds.CmdInventory.aliases + ["背包", "物品", "身上"]


class CmdGet(default_cmds.CmdGet):
    aliases = list(default_cmds.CmdGet.aliases) + ["拿", "撿", "撿起", "拿取"]


class CmdDrop(default_cmds.CmdDrop):
    aliases = ["丟下", "放下", "丟棄"]


class CmdGive(default_cmds.CmdGive):
    aliases = ["給", "給予", "交給"]


class CmdSay(default_cmds.CmdSay):
    aliases = default_cmds.CmdSay.aliases + ["說", "說道", "講"]


class CmdHelp(default_cmds.CmdHelp):
    aliases = ["說明", "幫助", "指令"]


class CmdQuit(default_cmds.CmdQuit):
    aliases = ["離開遊戲", "登出", "退出"]


class CmdWho(default_cmds.CmdWho):
    aliases = list(default_cmds.CmdWho.aliases) + ["誰在線", "在線名單"]


# --- Login-screen (pre-connection) aliases ---
# `connect <name> <password>` / `create <name> <password>` still need Latin
# usernames/passwords under the hood (Evennia account names), but the VERB
# itself — the part a Chinese-first user has to guess at every time — now
# has a Chinese option too.


class CmdUnconnectedConnect(default_cmds.CmdUnconnectedConnect):
    aliases = default_cmds.CmdUnconnectedConnect.aliases + ["登入", "連線"]


class CmdUnconnectedCreate(default_cmds.CmdUnconnectedCreate):
    aliases = default_cmds.CmdUnconnectedCreate.aliases + ["註冊", "建立帳號"]


class CmdUnconnectedQuit(default_cmds.CmdUnconnectedQuit):
    aliases = default_cmds.CmdUnconnectedQuit.aliases + ["離開"]


class CmdUnconnectedLook(default_cmds.CmdUnconnectedLook):
    aliases = default_cmds.CmdUnconnectedLook.aliases + ["看"]


class CmdUnconnectedHelp(default_cmds.CmdUnconnectedHelp):
    aliases = default_cmds.CmdUnconnectedHelp.aliases + ["說明", "幫助"]
