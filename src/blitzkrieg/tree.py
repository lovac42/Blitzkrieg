# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# Copyright 2014 Patrice Neff
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


from aqt import mw
from aqt.qt import *
from anki.lang import ngettext, _
from operator import  itemgetter

from .lib.com.lovac42.anki.backend.collection import getConfigGetterMethod


try:
    from aqt.browser import SidebarItem
except: #SHOULD_PATCH
    from .patch_sidebar import SidebarItem



def stdTree(browser, root):
    for name, filt, icon in [[_("Whole Collection"), "", "collection"],
                       [_("Current Deck"), "deck:current", "deck"]]:
        item = SidebarItem(
            name, ":/icons/{}.svg".format(icon), browser._filterFunc(filt))
        item.type=None
        root.addChild(item)



def favTree(browser, root):
    assert browser.col
    tree = browser.sidebarTree
    ico = ":/icons/heart.svg"

    getConfig = getConfigGetterMethod()

    icoOpt = getConfig('Blitzkrieg.icon_fav',True)

    saved = getConfig('savedFilters', {})
    if not saved:
        return
    favs_tree = {}
    for fav, filt in sorted(saved.items()):
        node = fav.split('::')
        lstIdx = len(node)-1
        ico = "heart.svg"
        type = "fav"
        fname = None
        for idx, name in enumerate(node):
            if node[0]=='Pinned':
                if idx==0:
                    type = "pin"
                elif filt.startswith('"tag:'):
                    type = "pinTag"
                    ico = "tag.svg"
                    fname = filt[5:-1]
                elif filt.startswith('"deck:'):
                    type = "pinDeck"
                    ico = "deck.svg"
                    fname = filt[6:-1]
                elif filt.startswith('"dyn:'):
                    type = "pinDyn"
                    ico = "deck.svg"
                    fname = filt[5:-1]
                    filt='"deck'+filt[4:]

            item = None
            leaf_tag = '::'.join(node[0:idx + 1])
            if not favs_tree.get(leaf_tag):
                parent = favs_tree['::'.join(node[0:idx])] if idx else root
                exp = tree.node_state.get(type).get(leaf_tag,False)
                item = SidebarItem(
                    name,
                    (":/icons/"+ico) if icoOpt or not idx or idx==lstIdx else None,
                    browser._filterFunc(filt),
                    expanded=exp
                )
                parent.addChild(item)

                item.type = type
                item.fullname = fname or leaf_tag
                item.favname = leaf_tag
                if tree.marked[type].get(leaf_tag, False):
                    item.background=QBrush(Qt.yellow)
                favs_tree[leaf_tag] = item




def userTagTree(browser, root):
    assert browser.col
    tree=browser.sidebarTree
    ico = ":/icons/tag.svg"
    getConfig = getConfigGetterMethod()

    icoOpt = getConfig('Blitzkrieg.icon_tag',True)
    rootNode = SidebarItem(
        "Tags", ico,
        expanded=tree.node_state.get("group").get('tag',True)
    )
    rootNode.type = "group"
    rootNode.fullname = "tag"
    root.addChild(rootNode)

    tags_tree = {}
    SORT = getConfig('Blitzkrieg.sort_tag',False)
    TAGS = sorted(browser.col.tags.all(),
            key=lambda t: t.lower() if SORT else t)
    for t in TAGS:
        if t.lower() == "marked" or t.lower() == "leech":
            continue
        node = t.split('::')
        lstIdx = len(node)-1
        for idx, name in enumerate(node):
            leaf_tag = '::'.join(node[0:idx + 1])
            if not tags_tree.get(leaf_tag):
                parent = tags_tree['::'.join(node[0:idx])] if idx else rootNode
                exp = tree.node_state.get('tag').get(leaf_tag,False)
                item = SidebarItem(
                    name, ico if icoOpt or idx==lstIdx else None,
                    browser._filterFunc("tag",leaf_tag),
                    expanded=exp
                )
                parent.addChild(item)

                item.type = "tag"
                item.fullname = leaf_tag
                if tree.found.get(item.type,{}).get(leaf_tag, False):
                    item.background=QBrush(Qt.cyan)
                elif tree.marked['tag'].get(leaf_tag, False):
                    item.background=QBrush(Qt.yellow)
                elif exp and '::' not in leaf_tag:
                    item.background=QBrush(QColor(0,0,10,10))
                tags_tree[leaf_tag] = item

    tag_cnt = len(TAGS)
    rootNode.tooltip = f"Total: {tag_cnt} tags"





