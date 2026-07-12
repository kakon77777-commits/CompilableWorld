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
    """Bilingual output, not just aliases — inventory is checked constantly,
    and its two possible messages are short, static, and self-contained
    (no Evennia $funcparser person-conjugation involved), so a clean
    override is safe here. Compare CmdGet/CmdDrop/CmdGive below, which are
    NOT overridden this deeply — their success messages go through
    `$You() $conj(...)` templates that render differently for the actor vs.
    onlookers, and reimplementing that correctly in Chinese (which doesn't
    conjugate by person at all — "你" vs. the actor's name — needs different
    logic, not just a different verb form) is real, separate follow-up work,
    not a quick text swap. Left as a known, described gap rather than done
    half-right.
    """

    aliases = default_cmds.CmdInventory.aliases + ["背包", "物品", "身上"]

    def func(self):
        items = self.caller.contents
        if not items:
            string = "你身上什麼都沒帶。 (You are not carrying anything.)"
        else:
            from evennia.utils import utils
            from evennia.utils.ansi import raw as raw_ansi

            table = self.styled_table(border="header")
            for key, desc, _ in utils.group_objects_by_key_and_desc(items, caller=self.caller):
                table.add_row(
                    f"|C{key}|n",
                    "{}|n".format(utils.crop(raw_ansi(desc or ""), width=50) or ""),
                )
            string = f"|w你攜帶著： (You are carrying:)\n{table}"
        self.msg(text=(string, {"type": "inventory"}))


class CmdGet(default_cmds.CmdGet):
    aliases = list(default_cmds.CmdGet.aliases) + ["拿", "撿", "撿起", "拿取"]


class CmdDrop(default_cmds.CmdDrop):
    aliases = ["丟下", "放下", "丟棄"]


class CmdGive(default_cmds.CmdGive):
    aliases = ["給", "給予", "交給"]


class CmdSay(default_cmds.CmdSay):
    aliases = default_cmds.CmdSay.aliases + ["說", "說道", "講"]


_HELP_CATEGORY_ZH = {
    "general": "一般",
    "building": "建造",
    "admin": "管理",
    "system": "系統",
    "comms": "通訊",
    "batchprocess": "批次處理",
}


def _zh_category(category):
    """'general' -> '一般 (General)'; unknown categories fall back to Title Case
    English rather than guessing a translation that might be wrong."""
    zh = _HELP_CATEGORY_ZH.get(category.lower())
    return f"{zh} ({category.title()})" if zh else category.title()


