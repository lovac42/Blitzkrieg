# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import re
from aqt import mw

_soundReg = r"\[sound:(.*?)\]"

def stripSounds(text):
    try:
        return mw.col.backend.strip_av_tags(text)
    except AttributeError:
        return re.sub(_soundReg, "", text)

