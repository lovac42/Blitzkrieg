# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2014 Patrice Neff
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/HumptyDumpty


from aqt import mw
from aqt.qt import *
from aqt.browser import Browser

from .sidebar21 import SidebarTreeWidget
from .tree import *


def replace_buildTree(self):
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

