# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# Copyright 2014 Patrice Neff
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


from aqt.qt import *
from anki.lang import _
from aqt.browser import Browser #, SidebarItem
from anki.hooks import addHook

from .patch_sidebar import SidebarItem, SidebarModel
from .sidebar21 import SidebarTreeView


#compatible with new nightmode, for colorizing tags on 2.1.15
NM_CONFIG = None
def nightModeChanged(config):
    global NM_CONFIG
    NM_CONFIG = config
addHook("night_mode_config_loaded", nightModeChanged)



#backwards compatible
def bc_maybeRefreshSidebar(self):
    if self.sidebarDockWidget.isVisible():
        # add slight delay to allow browser window to appear first
        def deferredDisplay():
            root = self.buildTree()
            model = SidebarModel(root)
            try:
                model.nightmode = NM_CONFIG.state_on.value
            except: pass
            self.sidebarTree.setModel(model)
            model.expandWhereNeccessary(self.sidebarTree)
        self.mw.progress.timer(10, deferredDisplay, False)


#backwards compatible
def bc_setupSidebar(self):
    def onSidebarItemExpanded(idx):
        item = idx.internalPointer()
        #item.on

    dw = self.sidebarDockWidget = QDockWidget(_("Sidebar"), self)
    dw.setFeatures(QDockWidget.DockWidgetClosable)
    dw.setObjectName("Sidebar")
    dw.setAllowedAreas(Qt.LeftDockWidgetArea)
    self.sidebarTree = self.SidebarTreeView()
    self.sidebarTree.mw = self.mw
    self.sidebarTree.browser = self
    self.sidebarTree.setUniformRowHeights(True)
    self.sidebarTree.setHeaderHidden(True)
    self.sidebarTree.setIndentation(15)
    self.sidebarTree.expanded.connect(onSidebarItemExpanded) # type: ignore
    dw.setWidget(self.sidebarTree)
    p = QPalette()
    p.setColor(QPalette.Base, p.window().color())
    self.sidebarTree.setPalette(p)
    self.sidebarDockWidget.setFloating(False)
    self.sidebarDockWidget.visibilityChanged.connect(self.onSidebarVisChanged) # type: ignore
    self.sidebarDockWidget.setTitleBarWidget(QWidget())
    self.addDockWidget(Qt.LeftDockWidgetArea, dw)


#backwards compatible
def bc_onSidebarVisChanged(self, _visible):
    self.maybeRefreshSidebar()
