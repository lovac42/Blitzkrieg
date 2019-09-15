# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2014 Patrice Neff
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


import re
from aqt import mw
from aqt.qt import *
from aqt.browser import Browser
from anki.hooks import addHook

from .sidebar21 import SidebarTreeWidget
from .tree import *


browserInstance=None

def replace_buildTree(self):
    global browserInstance
    browserInstance = self
    self.sidebarTree.browser = self
    self.sidebarTree.clear()
    root = self.sidebarTree
    self._stdTree(root)
    favTree(self,root)
    decksTree(self,root)
    modelTree(self,root)
    userTagTree(self,root)
    self.sidebarTree.setIndentation(15)


Browser.SidebarTreeWidget = SidebarTreeWidget
Browser.buildTree = replace_buildTree


def onRevertedState(stateName):
    tok=stateName.split()[-1]
    if tok in browserInstance.sidebarTree.node_state.keys():
        browserInstance.buildTree()
addHook("revertedState", onRevertedState)

