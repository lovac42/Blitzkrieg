# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


from aqt import mw
from aqt.qt import *
from anki.lang import _
from aqt.browser import Browser

from .sidebar21 import TagTreeWidget


def replace_addTags(browser, tags=None, label=None, *args, **kwargs):
    if label is None:
        label = _("Add Tags")
    d = QDialog(browser)
    d.setObjectName("DeleteTags")
    d.setWindowTitle(label)
    d.resize(360, 340)
    tagTree = TagTreeWidget(browser,d)
    tagTree.addTags()
    line = QLineEdit(d)
    layout = QVBoxLayout(d)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(QLabel(_("""Select tags and close dialog, green items will be added.""")))
    layout.addWidget(tagTree)
    layout.addWidget(QLabel(_("Add Extra Tags:")))
    layout.addWidget(line)
    d.exec_()

    txt=line.text()
    tags=[txt] if txt else []
    for k,v in tagTree.node.items():
        if v: tags.append(k)
    if tags:
        browser.mw.checkpoint(label)
        browser.model.beginReset()
        nids = browser.selectedNotes()
        browser.col.tags.bulkAdd(nids," ".join(tags))
        browser.model.endReset()
        browser.mw.requireReset()


def replace_deleteTags(browser, tags=None, label=None):
    if label is None:
        label = _("Delete Tags")
    d = QDialog(browser)
    d.setObjectName("DeleteTags")
    d.setWindowTitle(label)
    d.resize(360, 340)
    nids = browser.selectedNotes()
    tagTree = TagTreeWidget(browser,d)
    tagTree.removeTags(nids)
    layout = QVBoxLayout(d)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(QLabel(_("""Select tags and close dialog, red items will be deleted.""")))
    layout.addWidget(tagTree)
    d.exec_()

    tags=[]
    for k,v in tagTree.node.items():
        if v:
            tags.append(k+'::*')
            tags.append(k)
    if tags:
        browser.mw.checkpoint(label)
        browser.model.beginReset()
        browser.col.tags.bulkRem(nids," ".join(tags))
        browser.model.endReset()
        browser.mw.requireReset()


Browser.addTags = replace_addTags
Browser.deleteTags = replace_deleteTags
