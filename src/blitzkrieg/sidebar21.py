# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


import re
import aqt
import unicodedata
from aqt import mw
from anki.lang import ngettext, _
from aqt.qt import *
from aqt.utils import getOnlyText, askUser, showWarning, showInfo
from anki.utils import intTime, ids2str
from anki.errors import DeckRenameError, AnkiError
from anki.hooks import runHook

from .lib.com.lovac42.anki.backend import collection


class SidebarTreeView(QTreeView):
    node_state = { # True for open, False for closed
        #Decks are handled per deck settings
        'group': {}, 'tag': {}, 'fav': {}, 'pinDeck': {}, 'pinDyn': {},
        'model': {}, 'dyn': {}, 'pinTag': {}, 'pin': {},
        'deck': None, 'Deck': None,
    }

    finder = {} # saved gui options

    marked = {
        'group': {}, 'tag': {}, 'fav': {}, 'pinDeck': {}, 'pinDyn': {},
        'model': {}, 'dyn': {}, 'deck': {}, 'pinTag': {}, 'pin': {},
    }


    def __init__(self):
        super().__init__()
        self.expanded.connect(self.onExpansion)
        self.collapsed.connect(self.onCollapse)

        self.found = {}
        self.browser = None
        self.timer = None

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDropIndicatorShown(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onTreeMenu)
        self.setupContextMenuItems()

        mw.col.tags.registerNotes() # clear unused tags to prevent lockup

        self.getConf = collection.getConfigGetterMethod()
        self.setConf = collection.getConfigSetterMethod()
        self.findNotes = collection.getFindNotes()
        self.findCards = collection.getFindCards()


    def clear(self):
        self.finder.clear()
        for k in self.node_state:
            try:
                self.node_state[k].clear()
            except AttributeError:
                pass
        for k in self.marked:
            try:
                self.marked[k].clear()
            except AttributeError:
                pass


    def keyPressEvent(self, evt):
        if evt.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.onClickCurrent()
        elif evt.key() in (Qt.Key_Down, Qt.Key_Up):
            super().keyPressEvent(evt)
            self.onClickCurrent()
        else:
            super().keyPressEvent(evt)


    def onClickCurrent(self):
        idx = self.currentIndex()
        if idx.isValid():
            item = idx.internalPointer()
            if item.onClick:
                #filter out right mouse clicks
                self.timer=mw.progress.timer(
                    25, lambda:self._timedItemClick(item, True), False
                )

    def _timedItemClick(self, item, fromTimer=False):
        item.onClick()
        try:
            type=item.type
        except AttributeError:
            return

        if type=='tag':
            showConf = self.getConf('Blitzkrieg.showAllTags', True)
            if (showConf and fromTimer) or \
            (not showConf and not fromTimer):
                #show all subtags option
                el = self.browser.form.searchEdit.lineEdit()
                el.setText(el.text()+"*")

        elif type=='deck':
            #Auto update overview summary deck
            up = self.getConf('Blitzkrieg.updateOV', False)
            if up and item.type in ('deck','dyn','pinDeck','pinDyn') \
            and mw.state == 'overview':
                d = mw.col.decks.byName(item.fullname)
                mw.col.decks.select(d["id"])
                mw.moveToState("overview")


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.onClickCurrent()

    def onExpansion(self, idx):
        self._onExpansionChange(idx, True)

    def onCollapse(self, idx):
        self._onExpansionChange(idx, False)

    def _onExpansionChange(self, idx, expanded):
        item = idx.internalPointer()
        try:
            self.node_state[item.type][item.fullname] = expanded
        except TypeError:
            pass
        except (AttributeError,KeyError):
            return # addon: Customize Sidebar, favTree errors

        if item.expanded != expanded:
            item.expanded = expanded
            if item.onExpanded:
                item.onExpanded(expanded)
                for c in item.children:
                    if c.onExpanded:
                        c.onExpanded(c.expanded)

        #highlight parent items
        if not self.marked[item.type].get(item.fullname):
            if item.expanded and item.type in ('tag','deck','model') \
            and len(item.children) and '::' not in item.fullname:
                item.background = QBrush(QColor(0,0,10,10))
            else:
                item.background = None


    def setupContextMenuItems(self):
              # Type, Item Title, Action Name, Callback
              # type -1: separator
              # type 0: normal
              # type 1: non-folder path, actual item
              # type 2: type 0 and multi selected
              # type 3: type 1 and multi selected
        self.MENU_ITEMS = {
            "pin":((-1,),),
            "pinDyn":(
                (1,"Empty","Empty",self._onTreeDeckEmpty),
                (1,"Rebuild","Rebuild",self._onTreeDeckRebuild),
                (1,"Options","Options",self._onTreeDeckOptions),
                (1,"Export","Export",self._onTreeDeckExport),
                (-1,),
                (1,"Rename","Rename",self._onTreeFavRename),
                (3,"Unpin*",None,self._onTreePinDelete),
            ),
            "pinDeck":(
                (1,"Add Notes",None,self._onTreeDeckAddCard),
                (1,"Options","Options",self._onTreeDeckOptions),
                (1,"Export","Export",self._onTreeDeckExport),
                (-1,),
                (1,"Rename","Rename",self._onTreeFavRename),
                (3,"Unpin*",None,self._onTreePinDelete),
            ),
            "pinTag":(
                (1,"Show All/one",None,self._timedItemClick),
                (3,"Add Notes*",None,self._onTreeTagAddCard),
                (1,"Tag Selected","Tag",self._onTreeTag),
                (1,"Untag Selected","Untag",self._onTreeUnTag),
                (-1,),
                (1,"Rename","Rename",self._onTreeFavRename),
                (3,"Unpin*",None,self._onTreePinDelete),
            ),
            "tag":(
                (0,"Show All/one",None,self._timedItemClick),
                (2,"Add Notes*",None,self._onTreeTagAddCard),
                (0,"Rename Leaf","Rename",self._onTreeTagRenameLeaf),
                (0,"Rename Branch","Rename",self._onTreeTagRenameBranch),
                (0,"Tag Selected","Tag",self._onTreeTag),
                (0,"Untag Selected","Untag",self._onTreeUnTag),
                (2,"Delete*","Delete",self._onTreeTagDelete),
                (-1,),
                (0,"Convert to decks","Convert",self._onTreeTag2Deck),
            ),
            "deck":(
                (0,"Rename Leaf","Rename",self._onTreeDeckRenameLeaf),
                (0,"Rename Branch","Rename",self._onTreeDeckRename),
                (0,"Add Notes",None,self._onTreeDeckAddCard),
                (0,"Add Subdeck","Add",self._onTreeDeckAdd),
                (0,"Options","Options",self._onTreeDeckOptions),
                (0,"Export","Export",self._onTreeDeckExport),
                (0,"Delete","Delete",self._onTreeDeckDelete),
                (-1,),
                (0,"Convert to tags","Convert",self._onTreeDeck2Tag),
            ),
            "dyn":(
                (0,"Rename Leaf","Rename",self._onTreeDeckRenameLeaf),
                (0,"Rename Branch","Rename",self._onTreeDeckRename),
                (0,"Empty","Empty",self._onTreeDeckEmpty),
                (0,"Rebuild","Rebuild",self._onTreeDeckRebuild),
                (0,"Options","Options",self._onTreeDeckOptions),
                (0,"Export","Export",self._onTreeDeckExport),
                (0,"Delete","Delete",self._onTreeDeckDelete),
            ),
            "fav":(
                (1,"Rename","Rename",self._onTreeFavRename),
                (1,"Modify","Modify",self._onTreeFavModify),
                (3,"Delete*","Delete",self._onTreeFavDelete),
            ),
            "model":(
                (0,"Rename Leaf","Rename",self._onTreeModelRenameLeaf),
                (0,"Rename Branch","Rename",self._onTreeModelRenameBranch),
                (0,"Add Model","Add",self._onTreeModelAdd),
                (1,"Edit Fields","Edit",self.onTreeModelFields),
                (1,"LaTeX Options","Edit",self.onTreeModelOptions),
                (1,"Delete","Delete",self._onTreeModelDelete),
            ),
        }



    def dropEvent(self, event):
        super().dropEvent(event)

        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        dropItem = index.internalPointer()

        try: #quick patch for addon compatibility
            dropItem.type
        except AttributeError:
            dropItem.type=None

        if dropItem and isinstance(dropItem.type, str):
            if dropItem.type=='group':
                #clear item to allow dropping to groups
                dropItem = None
        else:
            return #not drop-able

        type = None
        dragItems = []
        for sel in event.source().selectedIndexes():
            item = sel.internalPointer()
            dgType = item.type
            if not isinstance(dgType, str):
                continue
            if dgType not in self.node_state:
                continue
            if not dropItem or \
            dropItem.type == dgType or \
            dropItem.type == dgType[:3]: #pin
                if not type:
                    if dgType in ("deck", "dyn"):
                        type = "deck"
                    elif dgType == "tag":
                        type = "tag"
                    elif dgType == "model":
                        type = "model"
                    elif dgType[:3] in ("fav","pin"):
                        type = "fav"
                    else:
                        continue
                elif type!=dgType:
                    #first item and subsequent items must match the same type
                    continue
                dragItems.append(item)

        if not type or not dragItems:
            return
        self.mw.progress.timer(10,
            lambda:self.dropEventHandler(type,dragItems,dropItem),
            False
        )

    def dropEventHandler(self, type, dragItems, dropItem):
        mw.checkpoint("Dragged %s"%type)
        self.browser._lastSearchTxt=""
        self.mw.progress.start(label=_("Processing...")) #doesn't always show up
        # prevent child elements being moved if selected
        dragItems = sorted(dragItems, key=lambda t: t.fullname)
        try:
            if type=="deck":
                self._deckDropEvent(dragItems, dropItem)
            elif type=="tag":
                self._tagDropEvent(dragItems, dropItem)
            elif type=="model":
                self._modelDropEvent(dragItems, dropItem)
            elif type=="fav":
                self._favDropEvent(dragItems, dropItem)
        finally:
            self.mw.progress.finish()
            mw.col.setMod()
            self.browser.maybeRefreshSidebar()
            if type=="deck":
                mw.reset()


    def _getItemNames(self, item, dropItem):
        try: #type fav or pin
            itemName = item.favname
            try:
                dropName = dropItem.favname
            except AttributeError:
                dropName = None #no parent
        except AttributeError:
            itemName = item.fullname
            try:
                dropName = dropItem.fullname
            except AttributeError:
                dropName = None #no parent
        if not dropName and item.type[:3] == "pin":
            dropName="Pinned"
        return itemName,dropName


    def _strDropEvent(self, dragItem, dropItem, type, callback):
        parse=mw.col.decks #used for parsing '::' separators
        dragName,dropName = self._getItemNames(dragItem, dropItem)
        if dragName and not dropName:
            if len(parse._path(dragName)) > 1:
                newName = parse._basename(dragName)
                callback(dragName, newName, dragItem, dropItem)
        elif parse._canDragAndDrop(dragName, dropName):
            assert dropName.strip()
            newName = dropName + "::" + parse._basename(dragName)
            callback(dragName, newName, dragItem, dropItem)
        self.node_state[type][dropName] = True


    def _deckDropEvent(self, dragItems, dropItem):
        parse = mw.col.decks #used for parsing '::' separators
        for item in dragItems:
            mw.progress.update(label=item.name)
            dropDid = None
            dragName,dropName = self._getItemNames(item, dropItem)
            dragDeck = parse.byName(dragName)
            if not dragDeck: #parent was moved first
                continue
            try:
                _,newName = dragName.rsplit('::',1)
            except ValueError:
                newName = None
            if dropName:
                dropDeck = parse.byName(dropName)
                dropDid = dropDeck["id"]
                newName = dropDeck["name"]+"::"+(newName or dragName)
            try:
                parse.renameForDragAndDrop(dragDeck["id"], dropDid)
            except DeckRenameError as e:
                showWarning(e.description)
                continue
            #deck type not used
            # self.node_state[item.type][dropName] = True
            mw.col.decks.get(dropDid or 1)['browserCollapsed'] = False
            if newName:
                self._swapHighlight(item.type,dragName,newName)
            #Adding HL here gets really annoying
            # self.highlight(item.type,dragDeck['name'])


    def _favDropEvent(self, dragItems, dropItem):
        for item in dragItems:
            mw.progress.update(label=item.name)
            self._strDropEvent(item,dropItem,item.type,self._moveFav)

    def _moveFav(self, dragName, newName="", dragItem=None, dropItem=None):
        try:
            type = dropItem.type or "fav"
        except AttributeError:
            type = "fav"
        savedFilters = self.getConf('savedFilters', {})
        for fav in list(savedFilters):
            act = savedFilters.get(fav)
            if fav.startswith(dragName + "::"):
                nn = fav.replace(dragName+"::", newName+"::", 1)
                savedFilters[nn] = act
                del(savedFilters[fav])
                self.node_state[type][nn] = True
                self._swapHighlight(type,dragName,newName)
            elif fav == dragName:
                savedFilters[newName] = act
                del(savedFilters[dragName])
                self.node_state[type][newName] = True
                self._swapHighlight(type,dragName,newName)
        self.setConf('savedFilters', savedFilters)

    def _modelDropEvent(self, dragItems, dropItem):
        if len(dragItems)>1:
            self.mw.progress._showWin() #never appears if not forced
        self.browser.editor.saveNow(self.hideEditor)
        for item in dragItems:
            mw.progress.update(label=item.name)
            self._strDropEvent(item,dropItem,item.type,self._moveModel)
        mw.col.models.flush()
        self.browser.model.reset()

    def moveModel(self, dragName, newName, dragItem):
        "Rename or Delete models"
        self.browser.editor.saveNow(self.hideEditor)
        self._moveModel(dragName,newName,dragItem)
        mw.col.models.flush()
        self.browser.model.reset()

    def _moveModel(self, dragName, newName="", dragItem=None, dropItem=None):
        "Rename or Delete models"
        model = mw.col.models.get(dragItem.mid)
        modelName=model['name']
        if modelName.startswith(dragName + "::"):
            model['name'] = modelName.replace(dragName+"::", newName+"::", 1)
        elif modelName == dragName:
            model['name'] = newName
        self.node_state['model'][newName] = True
        self._swapHighlight('model',dragName,newName)
        mw.col.models.save(model)

    def _tagDropEvent(self, dragItems, dropItem):
        self.browser.editor.saveNow(self.hideEditor)
        mw.col.tags.registerNotes() # clearn unused tags to prevent lockup
        for item in dragItems:
            mw.progress.update(label=item.name)
            self._strDropEvent(item,dropItem,item.type,self._moveTag)
        self._saveTags()
        mw.col.tags.registerNotes()

    def moveTag(self, dragName, newName):
        self.browser.editor.saveNow(self.hideEditor)
        mw.col.tags.registerNotes() # clearn unused tags to prevent lockup
        self._moveTag(dragName,newName)
        self._saveTags()
        mw.col.tags.registerNotes()

    def _moveTag(self, dragName, newName, dragItem=None, dropItem=None):
        "Rename tag"
        # rename children
        for tag in mw.col.tags.all():
            if tag.startswith(dragName + "::"):
                ids = self.findNotes('"tag:%s"'%tag)
                nn = tag.replace(dragName+"::", newName+"::", 1)
                mw.col.tags.bulkRem(ids,tag)
                mw.col.tags.bulkAdd(ids,nn)
                self.node_state['tag'][nn]=True
                self._swapHighlight('tag',tag,nn)
        # rename parent
        ids = self.findNotes('"tag:%s"'%dragName)
        mw.col.tags.bulkRem(ids,dragName)
        mw.col.tags.bulkAdd(ids,newName)
        self.node_state['tag'][newName] = True
        self._swapHighlight('tag',dragName,newName)


    def hideEditor(self):
        self.browser.editor.setNote(None)
        self.browser.singleCard=False


    def onTreeMenu(self, pos):
        try:
            #stop timer for, auto update overview summary deck, during right clicks
            self.timer.stop()
        except: pass

        index=self.indexAt(pos)
        if not index.isValid():
            return
        item=index.internalPointer()
        if not item:
            return

        try: #quick patch for addon compatibility
            item.type
        except AttributeError:
            item.type=None

        m = QMenu(self)
        if not isinstance(item.type, str) or item.type == "sys":
            # 2.1 does not patch _systemTagTree.
            # So I am using this to readjust item.type
            item.type = "sys"

        #TODO: Rewrite menu for each type + modifier keys
        elif mw.app.keyboardModifiers()==Qt.ShiftModifier:
            if item.type != "group":
                if item.type == "tag":
                    act = m.addAction("Create Filtered Tag*")
                    act.triggered.connect(lambda:self._onTreeCramTags(index))
                    m.addSeparator()
                #TODO: add support for custom study from deck list

                act = m.addAction("Mark/Unmark Item*")
                act.triggered.connect(lambda:self._onTreeMark(index))
                if item.type in ("deck","tag"):
                    act = m.addAction("Pin Item*")
                    act.triggered.connect(lambda:self._onTreePin(index))
                if item.type in ("pin","fav"):
                    ico = self.getConf('Blitzkrieg.icon_fav', True)
                    act = m.addAction("Show icon for paths")
                    act.setCheckable(True)
                    act.setChecked(ico)
                    act.triggered.connect(lambda:self._toggleIconOption(item))

            act = m.addAction("Refresh")
            act.triggered.connect(self.refresh)
            if item.type == "group":
                if item.fullname in ("tag","deck","model"):
                    sort = self.getConf('Blitzkrieg.sort_'+item.fullname, False)
                    act = m.addAction("Sort by A-a-B-b")
                    act.setCheckable(True)
                    act.setChecked(sort)
                    act.triggered.connect(lambda:self._toggleSortOption(item))
                if item.fullname in ("tag","model"):
                    ico = self.getConf('Blitzkrieg.icon_'+item.fullname, True)
                    act = m.addAction("Show icon for paths")
                    act.setCheckable(True)
                    act.setChecked(ico)
                    act.triggered.connect(lambda:self._toggleIconOption(item))
                if item.fullname == "deck":
                    up = self.getConf('Blitzkrieg.updateOV', False)
                    act = m.addAction("Auto Update Overview")
                    act.setCheckable(True)
                    act.setChecked(up)
                    act.triggered.connect(self._toggleMWUpdate)
                elif item.fullname == "tag":
                    sa = self.getConf('Blitzkrieg.showAllTags', True)
                    act = m.addAction("Auto Show Subtags")
                    act.setCheckable(True)
                    act.setChecked(sa)
                    act.triggered.connect(self._toggleShowSubtags)

            if len(item.children):
                m.addSeparator()
                act = m.addAction("Collapse All*")
                act.triggered.connect(lambda:self.expandAllChildren(index))
                act = m.addAction("Expand All*")
                act.triggered.connect(lambda:self.expandAllChildren(index,True))

        elif item.type == "group":
            if item.fullname == "tag":
                act = m.addAction("Refresh")
                act.triggered.connect(self.refresh)
            elif item.fullname == "deck":
                act = m.addAction("Add Deck")
                act.triggered.connect(self._onTreeDeckAdd)
                act = m.addAction("Empty All Filters")
                act.triggered.connect(self.onEmptyAll)
                act = m.addAction("Rebuild All Filters")
                act.triggered.connect(self.onRebuildAll)
            elif item.fullname == "model":
                act = m.addAction("Manage Model")
                act.triggered.connect(self.onManageModel)

            m.addSeparator()
            act = m.addAction("Find...")
            act.triggered.connect(lambda:self.findRecursive(index))
            act = m.addAction("Collapse All*")
            act.triggered.connect(lambda:self.expandAllChildren(index))
            act = m.addAction("Expand All*")
            act.triggered.connect(lambda:self.expandAllChildren(index,True))

        elif len(self.selectedIndexes())>1:
            #Multi sel items
            for itm in self.MENU_ITEMS[item.type]:
                if itm[0] < 0:
                    m.addSeparator()
                elif itm[0]==2 or (itm[0]==3 and self.hasValue(item)):
                    act = m.addAction(itm[1])
                    act.triggered.connect(
                        lambda b, item=item, itm=itm:
                            self._onTreeItemAction(item,itm[2],itm[3])
                    )
        else:
            #Single selected itms
            for itm in self.MENU_ITEMS[item.type]:
                if itm[0] < 0:
                    m.addSeparator()
                elif itm[0] in (0,2) or self.hasValue(item):
                    act = m.addAction(itm[1])
                    act.triggered.connect(
                        lambda b, item=item, itm=itm:
                            self._onTreeItemAction(item,itm[2],itm[3])
                    )

        runHook("Blitzkrieg.treeMenu", self, item, m)
        if not m.isEmpty():
            m.popup(QCursor.pos())



    def _onTreeItemAction(self, item, action, callback):
        self.browser.editor.saveNow(self.hideEditor)
        if action:
            mw.checkpoint(action+" "+item.type)
        try:
            callback(item)
        finally:
            mw.col.setMod()
            self.browser.onReset()
            self.browser.maybeRefreshSidebar()


    def _onTreeDeckEmpty(self, item):
        self.browser._lastSearchTxt=""
        sel = mw.col.decks.byName(item.fullname)
        mw.col.sched.emptyDyn(sel['id'])
        mw.reset()

    def _onTreeDeckRebuild(self, item):
        sel = mw.col.decks.byName(item.fullname)
        mw.col.sched.rebuildDyn(sel['id'])
        mw.reset()

    def _onTreeDeckOptions(self, item):
        deck = mw.col.decks.byName(item.fullname)
        try:
            if deck['dyn']:
                import aqt.dyndeckconf
                aqt.dyndeckconf.DeckConf(self.mw, deck=deck, parent=self.browser)
            else:
                import aqt.deckconf
                aqt.deckconf.DeckConf(self.mw, deck, self.browser)
        except TypeError:
            mw.onDeckConf(deck)
        mw.reset(True)

    def _onTreeDeckExport(self, item):
        deck = mw.col.decks.byName(item.fullname)
        try:
            import aqt.exporting
            aqt.exporting.ExportDialog(self.mw, deck['id'], self.browser)
        except TypeError:
            mw.onExport(did=deck['id'])
        mw.reset(True)

    def _onTreeDeckAdd(self, item=None):
        parent=item.fullname+"::" if item and item.type=='deck' else ''
        subdeck = getOnlyText(_("Name for deck/subdeck:"))
        if subdeck:
            mw.col.decks.id(parent+subdeck)
            self._saveDecks()
            mw.reset(True)

    def _onTreeDeckDelete(self, item):
        self.browser._lastSearchTxt=""
        sel=mw.col.decks.byName(item.fullname)
        mw.deckBrowser._delete(sel['id'])
        self._saveDecks()
        mw.reset(True)

    def _onTreeDeckRenameLeaf(self, item):
        mw.checkpoint(_("Rename Deck"))
        from aqt.utils import showWarning
        from anki.errors import DeckRenameError

        self.browser._lastSearchTxt=""
        sel = mw.col.decks.byName(item.fullname)
        try:
            path,leaf = item.fullname.rsplit('::',1)
            newName = path+'::'+ getOnlyText(_("New deck name:"), default=leaf)
        except ValueError:
            newName = getOnlyText(_("New deck name:"), default=item.fullname)
        newName = newName.replace('"', "")
        if not newName or newName == item.fullname:
            return

        newName = unicodedata.normalize("NFC", newName)
        deck = mw.col.decks.get(sel["id"])
        try:
            mw.col.decks.rename(deck, newName)
        except DeckRenameError as e:
            return showWarning(e.description)
        self._swapHighlight(item.type,item.fullname,newName)
        self._saveDecks()
        # self.highlight('deck',newName)
        mw.show()
        mw.reset(True)

    def _onTreeDeckRename(self, item):
        self.browser._lastSearchTxt=""
        sel=mw.col.decks.byName(item.fullname)
        mw.deckBrowser._rename(sel['id'])
        if item.fullname != sel['name']:
            # TODO: current version of anki api does not normalize on renames.
            # Remove this line once it does.
            sel['name'] = unicodedata.normalize("NFC", sel['name'])

            self._swapHighlight(item.type,item.fullname,sel['name'])
            self._saveDecks()
            # self.highlight('deck',sel['name'])
            mw.reset(True)

    def _onTreeDeckAddCard(self, item):
        from aqt import addcards
        d = mw.col.decks.byName(item.fullname)
        mw.col.decks.select(d["id"])
        diag = aqt.dialogs.open("AddCards", self.mw)

    def _onTreeTagAddCard(self, item):
        from aqt import addcards
        tags=[]
        items=self.selectedIndexes()
        for i in items:
            itm=i.internalPointer()
            tags.append(itm.fullname)
        diag = aqt.dialogs.open("AddCards", self.mw)
        diag.editor.tags.setText(" ".join(tags))

    def _onTreeTagRenameLeaf(self, item):
        oldNameArr = item.fullname.split("::")
        newName = getOnlyText(_("New tag name:"),default=oldNameArr[-1])
        newName = unicodedata.normalize("NFC", newName)
        newName = newName.replace('"', "")
        if not newName or newName == oldNameArr[-1]:
            return
        oldNameArr[-1] = newName
        newName = "::".join(oldNameArr)
        self.moveTag(item.fullname,newName)
        # self.highlight('tag',newName)

    def _onTreeTagRenameBranch(self, item):
        newName = getOnlyText(_("New tag name:"),default=item.fullname)
        newName = unicodedata.normalize("NFC", newName)
        newName = newName.replace('"', "")
        if not newName or newName == item.fullname:
            return
        self.moveTag(item.fullname,newName)
        # self.highlight('tag',newName)

    def _onTreeTagDelete(self, item):
        "allows del of multi selected tags"
        self.browser.editor.saveNow(self.hideEditor)
        items=self.selectedIndexes()
        for i in items:
            itm=i.internalPointer()
            self._massDelTag(itm.fullname)
        self._saveTags()
        mw.col.tags.registerNotes()

    def _massDelTag(self, dragName):
        # rename children
        for tag in mw.col.tags.all():
            if tag.startswith(dragName + "::"):
                ids = self.findNotes('"tag:%s"'%tag)
                self._swapHighlight('tag',tag,"",False)
                mw.col.tags.bulkRem(ids,tag)
        # rename parent
        ids = self.findNotes('"tag:%s"'%dragName)
        mw.col.tags.bulkRem(ids,dragName)
        self._swapHighlight('tag',dragName,"",False)

    def _onTreeTag(self, item, add=True):
        sel = self.browser.selectedNotes()
        tag = item.fullname
        self.browser.model.beginReset()
        if add:
            mw.col.tags.bulkAdd(sel,tag)
        else:
            mw.col.tags.bulkRem(sel,tag)
        self.browser.model.endReset()
        mw.requireReset()

    def _onTreeUnTag(self, item):
        self._onTreeTag(item,False)
        self.refresh()

    def _onTreeDeck2Tag(self, item):
        msg = _("Convert all notes in deck/subdecks to tags?")
        if not askUser(msg, parent=self, defaultno=True):
            return

        mw.progress.start(
            label=_("Converting decks to tags"))
        try:
            self.browser._lastSearchTxt=""
            parentDid = mw.col.decks.byName(item.fullname)["id"]
            actv = mw.col.decks.children(parentDid)
            actv = sorted(actv, key=lambda t: t[0])
            actv.insert(0,(item.fullname,parentDid))

            found = False
            for name,did in actv:
                mw.progress.update(label=name)
                #add subdeck tree structure as tags
                nids = self.findNotes('''"deck:%s" -"deck:%s::*"'''%(name,name))
                if nids:
                    found = True
                    tagName = re.sub(r"\s*(::)\s*","\g<1>",name)
                    tagName = re.sub(r"\s+","_",tagName)
                    tagName = unicodedata.normalize("NFC", tagName)
                    mw.col.tags.bulkAdd(nids, tagName)
                #skip parent or dyn decks
                if did == parentDid or mw.col.decks.get(did)['dyn']:
                    continue
                #collapse subdecks into one
                mw.col.sched.emptyDyn(None, "odid=%d"%did)
                mw.col.db.execute(
                    "update cards set usn=?, mod=?, did=? where did=?",
                    mw.col.usn(), intTime(), parentDid, did
                )
                mw.col.decks.rem(did,childrenToo=False)
        finally:
            mw.progress.finish()
            if not found:
                showInfo("No Cards in deck")
                return
            self._saveDecks()
            self._saveTags()
            # self.highlight('tag',item.fullname)
            mw.col.tags.registerNotes()
            mw.requireReset()


    def _onTreeTag2Deck(self, item):
        def tag2Deck(tag):
            did = mw.col.decks.id(tag)
            cids = self.findCards('"tag:%s"'%tag)
            if not cids:
                return
            mw.col.sched.remFromDyn(cids)
            mw.col.db.execute(
                "update cards set usn=?, mod=?, did=? where id in %s"%ids2str(cids),
                mw.col.usn(), intTime(), did
            )
            nids = self.findNotes('"tag:%s"'%tag)
            mw.col.tags.bulkRem(nids,tag)

        msg = _("Convert all tags to deck structure?")
        if not askUser(msg, parent=self, defaultno=True):
            return

        mw.progress.start(
            label=_("Converting tags to decks"))

        try:
            self.browser._lastSearchTxt=""
            parent = unicodedata.normalize("NFC", item.fullname)
            tag2Deck(parent)
            for tag in mw.col.tags.all():
                mw.progress.update(label=tag)
                if tag.startswith(parent + "::"):
                    tag2Deck(tag)
        finally:
            mw.progress.finish()
            self._saveDecks()
            self._saveTags()
            # self.highlight('deck',item.fullname)
            mw.col.tags.registerNotes()
            mw.requireReset()


    def _onTreePinDelete(self, item):
        savedFilters = self.getConf('savedFilters', {})
        for idx in self.selectedIndexes():
            itm = idx.internalPointer()
            if savedFilters.get(itm.favname):
                del savedFilters[itm.favname]
        self.setConf('savedFilters', savedFilters)

    def _onTreeFavDelete(self, item):
        savedFilters = self.getConf('savedFilters', {})
        for idx in self.selectedIndexes():
            itm = idx.internalPointer()
            if savedFilters.get(itm.favname) and \
            askUser(_("Remove %s from your saved searches?") % itm.favname):
                del savedFilters[itm.favname]
        self.setConf('savedFilters', savedFilters)

    def _onTreeFavRename(self, item):
        savedFilters = self.getConf('savedFilters', {})
        act = savedFilters.get(item.favname)
        if not act: return
        s=item.favname
        p=False
        if item.type.startswith("pin"):
            s=re.sub(r"^Pinned::","",s)
            p=True
        newName = getOnlyText(_("New search name:"),default=s)
        newName = re.sub(r"^Pinned::","",newName)
        if newName:
            if p: newName="Pinned::"+newName
            del(savedFilters[item.favname])
            savedFilters[newName] = act
        self.setConf('savedFilters', savedFilters)

    def _onTreeFavModify(self, item):
        savedFilters = self.getConf('savedFilters', {})
        act = savedFilters.get(item.fullname)
        if not act: return
        act=getOnlyText(_("New Search:"),default=act)
        if act:
            savedFilters[item.fullname]=act
        self.setConf('savedFilters', savedFilters)

    def _onTreeModelRenameLeaf(self, item):
        self.browser._lastSearchTxt=""
        oldNameArr = item.fullname.split("::")
        newName = getOnlyText(_("New model name:"),default=oldNameArr[-1])
        newName = newName.replace('"', "")
        if not newName or newName == oldNameArr[-1]:
            return
        oldNameArr[-1] = unicodedata.normalize("NFC", newName)
        newName = "::".join(oldNameArr)
        self.moveModel(item.fullname,newName,item)
        # self.highlight('model',newName)

    def _onTreeModelRenameBranch(self, item):
        self.browser._lastSearchTxt=""
        newName = getOnlyText(_("New model name:"),default=item.fullname)
        newName = newName.replace('"', "")
        if not newName or newName == item.fullname:
            return
        newName = unicodedata.normalize("NFC", newName)
        self.moveModel(item.fullname,newName,item)
        # self.highlight('model',newName)

    def _onTreeModelDelete(self, item):
        self.browser._lastSearchTxt=""
        model = mw.col.models.get(item.mid)
        if not model:
            return
        if mw.col.models.useCount(model):
            msg = _("Delete this note type and all its cards?")
        else:
            msg = _("Delete this unused note type?")
        if askUser(msg, parent=self, defaultno=True):
            try:
                mw.col.models.rem(model)
            except AnkiError:
                #user says no to full sync requirement
                return
        self._saveModels()
        self.browser.setupTable()
        self.browser.model.reset()

    def _onTreeModelAdd(self, item):
        from aqt.models import AddModel
        self.browser.form.searchEdit.lineEdit().setText("")
        m = AddModel(self.mw, self.browser).get()
        if m:
            #model is already created
            txt = getOnlyText(_("Name:"), default=item.fullname+'::')
            if txt:
                m['name'] = txt
            mw.col.models.ensureNameUnique(m)
            mw.col.models.save(m)

    def onTreeModelFields(self, item):
        from aqt.fields import FieldDialog
        model = mw.col.models.get(item.mid)
        mw.col.models.setCurrent(model)
        n = mw.col.newNote(forDeck=False)
        for name in list(n.keys()):
            n[name] = "("+name+")"
        try:
            if "{{cloze:Text}}" in model['tmpls'][0]['qfmt']:
                n['Text'] = _("This is a {{c1::sample}} cloze deletion.")
        except:
            # invalid cloze
            pass
        FieldDialog(self.mw, n, parent=self.browser)

    def onTreeModelOptions(self, item):
        from aqt.forms import modelopts
        model = mw.col.models.get(item.mid)
        d = QDialog(self)
        frm = modelopts.Ui_Dialog()
        frm.setupUi(d)
        frm.latexHeader.setText(model['latexPre'])
        frm.latexFooter.setText(model['latexPost'])
        d.setWindowTitle(_("Options for %s") % model['name'])
        d.exec_()
        model['latexPre'] = str(frm.latexHeader.toPlainText())
        model['latexPost'] = str(frm.latexFooter.toPlainText())
        self._saveModels()

    def onManageModel(self):
        self.browser.editor.saveNow(self.hideEditor)
        mw.checkpoint("Manage model")
        import aqt.models
        aqt.models.Models(self.mw, self.browser)
        mw.col.setMod()
        self.browser.onReset()
        self.browser.maybeRefreshSidebar()


    def _onTreeCramTags(self, index):
        indexes=self.selectedIndexes()
        if index not in indexes:
            indexes.append(index)
        tags=[]
        for idx in indexes:
            item = idx.internalPointer()
            if self.getConf('Blitzkrieg.showAllTags', True):
                tags.append('''tag:"%s*"'''%item.fullname)
            else:
                tags.append('''tag:"%s"'''%item.fullname)
        self.clearSelection()
        mw.onCram("("+" or ".join(tags)+")")


    def _onTreeMark(self, index):
        indexes=self.selectedIndexes()
        if index not in indexes:
            indexes.append(index)
        for idx in indexes:
            item = idx.internalPointer()
            tf=not self.marked[item.type].get(item.fullname, False)
            self.marked[item.type][item.fullname]=tf
            color=QBrush(Qt.yellow) if tf else None
            item.background=color
        self.clearSelection()

    def _onTreePin(self, index):
        savedFilters = self.getConf('savedFilters', {})
        indexes=self.selectedIndexes()
        if index not in indexes:
            indexes.append(index)
        for idx in indexes:
            item = idx.internalPointer()
            name = "Pinned::%s"%(
                item.fullname.split("::")[-1])
            search = '"%s:%s"'%(item.type,item.fullname)
            savedFilters[name] = search
        self.setConf('savedFilters', savedFilters)
        self.browser.maybeRefreshSidebar()

    def onEmptyAll(self):
        for d in mw.col.decks.all():
            if d['dyn']:
                mw.col.sched.emptyDyn(d['id'])
        self.browser.onReset()

    def onRebuildAll(self):
        for d in mw.col.decks.all():
            if d['dyn']:
                mw.col.sched.rebuildDyn(d['id'])
        self.browser.onReset()

    def hasValue(self, item):
        if item.type == "model":
            return mw.col.models.byName(item.fullname)
        if item.type == "fav":
            savedFilters = self.getConf('savedFilters', {})
            return savedFilters.get(item.fullname)
        if item.type in ("pinTag","pinDeck","pinDyn"):
            savedFilters = self.getConf('savedFilters', {})
            return savedFilters.get(item.favname)
        return False

    def _toggleMWUpdate(self):
        up = self.getConf('Blitzkrieg.updateOV', False)
        self.setConf('Blitzkrieg.updateOV', not up)

    def _toggleShowSubtags(self):
        sa = self.getConf('Blitzkrieg.showAllTags', True)
        self.setConf('Blitzkrieg.showAllTags', not sa)

    def _toggleSortOption(self, item):
        sort = not self.getConf('Blitzkrieg.sort_'+item.fullname,False)
        self.setConf('Blitzkrieg.sort_'+item.fullname, sort)
        self.browser.maybeRefreshSidebar()

    def _toggleIconOption(self, item):
        TYPE='fav' if item.type in ("pin","fav") else item.fullname
        ico = not self.getConf('Blitzkrieg.icon_'+TYPE,True)
        self.setConf('Blitzkrieg.icon_'+TYPE, ico)
        self.browser.maybeRefreshSidebar()


    def expandAllChildren(self, index, expanded=False):
        self._expandAllChildren(index, expanded)
        for idx in self.selectedIndexes():
            self._expandAllChildren(idx, expanded)

    def _expandAllChildren(self, parentIdx, expanded=False):
        parentItem=parentIdx.internalPointer()
        parentItem.expanded=expanded
        for row, child in enumerate(parentItem.children):
            childIdx = self.model().index(row, 0, parentIdx)
            self._expandAllChildren(childIdx, expanded)

        self.setExpanded(parentIdx, expanded)
        try: #no deck type
            self.node_state[parentItem.type][parentItem.fullname]=expanded
        except TypeError: pass


    def findRecursive(self, index):
        from .forms import findtreeitems
        item=index.internalPointer()
        TAG_TYPE = item.fullname
        self.found = {}
        self.found[TAG_TYPE] = {}
        d = QDialog(self.browser)
        frm = findtreeitems.Ui_Dialog()
        frm.setupUi(d)

        # Restore btn states
        frm.input.setText(self.finder.get('txt',''))
        frm.input.setFocus()
        frm.cb_case.setChecked(self.finder.get('case',0))
        for idx,func in enumerate((
            frm.btn_contains, frm.btn_exactly,
            frm.btn_startswith, frm.btn_endswith,
            frm.btn_regexp
        )):
            func.setChecked(0)
            if self.finder.get('radio',0)==idx:
                func.setChecked(2)

        if not d.exec_():
            return

        txt = frm.input.text()
        if not txt:
            return
        txt = unicodedata.normalize("NFC", txt)
        options = Qt.MatchRecursive
        if txt=='vote for pedro':
            mw.pm.profile['Blitzkrieg.VFP']=True
            from .alt import disabledDebugStuff
            disabledDebugStuff()
        self.finder['txt'] = txt
        self.finder['case'] = frm.cb_case.isChecked()
        if self.finder['case']:
            options |= Qt.MatchCaseSensitive

        if frm.btn_exactly.isChecked():
            options |= Qt.MatchExactly
            self.finder['radio'] = 1
        elif frm.btn_startswith.isChecked():
            options |= Qt.MatchStartsWith
            self.finder['radio'] = 2
        elif frm.btn_endswith.isChecked():
            options |= Qt.MatchEndsWith
            self.finder['radio'] = 3
        elif frm.btn_regexp.isChecked():
            options |= Qt.MatchRegExp
            self.finder['radio'] = 4
        else:
            options |= Qt.MatchContains
            self.finder['radio'] = 0

        self.expandAllChildren(index,True)

        for idx in self.findItems(txt,options):
            itm = idx.internalPointer()
            if itm.type == TAG_TYPE:
                itm.background=QBrush(Qt.cyan)
                self.found[TAG_TYPE][itm.fullname] = True

        if not self.found[TAG_TYPE]:
            showInfo("Found nothing, nada, zilch!")

    def findItems(self, txt, options):
        model=self.model()
        return model.match(
            self.currentIndex(), Qt.DisplayRole,
            QVariant(txt), -1, options
        )

    def refresh(self):
        self.found = {}
        mw.col.tags.registerNotes() #calls "newTag" hook which invokes maybeRefreshSidebar
        #Clear to create a smooth UX
        self.marked['group'] = {}
        self.marked['pinDeck'] = {}
        self.marked['pinDyn'] = {}
        self.marked['pinTag'] = {}

    def _swapHighlight(self, type, oName, nName, swap=True):
        if swap and self.marked[type].get(oName, False):
            self.marked[type][nName] = True
        try:
            del(self.marked[type][oName])
        except KeyError: pass


    def _saveTags(self):
        # for anki 2.1.24beta4 and below
        try:
            mw.col.tags.save()
            mw.col.tags.flush()
        except AttributeError: pass

    def _saveDecks(self):
        try:
            mw.col.decks.save()
            mw.col.decks.flush()
        except AttributeError: pass

    def _saveModels(self):
        try:
            mw.col.models.save()
            mw.col.models.flush()
        except AttributeError: pass






