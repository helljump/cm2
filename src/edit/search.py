#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

"""
Поиск во всех(выбраных) статьях
"""

from PyQt4 import QtCore, QtGui
import re
from PyQt4.QtCore import QThread
import itertools
from logging import debug, exception

class ReplaceTextCommand(QtGui.QUndoCommand):
    def __init__(self, parent, item, title, text, intro):
        QtGui.QUndoCommand.__init__(self, u"Пакетная замена текста")
        self.parent = parent
        self.item = item
        article = item.article
        self.new_title = title
        self.new_text = text
        self.new_intro = intro
        self.old_title = getattr(article, "title", None)
        self.old_text = getattr(article, "text", None)
        self.old_intro = getattr(article, "intro", None)
                        
    def undo(self):
        article = self.item.article
        if self.old_title is not None:
            article.title = self.old_title
            self.item.title = self.old_title
        if self.old_text is not None: article.text = self.old_text
        if self.old_intro is not None: article.intro = self.old_intro
        self.parent.itemChanged.emit(self.item, 0)
        
    def redo(self):
        article = self.item.article
        if self.new_title is not None:
            article.title = self.new_title
            self.item.title = self.new_title
        if self.new_text is not None: article.text = self.new_text
        if self.new_intro is not None: article.intro = self.new_intro
        self.parent.itemChanged.emit(self.item, 0)

class SearchThread(QThread):
    def __init__(self, item_iter, search, replace, useregexp, ignorecase, parent):
        QtCore.QThread.__init__(self, parent)
        self.item_iter = item_iter
        self.search = search
        self.replace = replace
        self.ignorecase = ignorecase
        self.useregexp = useregexp
        self.parent = parent
    
    def run(self):
        self.online = True
        try:
            params = re.S | re.M | re.U
            if self.ignorecase:
                params |= re.I
            if not self.useregexp:
                self.search = re.escape(self.search)
            find_str = re.compile(self.search, params)
            
            if self.replace:
                self.parent.undo_stack.beginMacro(u"Пакетная замена текста")
            
            for item in self.item_iter:
                article = item.article
                if not self.online:
                    break
                if self.replace == None:
                    if (find_str.search(article.text) 
                        or find_str.search(article.title)
                        or (hasattr(article, "intro") and find_str.search(article.intro))
                        ):
                        self.parent.emit(
                            QtCore.SIGNAL("add_item(QTreeWidgetItem*)"), item)
                else: #debug("replace mode")
                    
                    article_title = article_text = article_intro = None
                    
                    newtitle, changes1 = find_str.subn(self.replace, article.title)
                    if changes1 > 0:
                        article_title = newtitle
                    newtext, changes2 = find_str.subn(self.replace, article.text)
                    if changes2 > 0:
                        article_text = newtext
                    changes3 = 0
                    if hasattr(article, "intro"):
                        newintro, changes3 = find_str.subn(self.replace, article.intro)
                        if changes3 > 0:
                            article_intro = newintro
                            
                    if changes1 + changes2 + changes3 > 0:
                        self.parent.emit(
                            QtCore.SIGNAL("add_item(QTreeWidgetItem*)"), item)
                        #self.parent.parent.emit(
                        #    QtCore.SIGNAL("refresh(QTreeWidgetItem*,int)"), item, 0)
                        
                        #parent, item, title=None, text=None, intro=None
                        tree = self.parent.parent.treeWidget.tree
                        command = ReplaceTextCommand(tree, item,
                            article_title, article_text, article_intro)
                        self.parent.undo_stack.push(command)
                        
            if self.replace:
                self.parent.undo_stack.endMacro()
                
        except:
            exception("*** SearchThread crashed")
        self.parent.emit(QtCore.SIGNAL("stop_search()"))
        debug("searchthread stop")
    
    def stop(self):
        self.online = False
        
    #TODO отстрел треда призакрытии диалога

