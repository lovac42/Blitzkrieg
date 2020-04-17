# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from aqt import mw


def getConfigGetterMethod():
    try:
        return mw.col.get_config
    except AttributeError:
        return mw.col.conf.get

def getConfigSetterMethod():
    try:
        return mw.col.set_config
    except AttributeError:
        return _dictSetter

def _dictSetter(key, value):
    mw.col.conf[key] = value




def getFindCards():
    try:
        return mw.col.find_cards
    except AttributeError:
        import anki.find
        return anki.find.Finder(mw.col).findCards


def getFindNotes():
    try:
        return mw.col.find_notes
    except AttributeError:
        import anki.find
        return anki.find.Finder(mw.col).findNotes
