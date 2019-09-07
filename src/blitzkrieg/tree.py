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



def favTree(self, root):
    saved = self.col.conf.get('savedFilters', {})
    if not saved:
        return
    root = self.CallbackItem(root, _("Searches"), None, expanded=True)
    root.setIcon(0, QIcon(":/icons/heart.svg"))
    root.setExpanded(True)
    for name, filt in sorted(saved.items()):
        item = self.CallbackItem(root, name, lambda s=filt: self.setFilter(s))
        item.type="fav"
        item.fullname = name
        item.setIcon(0, QIcon(":/icons/heart.svg"))


def userTagTree(self, root):
    root = self.CallbackItem(root, _("Tags"), None, expanded=True)
    root.setIcon(0, QIcon(":/icons/tag.svg"))
    root.setExpanded(True)
    tags_tree = {}
    for t in sorted(self.col.tags.all(), key=lambda t: t.lower()):
        # if t.lower() == "marked" or t.lower() == "leech":
            # continue
        node = t.split('::')
        for idx, name in enumerate(node):
            leaf_tag = '::'.join(node[0:idx + 1])
            if not tags_tree.get(leaf_tag):
                if idx == 0:
                    parent = root
                else:
                    parent_tag = '::'.join(node[0:idx])
                    parent = tags_tree[parent_tag]
                item = self.CallbackItem(
                    parent, name,
                    lambda p=leaf_tag: self.setFilter("tag",p),
                    expanded=bool(len(node)>2)
                )
                item.type = "tag"
                item.fullname = leaf_tag
                item.setIcon(0, QIcon(":/icons/tag.svg"))
                tags_tree[leaf_tag] = item


def decksTree(self, root):
    root = self.CallbackItem(root, _("Decks"), None, expanded=True)
    root.setIcon(0, QIcon(":/icons/deck.svg"))
    root.setExpanded(True)
    grps = self.col.sched.deckDueTree()
    def fillGroups(root, grps, head=""):
        for g in grps:
            item = self.CallbackItem(
                root, g[0],
                lambda g=g: self.setFilter("deck", head+g[0]),
                lambda g=g: self.mw.col.decks.collapseBrowser(g[1]),
                not self.mw.col.decks.get(g[1]).get('browserCollapsed', False))
            item.type="deck"
            item.fullname = head + g[0]
            item.setIcon(0, QIcon(":/icons/deck.svg"))
            newhead = head + g[0]+"::"
            fillGroups(item, g[5], newhead)
            # item.setExpanded(bool(len(grps)<2))
    fillGroups(root, grps)


def modelTree(self, root):
    root = self.CallbackItem(root, _("Models"), None)
    root.setIcon(0, QIcon(":/icons/notetype.svg"))
    root.setExpanded(False)
    for m in sorted(self.col.models.all(), key=itemgetter("name")):
        mitem = self.CallbackItem(
            root, m['name'], lambda m=m: self.setFilter("note", m['name']))
        mitem.type="model"
        mitem.fullname = m['name']
        mitem.setIcon(0, QIcon(":/icons/notetype.svg"))

