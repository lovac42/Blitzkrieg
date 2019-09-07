# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2014 Patrice Neff
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


import anki.find
from aqt import mw
from anki.lang import ngettext, _
from aqt.qt import *
from aqt.utils import getOnlyText, askUser, showWarning
from anki.errors import DeckRenameError


class SidebarTreeWidget(QTreeWidget):
    node_state = { # True for open, False for closed
        #Decks are handled per deck settings
        'group': {},
        'tag': {},
    }

    def __init__(self):
        QTreeWidget.__init__(self)
        self.browser = None
        self.dropItem = None
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.itemClicked.connect(self.onTreeClick)
        self.itemExpanded.connect(self.onTreeCollapse)
        self.itemCollapsed.connect(self.onTreeCollapse)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onTreeMenu)

    def keyPressEvent(self, evt):
        if evt.key() in (Qt.Key_Return, Qt.Key_Enter):
            item = self.currentItem()
            self.onTreeClick(item, 0)
        else:
            super().keyPressEvent(evt)

    def onTreeClick(self, item, col):
        if getattr(item, 'onclick', None):
            item.onclick()

    def onTreeCollapse(self, item):
        if getattr(item, 'oncollapse', None):
            item.oncollapse()
            return
        try:
            exp = item.isExpanded()
            self.node_state[item.type][item.fullname] = exp
        except: pass

    def dropMimeData(self, parent, row, data, action):
        # Dealing with qt serialized data is a headache,
        # so I'm just going to save a reference to the dropped item.
        # data.data('application/x-qabstractitemmodeldatalist')
        self.dropItem = parent
        return True

    def dropEvent(self, event):
        dragItem = event.source().currentItem()
        if dragItem.type not in ("tag","deck"):
            event.setDropAction(Qt.IgnoreAction)
            event.accept()
            return

        QAbstractItemView.dropEvent(self, event)
        if not self.dropItem or self.dropItem.type == dragItem.type:
            dragName = dragItem.fullname
            try:
                dropName = self.dropItem.fullname
            except AttributeError:
                dropName = None

            mw.checkpoint("Dragged "+dragItem.type)
            parse=mw.col.decks #used for parsing '::' separators

            if dragItem.type == "deck":
                dragDid = parse.byName(dragName)["id"]
                dropDid = parse.byName(dropName)["id"] if dropName else None
                try:
                    parse.renameForDragAndDrop(dragDid,dropDid)
                except DeckRenameError as e:
                    showWarning(e.description)
                mw.col.decks.get(dropDid)['browserCollapsed']=False

            elif dragItem.type == "tag":
                if dragName and not dropName:
                    if len(parse._path(dragName)) > 1:
                        self.moveTag(dragName, parse._basename(dragName))
                elif parse._canDragAndDrop(dragName, dropName):
                    assert dropName.strip()
                    self.moveTag(dragName, dropName + "::" + parse._basename(dragName))
                mw.col.tags.registerNotes()
                self.node_state['tag'][dropName]=True

        self.browser.buildTree()

    def moveTag(self, dragName, newName="", rename=True):
        "Rename or Delete tag"
        self.browser.editor.saveNow(self.hideEditor)
        f = anki.find.Finder(mw.col)
        # rename children
        for tag in mw.col.tags.all():
            if tag.startswith(dragName + "::"):
                ids = f.findNotes("tag:"+tag)
                if rename:
                    nn = tag.replace(dragName+"::", newName+"::", 1)
                    mw.col.tags.bulkAdd(ids,nn)
                    self.node_state['tag'][nn]=True
                mw.col.tags.bulkRem(ids,tag)
        # rename parent
        ids = f.findNotes("tag:"+dragName)
        if rename:
            mw.col.tags.bulkAdd(ids,newName)
            self.node_state['tag'][newName]=True
        mw.col.tags.bulkRem(ids,dragName)
        mw.col.tags.flush()


    def hideEditor(self):
        self.browser.editor.setNote(None)
        self.browser.singleCard=False

    def onTreeMenu(self, pos):
        item=self.currentItem()
        if not item or item.type in ("sys","group"):
            return
        m = QMenu(self)
        if item.type == "deck":
            act = m.addAction("Add")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Add",self._onTreeDeckAdd))
            act = m.addAction("Rename")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Rename",self._onTreeDeckRename))
            act = m.addAction("Delete")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Delete",self._onTreeDeckDelete))
        elif item.type == "tag":
            act = m.addAction("Rename Leaf")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Rename",self._onTreeTagRenameLeaf))
            act = m.addAction("Rename Branch")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Rename",self._onTreeTagRenameBranch))
            act = m.addAction("Delete")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Delete",self._onTreeTagDelete))
        elif item.type == "fav":
            act = m.addAction("Rename")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Rename",self._onTreeFavRename))
            act = m.addAction("Delete")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Delete",self._onTreeFavDelete))
        elif item.type == "model":
            act = m.addAction("Rename")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Rename",self._onTreeModelRename))
            act = m.addAction("Delete")
            act.triggered.connect(lambda:
                self._onTreeItemAction(item,"Delete",self._onTreeModelDelete))
        else:
            return
        m.popup(QCursor.pos())


    def _onTreeItemAction(self, item, action, callback):
        self.browser.editor.saveNow(self.hideEditor)
        mw.checkpoint(action+" "+item.type)
        callback(item)
        mw.col.setMod()
        self.browser.buildTree()

    def _onTreeDeckAdd(self, item):
        self.browser._lastSearchTxt=""
        did=mw.col.decks.byName(item.fullname)["id"]
        deck = getOnlyText(_("Name for deck:"),default=item.fullname+"::")
        if deck:
            mw.col.decks.id(deck)
        self.mw.reset(True)

    def _onTreeDeckDelete(self, item):
        self.browser._lastSearchTxt=""
        did=mw.col.decks.byName(item.fullname)["id"]
        mw.deckBrowser._delete(did)
        mw.reset(True)

    def _onTreeDeckRename(self, item):
        self.browser._lastSearchTxt=""
        did=mw.col.decks.byName(item.fullname)["id"]
        mw.deckBrowser._rename(did)
        mw.reset(True)

    def _onTreeTagRenameLeaf(self, item):
        oldNameArr = item.fullname.split("::")
        newName = getOnlyText(_("New tag name:"),default=oldNameArr[-1])
        newName = newName.replace('"', "")
        if not newName or newName == oldNameArr[-1]:
            return
        oldNameArr[-1] = newName
        newName = "::".join(oldNameArr)
        self.moveTag(item.fullname,newName)
        mw.col.tags.registerNotes()

    def _onTreeTagRenameBranch(self, item):
        newName = getOnlyText(_("New tag name:"),default=item.fullname)
        newName = newName.replace('"', "")
        if not newName or newName == item.fullname:
            return
        self.moveTag(item.fullname,newName)
        mw.col.tags.registerNotes()

    def _onTreeTagDelete(self, item):
        self.moveTag(item.fullname,rename=False)
        mw.col.tags.registerNotes()

    def _onTreeFavDelete(self, item):
        if askUser(_("Remove %s from your saved searches?") % item.fullname):
            del mw.col.conf['savedFilters'][item.fullname]

    def _onTreeFavRename(self, item):
        newName = getOnlyText(_("New search name:"),default=item.fullname)
        act=mw.col.conf['savedFilters'][item.fullname]
        mw.col.conf['savedFilters'][newName]=act
        del(mw.col.conf['savedFilters'][item.fullname])

    def _onTreeModelRename(self, item):
        self.browser.form.searchEdit.lineEdit().setText("")
        model = mw.col.models.byName(item.fullname)
        newName = getOnlyText(_("New model name:"),default=item.fullname)
        model['name'] = newName
        mw.col.models.save(model)
        mw.col.models.flush()
        self.browser.model.reset()

    def _onTreeModelDelete(self, item):
        self.browser.form.searchEdit.lineEdit().setText("")
        model = mw.col.models.byName(item.fullname)
        if mw.col.models.useCount(model):
            msg = _("Delete this note type and all its cards?")
        else:
            msg = _("Delete this unused note type?")
        if not askUser(msg, parent=self):
            return
        mw.col.models.rem(model)
        model = None
        mw.col.models.flush()
        self.browser.setupTable()
        self.browser.model.reset()

