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
        for idx, name in enumerate(node):
            leaf_tag = '::'.join(node[0:idx + 1])
            if not favs_tree.get(leaf_tag):
                parent = favs_tree['::'.join(node[0:idx])] if idx else root
                item = browser.CallbackItem(
                    parent, name,
                    lambda s=filt: browser.setFilter(s),
                    expanded=browser.sidebarTree.node_state.get('fav').get(leaf_tag,True)
                )
                item.type = "fav"
                item.fullname = leaf_tag
                item.setIcon(0, QIcon(":/icons/heart.svg"))
                if browser.sidebarTree.marked['fav'].get(leaf_tag, False):
                    item.setBackground(0, QBrush(Qt.yellow))
                favs_tree[leaf_tag] = item


def userTagTree(browser, root):
    root = browser.CallbackItem(root, _("Tags"), None, expanded=True)
    root.type = "group"
    root.fullname = "tag"
    root.setExpanded(browser.sidebarTree.node_state.get("group").get('tag',True))
    root.setIcon(0, QIcon(":/icons/tag.svg"))
    tags_tree = {}
    for t in sorted(browser.col.tags.all(), key=lambda t: t.lower()):
        if t.lower() == "marked" or t.lower() == "leech":
            continue
        node = t.split('::')
        for idx, name in enumerate(node):
            leaf_tag = '::'.join(node[0:idx + 1])
            if not tags_tree.get(leaf_tag):
                parent = tags_tree['::'.join(node[0:idx])] if idx else root
                exp = browser.sidebarTree.node_state.get('tag').get(leaf_tag,False)
                item = browser.CallbackItem(
                    parent, name,
                    lambda p=leaf_tag: browser.setFilter("tag",p),
                    expanded=exp
                )
                item.type = "tag"
                item.fullname = leaf_tag
                item.setIcon(0, QIcon(":/icons/tag.svg"))
                if browser.sidebarTree.marked['tag'].get(leaf_tag, False):
                    item.setBackground(0, QBrush(Qt.yellow))
                elif exp and '::' not in leaf_tag:
                    item.setBackground(0, QBrush(QColor(0,0,10,10)))
                tags_tree[leaf_tag] = item


def decksTree(browser, root):
    root = browser.CallbackItem(root, _("Decks"), None, expanded=True)
    root.type = "group"
    root.fullname = "deck"
    root.setExpanded(browser.sidebarTree.node_state.get("group").get('deck',True))
    root.setIcon(0, QIcon(":/icons/deck.svg"))
    grps = browser.col.sched.deckDueTree()
    def fillGroups(root, grps, head=""):
        for g in grps:
            item = browser.CallbackItem(
                root, g[0],
                lambda g=g: browser.setFilter("deck", head+g[0]),
                lambda g=g: browser.mw.col.decks.collapseBrowser(g[1]),
                not browser.mw.col.decks.get(g[1]).get('browserCollapsed', False))
            item.fullname = head + g[0]
            item.setIcon(0, QIcon(":/icons/deck.svg"))
            if mw.col.decks.byName(item.fullname)['dyn']:
                item.setForeground(0, QBrush(Qt.blue))
                item.type = "dyn"
            else:
                item.type = "deck"
            if browser.sidebarTree.marked[item.type].get(item.fullname, False):
                item.setBackground(0, QBrush(Qt.yellow))
            newhead = head + g[0]+"::"
            fillGroups(item, g[5], newhead)
    fillGroups(root, grps)


def modelTree(browser, root):
    root = browser.CallbackItem(root, _("Models"), None)
    root.type = "group"
    root.fullname = "model"
    root.setExpanded(browser.sidebarTree.node_state.get("group").get('model',False))
    root.setIcon(0, QIcon(":/icons/notetype.svg"))
    models_tree = {}
    for m in sorted(browser.col.models.all(), key=itemgetter("name")):
        node = m['name'].split('::')
        for idx, name in enumerate(node):
            leaf_model = '::'.join(node[0:idx + 1])
            if not models_tree.get(leaf_model):
                parent = models_tree['::'.join(node[0:idx])] if idx else root
                item = browser.CallbackItem(
                    parent, name,
                    lambda m=m: browser.setFilter("mid", str(m['id'])),
                    expanded=browser.sidebarTree.node_state.get('model').get(leaf_model,False)
                )
                item.type = "model"
                item.fullname = leaf_model
                item.setIcon(0, QIcon(":/icons/notetype.svg"))
                if browser.sidebarTree.marked['model'].get(leaf_model, False):
                    item.setBackground(0, QBrush(Qt.yellow))
                models_tree[leaf_model] = item