class SearchDialog(QtGui.QDialog):
    
    class MyListItem(QtGui.QListWidgetItem):
        def __init__(self, item, parent):
            QtGui.QListWidgetItem.__init__(self, item.title, parent)
            self.item = item
    
    def __init__(self, articles_iter, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Поиск и замена")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(480, 360)
        self.articles_iter = articles_iter
        self.parent = parent
        self.undo_stack = parent.undo_stack
        #debug(self.articles_iter)
        
        mainlayout = QtGui.QGridLayout(self)
        
        fieldslayout = QtGui.QGridLayout()
        fieldslayout.addWidget(QtGui.QLabel(u"Найти"), 0, 0)
        self.find_le = QtGui.QLineEdit(self)
        fieldslayout.addWidget(self.find_le, 0, 1)
        fieldslayout.addWidget(QtGui.QLabel(u"Заменить"), 1, 0)
        self.replace_le = QtGui.QLineEdit(self)
        fieldslayout.addWidget(self.replace_le, 1, 1)
        self.regexp_cb = QtGui.QCheckBox(u"Регулярное выражение", self)
        fieldslayout.addWidget(self.regexp_cb, 2, 0, 1, 2)        
        self.case_cb = QtGui.QCheckBox(u"Без учета регистра", self)
        fieldslayout.addWidget(self.case_cb, 3, 0, 1, 2)        
        mainlayout.addLayout(fieldslayout, 0, 0)

        buttonslayout = QtGui.QGridLayout()
        self.find_pb = QtGui.QPushButton(u"Найти", self)
        self.find_pb.clicked.connect(self.search)
        buttonslayout.addWidget(self.find_pb, 0, 0)
        self.replace_pb = QtGui.QPushButton(u"Заменить", self)
        self.replace_pb.clicked.connect(self.replace)
        buttonslayout.addWidget(self.replace_pb, 1, 0)
        self.close_pb = QtGui.QPushButton(u"Закрыть", self)
        self.close_pb.clicked.connect(lambda: self.hide())
        buttonslayout.addWidget(self.close_pb, 2, 0)
        mainlayout.addLayout(buttonslayout, 0, 1)
        
        self.listbox = QtGui.QListWidget(self)
        mainlayout.addWidget(self.listbox, 1, 0, 1, 2)
        
        #self.connect(self, QtCore.SIGNAL("add_item(QString)"), self.listbox, QtCore.SLOT("addItem(QStringQString)"))
        
        self.connect(self, QtCore.SIGNAL("add_item(QTreeWidgetItem*)"), self.add_result)
        self.connect(self, QtCore.SIGNAL("stop_search()"), self.stop_search)
        
        self.listbox.itemDoubleClicked.connect(self.open_tree_item)

        #self.connect(self, QtCore.SIGNAL("add_undocommand(QUndoCommand*)"), self.add_undocommand)

        #for item in self.articles_iter:
        #    self.listbox.addItem(item.title)

        #self.find_le.setText(u"ссылк")
        self.th = None
        
    """
    def add_undocommand(self, command):
        debug("add_undocommand %s", command)
        #egg = command.toPyObject()
        #command.test()
        #self.undo_stack.push(command)
        #pass
    """
    
    def open_tree_item(self, widget):
        #debug(widget.item)
        self.open_item = widget.item
        self.hide()
        
    def add_result(self, item):
        l = SearchDialog.MyListItem(item, self.listbox)
        self.listbox.addItem(l)

    def stop_search(self):
        if self.th: self.th.stop()
        self.close_pb.setText(u"Закрыть")
        self.close_pb.clicked.disconnect()
        self.close_pb.clicked.connect(lambda: self.hide())
        self.find_pb.setDisabled(False)
        self.replace_pb.setDisabled(False)

    def start_search(self):
        self.listbox.clear()
        self.close_pb.setText(u"Остановить")
        self.close_pb.clicked.disconnect()
        self.close_pb.clicked.connect(self.stop_search)
        self.find_pb.setDisabled(True)
        self.replace_pb.setDisabled(True)

    def search(self, replace=None):
        if replace == False:
            replace = None
        self.start_search()
        egg, self.articles_iter = itertools.tee(self.articles_iter, 2)
        find_str = unicode(self.find_le.text())
        regexp_b = self.regexp_cb.isChecked()
        case_b = self.case_cb.isChecked()
        self.th = SearchThread(egg, find_str, replace, regexp_b, case_b, self)
        self.th.start()
        
    def replace(self):
        replace_str = unicode(self.replace_le.text())
        #debug("[%s]",replace_str)
        self.search(replace_str)