class CmdHelp(default_cmds.CmdHelp):
    """Bilingual help chrome: section headers ("Commands"/"Game & World"),
    category names, and the per-entry framing ("aliases", "Subtopics",
    "Other topic suggestions") — all safe, documented override points per
    the parent class's own docstrings ("This method can be overridden to
    customize the way a help entry is displayed"), not a workaround.

    Deliberately NOT covered: the actual help TEXT of each command (still
    each command's own English docstring — translating ~100 default
    commands' full usage text is real, separate content work, not a chrome
    tweak) and the couple of "no topic found" search-failure messages
    buried inside CmdHelp.func() itself, which is long and stateful enough
    that copying it whole just to translate two rarely-seen strings would
    trade a small win for a real maintenance liability (drifting from
    upstream's own help-search logic over time).
    """

    aliases = ["說明", "幫助", "指令"]

    def format_help_entry(
        self, topic="", help_text="", aliases=None, suggested=None, subtopics=None, click_topics=True
    ):
        from evennia.utils.utils import dedent, format_grid

        separator = "|C" + "-" * self.client_width() + "|n"
        start = f"{separator}\n"

        title = f"|C說明：|w{topic}|n (Help for {topic})" if topic else "|r找不到說明 (No help found)|n"

        if aliases:
            aliases_str = " |C（別名 aliases：{}|C）|n".format(
                "|C,|n ".join(f"|w{ali}|n" for ali in aliases)
            )
        else:
            aliases_str = ""

        help_text_str = "\n" + dedent(help_text.strip("\n")) if help_text else ""

        if subtopics:
            if click_topics:
                subtopics_list = [
                    f"|lchelp {topic}/{subtop}|lt|w{topic}/{subtop}|n|le" for subtop in subtopics
                ]
            else:
                subtopics_list = [f"|w{topic}/{subtop}|n" for subtop in subtopics]
            subtopics_str = "\n|C子主題 (Subtopics)：|n\n  {}".format(
                "\n  ".join(
                    format_grid(subtopics_list, width=self.client_width(), line_prefix=self.index_topic_clr)
                )
            )
        else:
            subtopics_str = ""

        if suggested:
            suggested_sorted = sorted(suggested)
            if click_topics:
                suggested_list = [f"|lchelp {sug}|lt|w{sug}|n|le" for sug in suggested_sorted]
            else:
                suggested_list = [f"|w{sug}|n" for sug in suggested_sorted]
            suggested_str = "\n|C其他建議主題 (Other topic suggestions)：|n\n{}".format(
                "\n  ".join(
                    format_grid(suggested_list, width=self.client_width(), line_prefix=self.index_topic_clr)
                )
            )
        else:
            suggested_str = ""

        end = start
        partorder = (start, title + aliases_str, help_text_str, subtopics_str, suggested_str, end)
        return "\n".join(part.rstrip() for part in partorder if part)

    def format_help_index(
        self, cmd_help_dict=None, db_help_dict=None, title_lone_category=False, click_topics=True
    ):
        from evennia.utils.utils import format_grid, pad
        from evennia.utils.ansi import ANSIString

        def _group_by_category(help_dict):
            grid = []
            verbatim_elements = []
            if len(help_dict) == 1 and not title_lone_category:
                for category in help_dict:
                    entries = sorted(set(help_dict.get(category, [])))
                    if click_topics:
                        entries = [f"|lchelp {entry}|lt{entry}|le" for entry in entries]
                    grid.extend(entries)
            else:
                for category in sorted(set(list(help_dict.keys()))):
                    category_str = f"-- {_zh_category(category)} "
                    grid.append(
                        ANSIString(
                            self.index_category_clr
                            + category_str
                            + "-" * max(0, width - len(category_str))
                            + self.index_topic_clr
                        )
                    )
                    verbatim_elements.append(len(grid) - 1)
                    entries = sorted(set(help_dict.get(category, [])))
                    if click_topics:
                        entries = [f"|lchelp {entry}|lt{entry}|le" for entry in entries]
                    grid.extend(entries)
            return grid, verbatim_elements

        help_index = ""
        width = self.client_width()
        grid = []
        verbatim_elements = []
        cmd_grid, db_grid = "", ""

        if any(cmd_help_dict.values()):
            sep1 = (
                self.index_type_separator_clr
                + pad("指令 (Commands)", width=width, fillchar="-")
                + self.index_topic_clr
            )
            grid, verbatim_elements = _group_by_category(cmd_help_dict)
            gridrows = format_grid(
                grid, width, sep="  ", verbatim_elements=verbatim_elements, line_prefix=self.index_topic_clr
            )
            cmd_grid = ANSIString("\n").join(gridrows) if gridrows else ""

        if any(db_help_dict.values()):
            sep2 = (
                self.index_type_separator_clr
                + pad("遊戲與世界 (Game & World)", width=width, fillchar="-")
                + self.index_topic_clr
            )
            grid, verbatim_elements = _group_by_category(db_help_dict)
            gridrows = format_grid(
                grid, width, sep="  ", verbatim_elements=verbatim_elements, line_prefix=self.index_topic_clr
            )
            db_grid = ANSIString("\n").join(gridrows) if gridrows else ""

        if cmd_grid and db_grid:
            help_index = f"{sep1}\n{cmd_grid}\n{sep2}\n{db_grid}"
        else:
            help_index = f"{cmd_grid}{db_grid}"

        return help_index


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