class TagTreeWidget(QTreeWidget):
    def __init__(self, browser, parent):
        QTreeWidget.__init__(self, parent)
        self.setHeaderHidden(True)
        self.browser = browser
        self.col = browser.col
        self.node = {}
        self.addMode = False
        self.color = Qt.red

        self.itemClicked.connect(self.onClick)
        self.itemExpanded.connect(self.onCollapse)
        self.itemCollapsed.connect(self.onCollapse)

        # self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def onClick(self, item, col):
        item.setSelected(False)
        if self.addMode or item.type=="tag":
            s = not self.node.get(item.fullname,False)
            self.node[item.fullname] = s
            color = self.color if s else Qt.transparent
            item.setBackground(0, QBrush(color))

    def onCollapse(self, item):
        try:
            s = self.node.get(item.fullname,False)
            color = self.color if s else Qt.transparent
            item.setBackground(0, QBrush(color))
        except AttributeError: pass

    def removeTags(self, nids):
        self.addMode = False
        self.color = Qt.red
        SORT = self.col.conf.get('Blitzkrieg.sort_tag',False)
        tags = self.col.db.list("""
select tags from notes where id in %s""" % ids2str(nids))
        tags = sorted(" ".join(tags).split(),
            key=lambda t: t.lower() if SORT else t)
        self._setTags(tags)

    def addTags(self, nids):
        self.addMode = True
        self.color = Qt.green
        SORT = self.col.conf.get('Blitzkrieg.sort_tag',False)
        allTags = sorted(self.col.tags.all(),
                key=lambda t: t.lower() if SORT else t)
        tags = self.col.db.list("""
select tags from notes where id in %s""" % ids2str(nids))
        tags = set(" ".join(tags).split())
        self._setTags(allTags,tags)

    def _setTags(self, allTags, curTags=""):
        tags_tree = {}
        for t in allTags:
            if self.addMode and t.lower() in ("marked","leech"):
                continue
            node = t.split('::')
            for idx, name in enumerate(node):
                leaf_tag = '::'.join(node[0:idx + 1])
                if not tags_tree.get(leaf_tag):
                    parent = tags_tree['::'.join(node[0:idx])] if idx else self
                    item = QTreeWidgetItem(parent,[name])
                    item.fullname = leaf_tag
                    item.setExpanded(True)
                    tags_tree[leaf_tag] = item
                    if leaf_tag in curTags:
                        item.setBackground(0, QBrush(Qt.yellow))
            try:
                item.type = "tag"
                item.setIcon(0, QIcon(":/icons/tag.svg"))
            except AttributeError: pass
