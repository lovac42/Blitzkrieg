# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# Copyright 2014 Patrice Neff
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


import re
from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
from aqt.browser import Browser
from anki.lang import _

from .sidebar21 import SidebarTreeView
from .tree import *
from .alt import *


try: #was fixed on 2.1.17beta3
    from aqt.browser import SidebarItem, SidebarModel
    from .patch_sidebar import SidebarItem as SBI, SidebarModel as SBM
    SidebarItem.__init__=SBI.__init__
    SidebarModel.__init__=SBM.__init__
    SidebarModel.data=SBM.data
    SidebarModel.flags=SBM.flags
    SidebarModel.supportedDropActions=SBM.supportedDropActions

except: #SHOULD_PATCH
    from .patch_sidebar import SidebarItem, SidebarModel
    from .patch_old_anki import *
    Browser.maybeRefreshSidebar = bc_maybeRefreshSidebar
    Browser.setupSidebar = bc_setupSidebar
    Browser.onSidebarVisChanged = bc_onSidebarVisChanged
    # print("patched browser code for addon:Blitzkrieg")



browserInstance=None

def replace_buildTree(self):
    global browserInstance
    browserInstance = self
    self.sidebarTree.browser = self

    root = SidebarItem("", "")

    try: #addons compatibility
        self._stdTree(root) #2.1.17++
    except TypeError:
        stdTree(self,root) #2.1.16--

    favTree(self,root)
    decksTree(self,root)
    modelTree(self,root)
    userTagTree(self,root)
    return root



Browser.SidebarTreeView = SidebarTreeView
Browser.buildTree = replace_buildTree


def onProfileLoaded():
    if browserInstance:
        browserInstance.sidebarTree.clear()
addHook('profileLoaded', onProfileLoaded)



def onRevertedState(stateName):
    tok=stateName.split()[-1]
    if tok=='deck' or \
    tok in browserInstance.sidebarTree.node_state.keys():
        browserInstance.sidebarTree.refresh()

addHook("revertedState", onRevertedState)

