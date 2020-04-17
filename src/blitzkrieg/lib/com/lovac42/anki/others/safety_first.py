# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import anki
from aqt import mw
from anki.hooks import addHook, runHook

from ..version import POINT_VERSION
from ......const import (
    ADDON_PATH, ADDON_NAME,
    TARGET_STABLE_VERSION
)
try:
    from ...config.safety_first import AUTHOR_HOOK, AUTHOR_MESSAGE
except ImportError:
    AUTHOR_HOOK = "BabyOnBoard"
    AUTHOR_MESSAGE = "%s"


def ankiVersionCompatibilityChecker(addon_name, stable_version):
    try:
        import os
        import time

        meta = mw.addonManager.addonMeta(ADDON_PATH)
        mod = meta.get("mod", 0)
        warn_mod = meta.get("warn_time", -1)
        warn_ver = meta.get("warn_pt_ver", stable_version)

        if warn_mod < mod or warn_ver < POINT_VERSION:
            if not mod:
                mod = int(time.time())
                meta["mod"] = mod
            meta["warn_time"] = mod
            meta["warn_pt_ver"] = POINT_VERSION
            mw.addonManager.writeAddonMeta(ADDON_PATH, meta)

            runHook(AUTHOR_HOOK, addon_name, stable_version)
    except:
        print("Can not print version compatibility warning due to an error.")



_timer = None
_to_warn = {}


def tryToWarn(addon_name, stable_version):
    global _timer, _to_warn
    try:
        if _timer:
            _timer.stop()
        _to_warn[addon_name] = stable_version
        _timer = mw.progress.timer(3000,warn,False)
    except: pass


def warn():
    addons = message = ""
    try:
        from aqt.utils import showWarning
        from ...config.safety_first import getMessageFromAuthor

        for k,v in _to_warn.items():
            addons += "%s was last tested to work on Anki v2.1.%d.\n"%(k,v)

        try:
            from anki.lang import currentLang
            message = getMessageFromAuthor(currentLang) % addons
        except:
            message = AUTHOR_MESSAGE % addons

        showWarning(
            text=message,
            parent=mw,
            title="Version Warnings"
        )
    except:
        print(message)


def onProfileLoaded():
    try:
        if AUTHOR_HOOK not in anki.hooks._hooks:
            addHook(AUTHOR_HOOK, tryToWarn)

        ankiVersionCompatibilityChecker(
            ADDON_NAME, TARGET_STABLE_VERSION)
    except: pass


if TARGET_STABLE_VERSION < POINT_VERSION:
    addHook('profileLoaded', onProfileLoaded)
