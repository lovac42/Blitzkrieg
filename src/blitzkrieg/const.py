# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


import anki

try:
    POINT_VERSION = anki.utils.pointVersion()
except AttributeError:
    POINT_VERSION = int(anki.version.split('.')[-1])