def decksTree(browser, root):
    assert browser.col
    tree=browser.sidebarTree
    ico = ":/icons/deck.svg"
    rootNode = SidebarItem(
        _("Decks"), ico,
        expanded=tree.node_state.get("group").get('deck',True)
    )
    rootNode.type = "group"
    rootNode.fullname = "deck"
    root.addChild(rootNode)

    getConfig = getConfigGetterMethod()

    SORT = getConfig('Blitzkrieg.sort_deck',False)
    grps = sorted(browser.col.sched.deckDueTree(),
            key=lambda g: g[0].lower() if SORT else g[0])
    def fillGroups(rootNode, grps, head=""):
        for g in grps:
            item = SidebarItem(
                g[0], ico,
                lambda g=g: browser.setFilter("deck", head+g[0]),
                lambda expanded, g=g: browser.mw.col.decks.collapseBrowser(g[1]),
                not browser.mw.col.decks.get(g[1]).get('browserCollapsed', False))
            rootNode.addChild(item)
            item.fullname = head + g[0] #name
            if mw.col.decks.isDyn(g[1]): #id
                item.foreground = QBrush(Qt.blue)
                item.type = "dyn"
            else:
                if g[1]==1: #default deck
                    item.foreground = QBrush(Qt.darkRed)
                item.type = "deck"
            if tree.found.get(item.type,{}).get(item.fullname, False):
                item.background=QBrush(Qt.cyan)
            elif tree.marked[item.type].get(item.fullname, False):
                item.background=QBrush(Qt.yellow)
            newhead = head + g[0]+"::"
            fillGroups(item, g[5], newhead)

    fillGroups(rootNode, grps)

    deck_cnt = len(browser.col.decks.all())
    rootNode.tooltip = f"Total: {deck_cnt} decks"





def modelTree(browser, root):
    assert browser.col
    tree=browser.sidebarTree
    ico = ":/icons/notetype.svg"

    getConfig = getConfigGetterMethod()

    icoOpt = getConfig('Blitzkrieg.icon_model',True)
    rootNode = SidebarItem(
        _("Models"), ico,
        expanded=tree.node_state.get("group").get('model',False)
    )
    rootNode.type = "group"
    rootNode.fullname = "model"
    root.addChild(rootNode)

    models_tree = {}
    SORT = getConfig('Blitzkrieg.sort_model',False)
    MODELS = sorted(browser.col.models.all(),
            key=lambda m: m["name"].lower() if SORT else m["name"])
    for m in MODELS:
        item = None
        mid=str(m['id'])
        node = m['name'].split('::')
        lstIdx = len(node)-1
        for idx, name in enumerate(node):
            leaf_model = '::'.join(node[0:idx + 1])
            if not models_tree.get(leaf_model) or idx==lstIdx: #last element, model names are not unique
                parent = models_tree['::'.join(node[0:idx])] if idx else rootNode
                exp = tree.node_state.get('model').get(leaf_model,False)

                item = SidebarItem(
                    name, ico if icoOpt or idx==lstIdx else None,
                    browser._filterFunc("mid", str(m['id'])),
                    expanded=exp
                )
                parent.addChild(item)
                item.type = "model"
                item.fullname = leaf_model
                item.mid = mid

                if tree.found.get(item.type,{}).get(leaf_model, False):
                    item.background=QBrush(Qt.cyan)
                elif tree.marked['model'].get(leaf_model, False):
                    item.background=QBrush(Qt.yellow)
                models_tree[leaf_model] = item

    model_cnt = len(MODELS)
    rootNode.tooltip = f"Total: {model_cnt} models"

