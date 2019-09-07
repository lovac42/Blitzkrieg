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
    root = browser.CallbackItem(root, _("Searches"), None, expanded=True)
    root.type = "group"
    root.fullname = "fav"
    root.setExpanded(browser.sidebarTree.node_state.get("group").get('fav',True))
    root.setIcon(0, QIcon(":/icons/heart.svg"))
    for name, filt in sorted(saved.items()):
        item = browser.CallbackItem(root, name, lambda s=filt: browser.setFilter(s))
        item.type="fav"
        item.fullname = name
        item.setIcon(0, QIcon(":/icons/heart.svg"))


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
                item = browser.CallbackItem(
                    parent, name,
                    lambda p=leaf_tag: browser.setFilter("tag",p),
                    expanded=browser.sidebarTree.node_state.get('tag').get(leaf_tag,False)
                )
                item.type = "tag"
                item.fullname = leaf_tag
                item.setIcon(0, QIcon(":/icons/tag.svg"))
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
            item.type="deck"
            item.fullname = head + g[0]
            item.setIcon(0, QIcon(":/icons/deck.svg"))
            newhead = head + g[0]+"::"
            fillGroups(item, g[5], newhead)
            # item.setExpanded(bool(len(grps)<2))
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
                models_tree[leaf_model] = item
