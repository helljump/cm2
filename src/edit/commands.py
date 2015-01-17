#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

from PyQt4 import QtCore, QtGui
from mytreeitem import MyTreeItem
from utils.article import Article

import logging

log = logging.getLogger(__name__)

class EditArticleCommand(QtGui.QUndoCommand):
    def __init__(self, tree, item, changes):
        QtGui.QUndoCommand.__init__(self, u"Изменение статьи")
        self.tree = tree
        self.item = item
        self.new_data = changes
        self.old_data = {}
        if "title" in changes:
            self.old_data.update(title=item.title)
        if "text" in changes:
            self.old_data.update(text=item.article.text)
        if "tags" in changes:
            self.old_data.update(tags=item.tags)
        if "date" in changes:
            self.old_data.update(date=item.article.date)
        if "intro" in changes:
            if hasattr(item.article,"intro"):
                self.old_data.update(intro=item.article.intro)
            else:
                self.old_data.update(intro=None)

    def copy_from_data(self, changes):
        if "title" in changes:
            self.item.title = changes['title']
        if "text" in changes:
            self.item.article.text = changes['text']
        if "tags" in changes:
            self.item.tags = changes['tags']
        if "date" in changes:
            self.item.article.date = changes['date']
        if "intro" in changes:
            if changes['intro'] is None:
                del self.item.article.intro
            else:
                self.item.article.intro = changes['intro']

    def undo(self):
        self.copy_from_data(self.old_data)
        self.tree.itemChanged.emit(self.item, 0)
        #TypeError: QTreeWidget.itemChanged[QTreeWidgetItem, int].emit():
        #argument 1 has unexpected type 'MyTreeItem'

    def redo(self):
        self.copy_from_data(self.new_data)
        self.tree.itemChanged.emit(self.item, 0)

class RandomDateCommand(QtGui.QUndoCommand):
    def __init__(self, tree, item, new_date):
        QtGui.QUndoCommand.__init__(self, u"Случайная дата")
        self.item = item
        self.tree = tree
        self.old_date = item.article.date
        self.new_date = new_date

    def undo(self):
        self.item.article.date = self.old_date
        self.tree.itemChanged.emit(self.item, 0)

    def redo(self):
        self.item.article.date = self.new_date
        self.tree.itemChanged.emit(self.item, 0)

class AutoSplitCommand(QtGui.QUndoCommand):
    def __init__(self, tree, root, title=u"Автонарезка статей"):
        QtGui.QUndoCommand.__init__(self, title)
        self.tree_widget = tree
        self.root = root

    def undo(self):
        for item in self.items:
            parent = item.parent() or self.tree_widget.tree.invisibleRootItem()
            row = parent.indexOfChild(item)
            self.tree_widget.tree.expandItem(parent)
            spam = parent.takeChild(row) #@UnusedVariable
            # self.tree_widget.itemChanged.emit(parent, 1)

    def redo(self):
        self.items = self.tree_widget.set_tree(self.root)

class SplitTextCommand(QtGui.QUndoCommand):
    def __init__(self, tree, orig_item, orig_text, new_text, new_item):
        QtGui.QUndoCommand.__init__(self, u"Разделить на две")
        self.tree = tree
        self.orig_item = orig_item
        self.orig_text = orig_text
        self.new_text = new_text
        self.new_item = new_item
        self.parent = self.orig_item.parent() or self.tree.invisibleRootItem()
        self.row = self.parent.indexOfChild(self.orig_item) + 1

    def undo(self):
        self.orig_item.text = self.orig_text
        self.tree.expandItem(self.parent)
        spam = self.parent.takeChild(self.row) #@UnusedVariable
        self.tree.itemChanged.emit(self.parent, 1)

    def redo(self):
        self.orig_item.text = self.new_text
        self.parent.insertChild(self.row, self.new_item)
        self.tree.itemChanged.emit(self.parent, 1)

