# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


import aqt  #TODO: RM later, for 2.1.15
from aqt.qt import *
from anki.lang import _


class SidebarItem:
    def __init__(self, name, icon, onClick=None, onExpanded=None, expanded=False):
        self.name = name
        self.icon = icon
        self.onClick = onClick
        self.onExpanded = onExpanded
        self.expanded = expanded
        self.children = [] # List["SidebarItem"]
        self.parentItem = None # Optional[SidebarItem]

        self.tooltip = None
        self.foreground = None
        self.background = None

    def addChild(self, cb): # cb=SidebarItem
        self.children.append(cb)
        cb.parentItem = self

    def rowForChild(self, child): # -> Optional[int], child=SidebarItem
        try:
            return self.children.index(child)
        except ValueError:
            return None



class SidebarModel(QAbstractItemModel):
    nightmode = False #TODO: RM later, for 2.1.15

    def __init__(self, root): # root=SidebarItem
        QAbstractItemModel.__init__(self)
        self.root = root
        self.iconCache = {} # Dict[str, QIcon]

        try:
            from aqt.theme import theme_manager
            self._getIcon = theme_manager.icon_from_resources
        except ImportError:
            self._getIcon = self.iconFromRef


    # Qt API
    ######################################################################

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(self.root.children)
        else:
            item: SidebarItem = parent.internalPointer()
            return len(item.children)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem: SidebarItem
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()

        item = parentItem.children[row]
        return self.createIndex(row, column, item)

    def parent(self, child): # type: ignore
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()
        parentItem = childItem.parentItem

        if parentItem is None or parentItem == self.root:
            return QModelIndex()

        row = parentItem.rowForChild(childItem)
        if row is None:
            return QModelIndex()

        return self.createIndex(row, 0, parentItem)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        item: SidebarItem = index.internalPointer()
        if role == Qt.DisplayRole:
            return QVariant(item.name)
        elif role == Qt.DecorationRole:
            return QVariant(self._getIcon(item.icon))
        elif role == Qt.BackgroundRole:
            return QVariant(item.background)
        elif role == Qt.ForegroundRole:
            return QVariant(item.foreground)
        elif role == Qt.ToolTipRole:
            return QVariant(item.tooltip)
        else:
            return QVariant()

    # Helpers
    ######################################################################

    #DEPRECATION WARNING: This method has been deprecated in anki 2.1.20
    def iconFromRef(self, iconRef):
        icon = self.iconCache.get(iconRef)
        if icon is None:
            icon = QIcon(iconRef)

            if self.nightmode: #TODO: RM later, for 2.1.15
                pixmap = icon.pixmap(32, 32)
                image = pixmap.toImage()
                image.invertPixels()
                icon = aqt.QIcon(QPixmap.fromImage(image))

            self.iconCache[iconRef] = icon
        return icon

    def expandWhereNeccessary(self, tree):
        for row, child in enumerate(self.root.children):
            if child.expanded:
                idx = self.index(row, 0, QModelIndex())
                self._expandWhereNeccessary(idx, tree)

    def _expandWhereNeccessary(self, parent, tree):
        parentItem: SidebarItem
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()

        # nothing to do?
        if not parentItem.expanded:
            return

        # expand children
        for row, child in enumerate(parentItem.children):
            if not child.expanded:
                continue
            childIdx = self.index(row, 0, parent)
            self._expandWhereNeccessary(childIdx, tree)

        # then ourselves
        tree.setExpanded(parent, True)


    # Drag and drop support
    ######################################################################

    def supportedDropActions(self):
        return Qt.MoveAction | Qt.CopyAction

    def flags(self, index):
        f = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.isValid():
            f |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return f
