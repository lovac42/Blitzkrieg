# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


# This is used for debugging and other stuff, yada yada.
# Nothing to see here, just move along...

from aqt import mw
from aqt.qt import *
from anki.lang import _
from anki.hooks import addHook
from aqt.browser import Browser
from aqt.tagedit import TagEdit

from .sidebar21 import TagTreeWidget


def replace_addTags(browser, tags=None, label=None, *args, **kwargs):
    nids = browser.selectedNotes()
    if not nids:
        showInfo("No card selected")
        return
    if label is None:
        label = _("Add Tags")
    if not tags:
        d = QDialog(browser)
        d.setObjectName("DeleteTags")
        d.setWindowTitle(label)
        d.resize(360, 340)
        tagTree = TagTreeWidget(browser,d)
        tagTree.addTags(nids)
        line = TagEdit(d)
        line.setCol(browser.col)
        layout = QVBoxLayout(d)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(_("""\
Select tags and close dialog: \
Yellow is for existing tags. \
Green items will be added.""")))
        layout.addWidget(tagTree)
        layout.addWidget(QLabel(_("Add Extra Tags:")))
        layout.addWidget(line)
        d.exec_()

        txt=line.text()
        tags=[txt] if txt else []
        for k,v in tagTree.node.items():
            if v: tags.append(k)
        tags=" ".join(tags)

    if tags:
        browser.mw.checkpoint(label)
        browser.model.beginReset()
        browser.col.tags.bulkAdd(nids,tags)
        browser.model.endReset()
        browser.mw.requireReset()


def replace_deleteTags(browser, tags=None, label=None):
    nids = browser.selectedNotes()
    if not nids:
        showInfo("No card selected")
        return
    if label is None:
        label = _("Delete Tags")
    if not tags:
        d = QDialog(browser)
        d.setObjectName("DeleteTags")
        d.setWindowTitle(label)
        d.resize(360, 340)
        tagTree = TagTreeWidget(browser,d)
        tagTree.removeTags(nids)
        layout = QVBoxLayout(d)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(_("""\
Select tags and close dialog. \
Red items will be deleted.""")))
        layout.addWidget(tagTree)
        d.exec_()

        tags=[]
        for k,v in tagTree.node.items():
            if v:
                # tags.append(k+'::*') #inc subtags?
                tags.append(k)
        tags=" ".join(tags)

    if tags:
        browser.mw.checkpoint(label)
        browser.model.beginReset()
        browser.col.tags.bulkRem(nids,tags)
        browser.col.tags.registerNotes()
        browser.model.endReset()
        browser.mw.requireReset()



def disabledDebugStuff():
    if mw.pm.profile.get('Blitzkrieg.VFP',False):
        Browser.addTags = replace_addTags
        Browser.deleteTags = replace_deleteTags
addHook('profileLoaded', disabledDebugStuff)