class InsertBlankArticleCommand(QtGui.QUndoCommand):
    def __init__(self, tree, parent, row):
        QtGui.QUndoCommand.__init__(self, u"Вставка пустой страницы")
        self.tree = tree
        self.parent = parent
        self.row = row
        self.new_item=MyTreeItem(Article(), None)

    def undo(self):
        self.tree.expandItem(self.parent)
        egg = self.parent.takeChild(self.row) #@UnusedVariable
        self.tree.itemChanged.emit(self.parent, 1)

    def redo(self):
        self.parent.insertChild(self.row, self.new_item)
        self.tree.itemChanged.emit(self.parent, 1)

class DeleteArticlesCommand(QtGui.QUndoCommand):
    class Row(object):
        def __init__(self, parent, row):
            self.parent = parent
            self.row = row
            self.item = None

    def __init__(self, tree):
        QtGui.QUndoCommand.__init__(self, u"Удаление страниц")
        self.tree = tree
        self.items = []
        self.fixed = False

    def append_item(self, parent, index):
        self.items.append(DeleteArticlesCommand.Row(parent, index))

    def undo(self):
        for row in sorted(self.items, cmp = lambda x,y: cmp(x.row, y.row)):
            row.parent.insertChild(row.row, row.item)
            self.tree.itemChanged.emit(row.parent, 1)

    def redo(self):
        self.tree.emit(QtCore.SIGNAL("itemsDeleted()"))
        if not self.fixed:
            self.fixed = True
            self.items.sort(cmp = lambda x,y: cmp(x.row, y.row), reverse=True)
        for row in self.items:
            self.tree.expandItem(row.parent)
            row.item = row.parent.takeChild(row.row)
            self.tree.itemChanged.emit(row.parent, 1)

class InternalDragCommand(QtGui.QUndoCommand):
    class Row(object):
        def __init__(self, source_item, source_row, target_item, target_row):
            assert target_item is not None
            assert source_item is not None
            self.source_item = source_item
            self.source_row = source_row
            self.target_item = target_item
            self.target_row = target_row
            self.item = None

    def __init__(self, tree):
        QtGui.QUndoCommand.__init__(self, u"Перемещение страниц")
        self.tree = tree
        self.items = []
        self.sorted = False

    def append_item(self, source_item, source_row, target_item, target_row):
        row = InternalDragCommand.Row(source_item, source_row, target_item, target_row)
        self.items.append(row)

    def fix(self):
        self.sorted = True
        self.items.sort(cmp = lambda x,y: cmp(x.source_row, y.source_row), reverse=True)

    def undo(self):
        normalized = sorted(self.items,
            cmp = lambda x,y: cmp(x.target_row, y.target_row), reverse=True)
        taken = []
        for row in normalized:
            self.tree.expandItem(row.target_item)
            egg = row.target_item.takeChild(row.target_row) #@UnusedVariable
            self.tree.itemChanged.emit(row.target_item, 1)
            taken.append(row)
#            print "undo take target row", row.target_row

        taken.sort(cmp = lambda x,y: cmp(x.source_row, y.source_row))
        while taken:
            row = taken.pop(0)
            self.tree.expandItem(row.source_item)
            row.source_item.insertChild(row.source_row, row.item)
            self.tree.itemChanged.emit(row.source_item, 1)
#            print "undo insert source row", row.source_row

    def redo(self):
        if not self.sorted:
            self.fix()
        taken = []
        for row in self.items:
            self.tree.expandItem(row.source_item)
            egg = row.source_item.takeChild(row.source_row)
            self.tree.itemChanged.emit(row.source_item, 1)
            if row.item is None:
                row.item = egg
#            print "redo take source row", row.source_row
            taken.append(row)
        while taken:
            row = taken.pop(0)
#            print "redo insert target row", row.target_row
            self.tree.expandItem(row.target_item)
            if row.target_row == -1:
#                print "addChild"
                row.target_item.addChild(row.item)
            else:
                egg = min(row.target_row, row.target_item.childCount())
                row.target_item.insertChild(egg, row.item)
                row.target_row = egg
            #self.tree.itemChanged.emit(row.item, 0)
            #self.tree.expandItem(row.target_item)
            self.tree.itemChanged.emit(row.target_item, 1)
