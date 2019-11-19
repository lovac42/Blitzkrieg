# -*- coding: utf-8 -*-
# Copyright 2019 Lovac42
# Copyright 2014 Patrice Neff
# Copyright 2006-2019 Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


from aqt import mw
from aqt.qt import *
from anki.lang import ngettext, _
from operator import  itemgetter



def favTree(browser, root):
    saved = browser.col.conf.get('savedFilters', {})
    if not saved:
        return
    favs_tree = {}
    for fav, filt in sorted(saved.items()):
        node = fav.split('::')
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
                item = browser.CallbackItem(
                    parent, name,
                    lambda s=filt: browser.setFilter(s),
                    expanded=root.node_state.get(type).get(leaf_tag,True)
                )
                item.type = type
                item.fullname = fname or leaf_tag
                item.favname = leaf_tag
                if not idx or browser.col.conf.get('Blitzkrieg.icon_fav',True):
                    item.setIcon(0, QIcon(":/icons/"+ico))
                if root.marked[type].get(leaf_tag, False):
                    item.setBackground(0, QBrush(Qt.yellow))
                favs_tree[leaf_tag] = item
        try:
            item.setIcon(0, QIcon(":/icons/"+ico))
        except AttributeError: pass


def userTagTree(browser, root):
    ico = QIcon(":/icons/tag.svg")
    icoOpt = browser.col.conf.get('Blitzkrieg.icon_tag',True)
    rootNode = browser.CallbackItem(root, _("Tags"), None, expanded=True)
    rootNode.type = "group"
    rootNode.fullname = "tag"
    rootNode.setExpanded(root.node_state.get("group").get('tag',True))
    rootNode.setIcon(0, QIcon(":/icons/tag.svg"))
    tags_tree = {}
    SORT = browser.col.conf.get('Blitzkrieg.sort_tag',False)
    TAGS = sorted(browser.col.tags.all(),
            key=lambda t: t.lower() if SORT else t)
    for t in TAGS:
        if t.lower() == "marked" or t.lower() == "leech":
            continue
        item = None
        node = t.split('::')
        for idx, name in enumerate(node):
            leaf_tag = '::'.join(node[0:idx + 1])
            if not tags_tree.get(leaf_tag):
                parent = tags_tree['::'.join(node[0:idx])] if idx else rootNode
                exp = root.node_state.get('tag').get(leaf_tag,False)
                item = browser.CallbackItem(
                    parent, name,
                    lambda p=leaf_tag: browser.setFilter("tag",p),
                    expanded=exp
                )
                item.type = "tag"
                item.fullname = leaf_tag
                if icoOpt:
                    item.setIcon(0, ico)
                if root.found.get(item.type,{}).get(leaf_tag, False):
                    item.setBackground(0, QBrush(Qt.cyan))
                elif root.marked['tag'].get(leaf_tag, False):
                    item.setBackground(0, QBrush(Qt.yellow))
                elif exp and '::' not in leaf_tag:
                    item.setBackground(0, QBrush(QColor(0,0,10,10)))
                tags_tree[leaf_tag] = item
        try:
            item.setIcon(0, ico)
        except AttributeError: pass

    totTags=len(TAGS)
    if totTags>1000:
        rootNode.setText(0, _("Tags (Warning: too many tags)"))
    rootNode.setToolTip(0, _("Total: %d tags"%totTags))


def decksTree(browser, root):
    rootNode = browser.CallbackItem(root, _("Decks"), None, expanded=True)
    rootNode.type = "group"
    rootNode.fullname = "deck"
    rootNode.setExpanded(root.node_state.get("group").get('deck',True))
    rootNode.setIcon(0, QIcon(":/icons/deck.svg"))
    SORT = browser.col.conf.get('Blitzkrieg.sort_deck',False)
    grps = sorted(browser.col.sched.deckDueTree(),
            key=lambda g: g[0].lower() if SORT else g[0])
    def fillGroups(rootNode, grps, head=""):
        for g in grps:
            item = browser.CallbackItem(
                rootNode, g[0],
                lambda g=g: browser.setFilter("deck", head+g[0]),
                lambda g=g: browser.mw.col.decks.collapseBrowser(g[1]),
                not browser.mw.col.decks.get(g[1]).get('browserCollapsed', False))
            item.fullname = head + g[0]
            item.setIcon(0, QIcon(":/icons/deck.svg"))
            if mw.col.decks.byName(item.fullname)['dyn']:
                item.setForeground(0, QBrush(Qt.blue))
                item.type = "dyn"
            else:
                if g[1]==1: #default deck
                    item.setForeground(0, QBrush(Qt.darkRed))
                item.type = "deck"
            if root.found.get(item.type,{}).get(item.fullname, False):
                item.setBackground(0, QBrush(Qt.cyan))
            elif root.marked[item.type].get(item.fullname, False):
                item.setBackground(0, QBrush(Qt.yellow))
            newhead = head + g[0]+"::"
            fillGroups(item, g[5], newhead)
    fillGroups(rootNode, grps)

    tot=len(grps)
    if tot>500:
        rootNode.setText(0, _("Decks (Warning: too many decks)"))
    rootNode.setToolTip(0, _("Total: %d decks"%tot))


def modelTree(browser, root):
    ico = QIcon(":/icons/notetype.svg")
    icoOpt = browser.col.conf.get('Blitzkrieg.icon_model',True)
    rootNode = browser.CallbackItem(root, _("Models"), None)
    rootNode.type = "group"
    rootNode.fullname = "model"
    rootNode.setExpanded(root.node_state.get("group").get('model',False))
    rootNode.setIcon(0, QIcon(":/icons/notetype.svg"))
    models_tree = {}
    SORT = browser.col.conf.get('Blitzkrieg.sort_model',False)
    MODELS = sorted(browser.col.models.all(),
            key=lambda m: m["name"].lower() if SORT else m["name"])
    for m in MODELS:
        item = None
        node = m['name'].split('::')
        for idx, name in enumerate(node):
            leaf_model = '::'.join(node[0:idx + 1])
            if not models_tree.get(leaf_model):
                parent = models_tree['::'.join(node[0:idx])] if idx else rootNode
                item = browser.CallbackItem(
                    parent, name,
                    lambda m=m: browser.setFilter("mid", str(m['id'])),
                    expanded=root.node_state.get('model').get(leaf_model,False)
                )
                item.type = "model"
                item.fullname = leaf_model
                if icoOpt:
                    item.setIcon(0, ico)
                if root.found.get(item.type,{}).get(leaf_model, False):
                    item.setBackground(0, QBrush(Qt.cyan))
                elif root.marked['model'].get(leaf_model, False):
                    item.setBackground(0, QBrush(Qt.yellow))
                models_tree[leaf_model] = item
        try:
            item.setIcon(0, ico)
        except AttributeError: pass

    tot=len(MODELS)
    if tot>300:
        rootNode.setText(0, _("Decks (Warning: too many models)"))
    rootNode.setToolTip(0, _("Total: %d models"%tot))
