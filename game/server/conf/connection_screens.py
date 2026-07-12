# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings

from evennia import utils

CONNECTION_SCREEN = """
|b==============================================================|n
 歡迎來到 |g{}|n（版本 {}）！

 登入或註冊的格式都是：指令 + 帳號 + 密碼，中間用空格隔開。
 舉例：如果你的帳號是 neo、密碼是 abc123，就照樣輸入這幾個字：

      |w登入 neo abc123|n

 還沒建立帳號的話，把「登入」換成「註冊」，一樣照打：

      |w註冊 neo abc123|n

 （以上兩個指令英文也通：|wconnect|n 和 |wcreate|n）

 上面的「neo」「abc123」只是範例，請換成你自己的帳號和密碼，
 不要照抄，也不需要加任何符號。

 帳號或密碼中若含有空格，才需要用引號包住，例如：登入 "我的帳號" "我的密碼"
 輸入 |w說明|n 取得更多說明；輸入 |w看|n 可重新顯示這個畫面。
|b==============================================================|n""".format(
    settings.SERVERNAME, utils.get_evennia_version("short")
)
