# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


from typing import Callable, List, Dict, Optional
from aqt.qt import *
from anki.lang import _



class SidebarItem:
    def __init__(self,
                 name: str,
                 icon: str,
                 onClick: Callable[[], None] = None,
                 onExpanded: Callable[[bool], None] = None,
                 expanded: bool = False) -> None:
        self.name = name
        self.icon = icon
        self.onClick = onClick
        self.onExpanded = onExpanded
        self.expanded = expanded
        self.children: List["SidebarItem"] = []
        self.parentItem: Optional[SidebarItem] = None

        self.tooltip = None
        self.foreground = None
        self.background = None

    def addChild(self, cb: "SidebarItem") -> None:
        self.children.append(cb)
        cb.parentItem = self

    def rowForChild(self, child: "SidebarItem") -> Optional[int]:
        try:
            return self.children.index(child)
        except ValueError:
            return None



class SidebarModel(QAbstractItemModel):
    def __init__(self, root: SidebarItem) -> None:
        super().__init__()
        self.root = root
        self.iconCache: Dict[str, QIcon] = {}

    # Qt API
    ######################################################################

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return len(self.root.children)
        else:
            item: SidebarItem = parent.internalPointer()
            return len(item.children)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem: SidebarItem
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()

        item = parentItem.children[row]
        return self.createIndex(row, column, item)

    def parent(self, child: QModelIndex) -> QModelIndex: # type: ignore
        if not child.isValid():
            return QModelIndex()

        childItem: SidebarItem = child.internalPointer()
        parentItem = childItem.parentItem

        if parentItem is None or parentItem == self.root:
            return QModelIndex()

        row = parentItem.rowForChild(childItem)
        if row is None:
            return QModelIndex()

        return self.createIndex(row, 0, parentItem)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if not index.isValid():
            return QVariant()

        item: SidebarItem = index.internalPointer()
        if role == Qt.DisplayRole:
            return QVariant(item.name)
        elif role == Qt.DecorationRole:
            return QVariant(self.iconFromRef(item.icon))
        elif role == Qt.ToolTipRole:
            return QVariant(item.tooltip)
        elif role == Qt.ForegroundRole:
            return QVariant(item.foreground)
        elif role == Qt.BackgroundRole:
            return QVariant(item.background)
        else:
            return QVariant()

    # Helpers
    ######################################################################

    def iconFromRef(self, iconRef: str) -> QIcon:
        icon = self.iconCache.get(iconRef)
        if icon is None:
            icon = QIcon(iconRef)
            self.iconCache[iconRef] = icon
        return icon

    def expandWhereNeccessary(self, tree: QTreeView) -> None:
        for row, child in enumerate(self.root.children):
            if child.expanded:
                idx = self.index(row, 0, QModelIndex())
                self._expandWhereNeccessary(idx, tree)

    def _expandWhereNeccessary(self, parent: QModelIndex, tree: QTreeView) -> None:
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


    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.MoveAction | Qt.CopyAction

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        f = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.isValid():
            f |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return f
