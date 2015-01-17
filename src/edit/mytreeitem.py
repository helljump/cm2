#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

from PyQt4 import QtGui, QtCore
import logging 

log = logging.getLogger(__name__)


class MyTreeItem(QtGui.QTreeWidgetItem):
        
    def __init__(self, article, parent):
        
        self.book_icon = QtGui.QIcon(":/ico/img/book.png")
        self.page_icon = QtGui.QIcon(":/ico/img/page.png")
        
        QtGui.QTreeWidgetItem.__init__(self, parent, QtGui.QTreeWidgetItem.UserType + 1)
        self.article = article
        if article and article.title:
            #self.setText(0, article.title)
            self.title = article.title        
        #self.set_icon()
        self.cached_children = -1
                
    @property
    def title(self):
        return self.article.title

    @title.setter
    def title(self, title): #@DuplicatedSignature
        self.article.title = title
        self.setText(0, title)
#        self.update_count()

#    def update_count(self):
    def data(self, c, r):
        if c == 0 and r == QtCore.Qt.DisplayRole:            
            return self.article.title
        elif c == 0 and r == QtCore.Qt.DecorationRole:
            if self.childCount() > 0:
                return self.book_icon
            else:
                return self.page_icon
        elif c == 1 and r == QtCore.Qt.DisplayRole:
#            if not hasattr(self,"cached_children"):
#                self.cached_children = -1
#            if self.cached_children == -1:
            self.cached_children = self.get_children_count()
            if self.cached_children == 0:            
                return "-"
            else:
                return "%i" % self.cached_children
        else:
            return None
    
    def clear_cache_children(self):
        self.cached_children = -1
    
    @property
    def text(self):
        return self.article.text
    @title.setter
    def text(self, text): #@DuplicatedSignature
        self.article.text = text
        #self.set_icon()
    
    @property
    def tags(self):
        return ", ".join(self.article.tags)
    @tags.setter
    def tags(self, tags): #@DuplicatedSignature
        tagsarray = [tag.strip() for tag in tags.split(",")]
        self.article.tags = tagsarray

    def get_children_count(self):
        def recurse(child):
            cnt = child.childCount()
            for i in range(cnt):
                cnt += recurse(child.child(i))
            return cnt
        return recurse(self)

    def __lt__(self, other):
        tree = self.treeWidget()
        if tree.sortColumn() == 1:
            return self.cached_children > other.cached_children
        else:
            return self.article.title > other.article.title
