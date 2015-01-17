#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

#import psyco
#psyco.full()

from PyQt4 import QtCore, QtGui, Qsci
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtWebKit import QWebView, QWebSettings
import sys, re, os
import shelve
from edit.thesaurusdialog import ThesaurusDialog
from logging import debug, exception, warning
import icons  # @UnusedImport
import cPickle
import types
from utils import qthelpers
from utils.qthelpers import ToolBarWithPopup, MyProgressDialog, MyDateEdit, MyPath, MyFile
import random
from utils.article import Article
from utils.formlayout import fedit
import datetime, time
import traceback
from utils.tidy import do_truncate, html_tags_re, do_truncate_html, encode_html_entities
from utils.saxclean import clear_html
from utils.misc import get_dir_content
import itertools
from yazzy.yazzydialog import YazzyDialog
from autotags import AutotagsDialog
import Stemmer
from regist import RegisterDialog
from search import SearchDialog
import updater
from synothread import SynoThread
from finddialog import FindDialog
import spelldialog
from htmledit import HtmlEdit
from insertlinks import InsertLinksDialog
from statistics import ShowStatistics
import fastags
from lxml.html.clean import Cleaner
from lxml.etree import XMLSyntaxError
import anydbm
import unicheck
from utils.paths import pluginpath
import Queue
from spider.grab import SpiderDialog
import anchorwidget
import config_dialog
import threading

import pyphp  # @UnusedImport
import phpserialize  # @UnusedImport

import tesseract

import plugmanager

from commands import (EditArticleCommand, RandomDateCommand, AutoSplitCommand, SplitTextCommand,
                      InsertBlankArticleCommand, DeleteArticlesCommand, InternalDragCommand)

from mytreeitem import MyTreeItem

from export import cmsimple
from export import wpxml
from export import textdir
from export import rssfeed
from export import joomla
from export import dle8
from export import zebrumlite
from export import static
from export import wprpc
from export import livejournalcom
from export import bloggercom
from export import cm2xmlrpc

from utils.paths import CONFIGFILE, TMP_FILENAME, KEY_FILENAME


def print_tree(root):
    for item in root.children:
        print "%s(%i)" % (item.title, len(item.children))


def is_subitem(item, selected_items):
    while item:
        parent = item.parent()
        if parent in selected_items:
            #debug("is subitem")
            return True
        item = parent
    return False


class MyTreeWidget(QtGui.QTreeWidget):
    def __init__(self, parent, undo_stack):
        QtGui.QTreeWidget.__init__(self, parent)
        self.undo_stack = undo_stack
        self.nowritecommand = False
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)

        self.headerItem().setText(0, u'Заголовок')
        self.headerItem().setText(1, u"Стр.")
        #self.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        #self.header().setStretchLastSection(True)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_toolbar_menu)

        #self.setSortingEnabled(True)

    def show_toolbar_menu(self, p):
        menu = QtGui.QMenu(self)
        a = menu.addMenu(u"Перенести в раздел")
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            a.addAction("\"%s\"" % item.title, lambda i=item: self.move_item(i))
        menu.exec_(QtGui.QCursor.pos())

    def move_item(self, item):
        #debug("move to %s" % item.title)
        self.moveSelection(item, 0)

    def dropEvent(self, event):
        if event.source() == self:
            QtGui.QAbstractItemView.dropEvent(self, event)

    def dropMimeData(self, parent, row, data, action):
        if action == QtCore.Qt.MoveAction:
            return self.moveSelection(parent, row)
        return False

    def moveSelection(self, target_item, position):
        command = InternalDragCommand(self)
        selection = self.selectedItems()
        if target_item is None:
            target_item = self.invisibleRootItem()
        target_index = self.indexFromItem(target_item)
        if target_index in selection:
            return False
        target_row = self.model().index(position, 0, target_index).row()
        if target_row < 0:
            target_row = position
        for item in selection:
            if item.parent() is None:
                source_item = self.invisibleRootItem()
            else:
                source_item = item.parent()
            if not is_subitem(item, selection):
                source_row = self.indexFromItem(item).row()
                command.append_item(source_item, source_row, target_item, target_row)
        self.undo_stack.push(command)
        return True


class TagLineEdit(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.lineEdit = QtGui.QLineEdit(self)
        layout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.toolButton = QtGui.QToolButton(self)
        self.toolButton.setText("...")
        self.toolButton.setIcon(QtGui.QIcon(":/ico/img/tag_blue_edit.png"))
        self.toolButton.setAutoRaise(True)
        layout.addWidget(self.toolButton, 0, 1, 1, 1)
        self.textChanged = self.lineEdit.textChanged

    def text(self):
        return self.lineEdit.text()

    def setText(self, s):
        return self.lineEdit.setText(s)


class DirtyFlag(object):
    CLEAN = 0
    TITLE = 1
    TAGS = 2
    DATE = 4
    TEXT = 8
    INTRO = 16


class ArticlesTreeWidget(QtGui.QWidget):

    def __init__(self, parent, undo_stack, mainwindow):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)

        self.parent = parent
        self.mainwindow = mainwindow
        self.undo_stack = undo_stack
        #self.tree=QtGui.QTreeWidget(self)
        self.tree = MyTreeWidget(self, undo_stack)

        toolbar = ToolBarWithPopup(self, style=QtCore.Qt.ToolButtonIconOnly)
        toolbar.setObjectName("treewidgettoolbar")
        toolbar.addAction(QtGui.QIcon(":/ico/img/page_add.png"), u"Добавить страницы",
            self.insert_blank_page)
        toolbar.addAction(QtGui.QIcon(":/ico/img/page_delete.png"), u"Удалить страницы", self._delete_page)
        toolbar.addAction(QtGui.QIcon(":/ico/img/arrow_out.png"), u"Развернуть", self.tree.expandAll)
        toolbar.addAction(QtGui.QIcon(":/ico/img/arrow_in.png"), u"Свернуть", self.tree.collapseAll)
        toolbar.addAction(QtGui.QIcon(":/ico/img/asterisk_orange.png"), u"Выделить всё", self.tree.selectAll)

        egg = toolbar.addAction(QtGui.QIcon(":/ico/img/sort_ascending.png"), u"Сортировка")
        egg.setCheckable(True)
        #egg.setChecked(True)
        egg.triggered.connect(self.tree.setSortingEnabled)

        #layout.addWidget(toolbar, 0, 0, 1, 1)
        mainwindow.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.LeftToolBarArea), toolbar)

        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree.setAllColumnsShowFocus(True)
        # self.tree.setHeaderHidden(True)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setStyleSheet("selection-background-color: rgb(182,195,210);")
        layout.addWidget(self.tree, 0, 0, 1, 1)

        #delkey = QtGui.QShortcut(QtGui.QKeySequence("Delete"), self.tree,
        #    context=QtCore.Qt.WidgetShortcut )
        #delkey.activated.connect(self._delete_page)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self._delete_page()
        elif event.key() == QtCore.Qt.Key_Insert:
            self.insert_blank_page()

    def insert_blank_page(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            egg = selected_items[-1]
            parent = egg.parent() or self.tree.invisibleRootItem()
            row = parent.indexOfChild(egg) + 1
        else:
            parent = self.tree.invisibleRootItem()
            row = parent.childCount()

        command = InsertBlankArticleCommand(self.tree, parent, row)
        self.undo_stack.push(command)

    def _add_article(self, article):
        parent = self.tree.invisibleRootItem()
        self.new_item = MyTreeItem(article, parent)

    def _delete_page(self):
        items = self.tree.selectedItems()
        if items:
            rc = QtGui.QMessageBox.question(self, u"Удаление", u"Удалить выбранные страницы?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if rc == QtGui.QMessageBox.Yes:
                command = DeleteArticlesCommand(self.tree)

                for item in items:
                    parent = item.parent() or self.tree.invisibleRootItem()
                    index = parent.indexOfChild(item)
                    if not is_subitem(item, items):
                        command.append_item(parent, index)

                self.undo_stack.push(command)

                """
                for item in reversed(items):
                    parent=item.parent()
                    if not parent:
                        index=self.tree.indexOfTopLevelItem(item)
                        item.takeChildren()
                        self.tree.takeTopLevelItem(index)
                    else:
                        index=parent.indexOfChild(item)
                        item.takeChildren()
                        parent.takeChild(index)
                """

    def set_tree(self, articles_tree):
        self.setDisabled(True)

        def recurse(article, treeitem):
            global selected_item
            roots_bloody_roots = []
            for subitem in article.children:
                new_treeitem = MyTreeItem(subitem, treeitem)
                if hasattr(subitem, "params"):
                    selected = subitem.params.get("selected", False)
                    if selected:
                        self.tree.currentItemChanged.emit(new_treeitem, None)
                        self.tree.setCurrentItem(new_treeitem)
                        #new_treeitem.setSelected(selected)
                    new_treeitem.setExpanded(subitem.params.get("expanded", False))
                roots_bloody_roots.append(new_treeitem)
                recurse(subitem, new_treeitem)
            return roots_bloody_roots

        QtGui.qApp.processEvents()
        self.setDisabled(False)

        root = self.tree
        egg = self.tree.selectedItems()
        if egg:
            root = egg[0]

        rc = recurse(articles_tree, root)
        return rc

    def set_tree_withundo(self, root, title):
        command = AutoSplitCommand(self, root, title)
        self.undo_stack.push(command)

    def append_treeparams(self, item, article):
        params = article.params if hasattr(article, "params") else {}
        params.update(selected=item.isSelected(), expanded=item.isExpanded())
        article.params = params

    def datefix(self, d):
        if isinstance(d, QtCore.QDateTime):
            egg = d.toPyDateTime()
        elif isinstance(d, QtCore.QDate):
            egg = d.toPyDate()
        else:
            egg = d
        return egg

    def get_tree(self):
        def recurse(item):
            children = []
            for i in range(item.childCount()):
                child = item.child(i)
                #debug("get tree dt1 %s", child.article.date)
                egg = self.datefix(child.article.date)
                article = Article(child.title, child.article.text,
                    child.article.tags, egg)
                self.append_treeparams(child, article)
                if hasattr(child.article, "intro"):
                    #debug("has intro")
                    article.intro = child.article.intro
                if hasattr(child.article, "meta"):
                    article.meta = child.article.meta
                    #print article.meta
                article.children = recurse(child)
                children.append(article)
                QtGui.qApp.processEvents()
            return children

        root = Article()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            #debug("get tree dt2 %s", item.article.date)
            egg = self.datefix(item.article.date)
            article = Article(item.title, item.article.text, item.article.tags, egg)
            self.append_treeparams(item, article)
            if hasattr(item.article, "intro"):
                article.intro = item.article.intro
            if hasattr(item.article, "meta"):
                article.meta = item.article.meta
            article.children = recurse(item)
            root.add_child(article)
            QtGui.qApp.processEvents()

        return root


class ArticlesTreeDialog(QtGui.QMainWindow):
    dirty_flag = DirtyFlag.CLEAN
    window_title_template = u"Редактор статей(%s)"
    #AUTOFILE = "autoload.prt"

    add_article = pyqtSignal(Article)

    def __init__(self, autofile):
        QtGui.QMainWindow.__init__(self)

        #self.setWindowFlags(QtCore.Qt.SplashScreen)

        self.set_current_filename()
        #self.setWindowFlags(QtCore.Qt.Window)
        self.resize(800, 600)

        self.centralwidget = QtGui.QWidget(self)

        self.q = 'download'

        layout = QtGui.QGridLayout(self.centralwidget)
        self.undo_stack = QtGui.QUndoStack(self)
        self.undo_stack.setUndoLimit(10)
        self.undo_stack.indexChanged.connect(self.undoredobuttons_enabler)

        self.menubar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menubar)

        """
        try:
            spam = open(KEY_FILENAME, "rb").read().decode('base64')
            p = cPickle.loads(spam)
            self.w = b = p["key"]
            del p["key"]
            self.q = a = qthelpers.gen(p)
        except:
            exception('oops')
            self.w = 'upload'
        """
        
        plugmanager.collect()

        self._create_menu()

        toolbar = ToolBarWithPopup(self, style=QtCore.Qt.ToolButtonIconOnly)
        toolbar.setObjectName("maintoolbar")
        toolbar.addAction(QtGui.QIcon(":/ico32/img/page_white.png"), u"Новый", self.all_clear)
        toolbar.addAction(QtGui.QIcon(":/ico32/img/folder.png"), u"Открыть", self.load_prt)
        toolbar.addAction(QtGui.QIcon(":/ico32/img/disk.png"), u"Сохранить", self.save_prt)
        self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), toolbar)

        toolbar2 = ToolBarWithPopup(self, style=QtCore.Qt.ToolButtonIconOnly)
        toolbar2.setObjectName("maintoolbar2")
        self.undo_action = toolbar2.addAction(QtGui.QIcon(":/ico32/img/arrow_undo.png"),
            u"Отменить операцию", self.undo_stack.undo)
        self.redo_action = toolbar2.addAction(QtGui.QIcon(":/ico32/img/arrow_redo.png"),
            u"Применить операцию", self.undo_stack.redo)
        self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), toolbar2)

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)

        self.treeWidget = ArticlesTreeWidget(self.splitter, self.undo_stack, self)

        self.add_article.connect(self.treeWidget._add_article)

        self.frame = QtGui.QFrame(self.splitter)
        layout2 = QtGui.QGridLayout(self.frame)
        layout2.setMargin(0)

        layout2.addWidget(QtGui.QLabel(u"Заголовок:", self.frame), 0, 0, 1, 1)
        self.title_le = QtGui.QLineEdit(self.frame)
        layout2.addWidget(self.title_le, 0, 1, 1, 1)

        layout2.addWidget(QtGui.QLabel(u"Метки:", self.frame), 1, 0, 1, 1)
        self.tags_le = TagLineEdit(self.frame)
        layout2.addWidget(self.tags_le, 1, 1, 1, 1)
        self.tags_le.toolButton.clicked.connect(self.generate_tags)

        layout2.addWidget(QtGui.QLabel(u"Публикации:", self.frame), 2, 0, 1, 1)
        self.datepub_de = MyDateEdit(parent=self.frame)
        self.datepub_de.setMaximumWidth(180)
        layout2.addWidget(self.datepub_de, 2, 1, 1, 1)

        self.article_toolbar = toolbar = ToolBarWithPopup(self, style=QtCore.Qt.ToolButtonIconOnly)

        toolbar.addAction(QtGui.QIcon(":/ico/img/accept.png"),
            u"Применить", self.accept_item)
        toolbar.addSeparator()

        a1 = QtGui.QAction(QtGui.QIcon(":/ico/img/text_align_left.png"), u"Перевод строк", self)
        a1.setCheckable(True)
        a1.setChecked(True)
        a1.triggered.connect(self._set_wrap_text)
        toolbar.addAction(a1)

        toolbar.addAction(QtGui.QIcon(":/ico/img/layout_content.png"),
            u"Добавить вступление", self._add_intro_to_current_article)
        toolbar.addAction(QtGui.QIcon(":/ico/img/arrow_divide.png"),
            u"Автонарезка статей", self._auto_splitter)
        toolbar.addAction(QtGui.QIcon(":/ico/img/application_split.png"),
            u"Разделить на две", self.split_article)

        #add popup button
        menu = QtGui.QMenu("HTML Tags", self)
        menu.setTearOffEnabled(True)
        for row in fastags.tags:
            if not row:
                menu.addSeparator()
                continue
            k = row[0]
            v = row[1]
            menu.addAction(k, lambda v=v: self.pasteInFocusEdit(v))
        self.articlemenu.addMenu(menu)

        #if self.w == self.q:
        plugs = plugmanager.getArticlePlugins()
        #else:
        #    plugs = []
        
        if plugs:
            self.articlemenu.addSeparator()
            for v in plugs:
                self.articlemenu.addAction(unicode(v[1], "utf-8"), lambda f=v[0]:
                    self.article_plugin_template(f.run), QtGui.QKeySequence(v[2]))

        tb1 = QtGui.QToolButton(self)
        tb1.setIcon(QtGui.QIcon(":/ico/img/tag.png"))
        tb1.setText("HTML Tags")
        tb1.setMenu(menu)
        tb1.setPopupMode(QtGui.QToolButton.InstantPopup)
        toolbar.addWidget(tb1)

        toolbar.addAction(QtGui.QIcon(":/ico/img/spellcheck.png"),
            u"Проверка орфографии", self.spell_check)

        toolbar.addAction(QtGui.QIcon(":/ico/img/draw_calligraphic.png"),
            u"Рерайтер", self.rewriter)

        toolbar.addAction(QtGui.QIcon(":/ico/img/google_web_elements.png"),
            u"Предпросмотр", self.preview)

        # layout2.addWidget(toolbar, 3, 0, 1, 2)
        toolbar.setObjectName("article_toolbar")
        self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), toolbar)

        toolbar3 = ToolBarWithPopup(self, style=QtCore.Qt.ToolButtonIconOnly)
        toolbar3.setObjectName("maintoolbar3")
        toolbar3.addAction(QtGui.QIcon(":/ico32/img/chart_line.png"), u"Статистика", self.calculate_statistic)
        toolbar3.addAction(QtGui.QIcon(":/ico32/img/hammer.png"), u"Настройки", self.show_config_dialog)
        toolbar3.addAction(QtGui.QIcon(":/ico32/img/cm2.png"), u"О программе", self.about)

        self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), toolbar3)

        self.stat_curpos = QtGui.QLabel(self)
        self.stat_selected = QtGui.QLabel(self)

        self.splitter2 = QtGui.QSplitter(self.frame)
        self.splitter2.setOrientation(QtCore.Qt.Vertical)
        self.textEdit = HtmlEdit(self.splitter2)
        self.textEdit.cursorPositionChanged.connect(self.set_stat_curpos)
        self.introTextEdit = HtmlEdit(self.splitter2)
        self.introTextEdit.cursorPositionChanged.connect(self.set_stat_curpos)
        layout2.addWidget(self.splitter2, 4, 0, 1, 2)
        self.splitter2.setStretchFactor(3, 1)
        self.splitter2.setSizes([500, 200])

        layout.addWidget(self.splitter, 0, 0)
        self.splitter.setSizes([200, 500])

        self.setCentralWidget(self.centralwidget)

        self.statusbar = QtGui.QStatusBar(self)
        self.statprogress = QtGui.QProgressBar(self)
        self.statprogress.setFixedSize(200, 16)
        self.statusbar.insertPermanentWidget(0, self.stat_selected, 0)
        self.statusbar.insertPermanentWidget(1, self.stat_curpos, 0)
        self.statusbar.addPermanentWidget(self.statprogress, 0)
        self.setStatusBar(self.statusbar)
        self.current_edit_item = None

        self.undoredobuttons_enabler()
        self.undoredo_view(self, self.undo_stack)

        dock = QtGui.QDockWidget(u"Анкоры", self)
        dock.setObjectName("anchor_view_2")
        self.anchor_view = egg = anchorwidget.AnchorWidget(dock)
        dock.setWidget(egg)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
        self.viewmenu.addAction(dock.toggleViewAction())

        self.current_load_path = "."
        self.current_save_path = "."

        # self.load_settings()

        try:

            self.exportmenu.addAction(u"WordPress XML файл", self.export_wpxml_file)

            #if self.w != self.q:
            #    raise Exception()
            #updater.update(p, self)

            self.exportmenu.addAction(u"CMS Simple", self.export_cmsimple_file)
            self.exportmenu.addAction(u"WordPress XML-RPC(WP/metaWeblog)", self.export_wprpc_file)
            self.exportmenu.addAction(u"Joomla 1.5", self.export_joomla_file)
            self.exportmenu.addAction(u"Datalife Engine 8", self.export_dle_file)
            self.exportmenu.addAction(u"Zebrum Lite", self.export_zebrumlite_file)
            self.exportmenu.addAction(u"Статичный сайт", self.export_static_site)
            self.exportmenu.addAction(u"Livejournal.com", self.export_livejournalcom)
            self.exportmenu.addAction(u"Blogger.com", self.export_bloggercom)
            self.exportmenu.addAction(u"Content Monster 2 XML-PRC", self.export_cm2xmlrpc)

            plugs = plugmanager.getExportPlugins()
            if plugs:
                self.exportmenu.addSeparator()
                for v in plugs:
                    self.exportmenu.addAction(unicode(v[1], "utf-8"), lambda f=v[0]:
                        self.export_plugin_template(f.run), QtGui.QKeySequence(v[2]))

        except:
            exception("*** huynyas ***")
            self.treeWidget.get_tree = lambda: None

        self.treeWidget.tree.itemSelectionChanged.connect(self.recalc_selected)
        self.treeWidget.tree.currentItemChanged.connect(self.selection_changed)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemsDeleted()"), self.items_deleted)
        self.connect(self.treeWidget, QtCore.SIGNAL("tmp_saved()"),
            lambda: self.sbmessage(u"Сохранён во временный файл"))
        self.connect(self.treeWidget, QtCore.SIGNAL("add_page()"),
            lambda: self.title_le.setFocus())

        self.title_le.textChanged.connect(lambda: self.set_dirty(DirtyFlag.TITLE))
        self.tags_le.textChanged.connect(lambda: self.set_dirty(DirtyFlag.TAGS))
        self.datepub_de.dateChanged.connect(lambda: self.set_dirty(DirtyFlag.DATE))
        self.textEdit.modificationChanged.connect(lambda: self.set_dirty(DirtyFlag.TEXT))
        self.introTextEdit.modificationChanged.connect(
            lambda: self.set_dirty(DirtyFlag.INTRO))

        self._tess = None

        self.errmsg = QtGui.QErrorMessage(self)
        self.errmsg.setModal(True)

        self.connect(self, QtCore.SIGNAL("refresh(QTreeWidgetItem*,int)"),
            self.treeWidget.tree,
            QtCore.SIGNAL("itemChanged(QTreeWidgetItem*,int)"))

        self.treeWidget.tree.itemChanged.connect(self.reload_item)

        #find_sk = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        #find_sk.activated.connect(self.find_in_text)

        self.load_settings()

        self.autoload(autofile)

        self.config_dialog = config_dialog.ConfigDialog(self)

        self.startTimer(1000 * 60 * self.config_dialog.config.get("autosave_timeout", 60))
        self.tmpsaving = threading.Event()

        if self.show_about:
            self.show()
            self.about()

    @property
    def tess(self):
        if not self._tess:
            self._tess = tesseract.Tesseract()
        return self._tess

    @property
    def connect_timeout(self):
        return self.config_dialog.config["connect_timeout"]

    c = types.CodeType(0, 0, 0, 0, '\x04\x71\x00\x00', (), (), (), '', '', 1, '')

    def pasteInFocusEdit(self, v):
        if self.current_edit_item is None:
            return
        if self.textEdit.hasFocus():
            widget = self.textEdit
        elif self.introTextEdit.hasFocus():
            widget = self.introTextEdit
        elif self.title_le.hasFocus():
            widget = self.title_le
        else:
            return
        params = {"text": widget.selectedText()}
        widget.removeSelectedText()
        widget.insert(v % params)

    def show_config_dialog(self):
        self.config_dialog.exec_()

    def open_url(self, url):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def reload_item(self, item, col=0):
        #self.treeWidget.tree.setCurrentItem(item)
        if self.treeWidget.tree.currentItem() is item:
            self.widget_to_fields(item)
            self.dirty_flag = DirtyFlag.CLEAN

        #        print "changed %s" % item
        #        if col==1: #counter
        #            item.update_count()

    def undoredo_view(self, parent, stack):
        dock = QtGui.QDockWidget(u"История операций", parent)
        dock.setObjectName("undoredo_view")
        #dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable
        #    | QtGui.QDockWidget.DockWidgetFloatable)
        undo_view = QtGui.QUndoView(stack, dock)
        dock.setWidget(undo_view)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
        self.viewmenu.addAction(dock.toggleViewAction())

    def undoredobuttons_enabler(self, index=0):
        #item=self.treeWidget.tree.itemFromIndex(self.current_edit_item)
        #self.reload_item(item)
        self.undo_action.setEnabled(self.undo_stack.canUndo())
        self.redo_action.setEnabled(self.undo_stack.canRedo())
        self.dirty_flag = DirtyFlag.CLEAN

    def save_tmp(self):
        if self.tmpsaving.is_set():
            return
        self.tmpsaving.set()
        self.sbmessage(u"Сохраняем временный файл..")
        self.treeWidget.setDisabled(True)
        root = self.treeWidget.get_tree()
        try:
            #cPickle.dump(root, open(TMP_FILENAME, "wb"), cPickle.HIGHEST_PROTOCOL)
            if os.path.isfile(TMP_FILENAME):
                os.unlink(TMP_FILENAME)
            fout = shelve.open(TMP_FILENAME, protocol=cPickle.HIGHEST_PROTOCOL)
            fout["root"] = root
            fout["anchors"] = self.anchor_view.get_list()
            fout.close()
        finally:
            self.treeWidget.setDisabled(False)
            self.tmpsaving.clear()
        self.sbmessage(u"Сохранён")

    def calculate_statistic(self):
        self._save_current_item()
        arts = self.get_selected_items(overall=True)
        try:
            ShowStatistics(arts, self)
        except Exception, err:
            self.errmsg.setWindowTitle(u"Ошибка обработки")
            self.errmsg.showMessage(str(err))

    def _auto_splitter(self):
        datalist = [
            (None, u"<b></b>"),
            (u"Статей в категории(минимум)", 5),
            (u"Статей в категории(максимум)", 15),
            (u"Регулярное выражение для разбивки", "(\.+)"),
            (u"Длина статьи, не более(знаков)", 1000),
            (u"Длина заголовка", 50),
            (u"Минимальная длина(знаков)", 3)
        ]
        rc = fedit(datalist, title=u"Автонарезка", parent=self)
        if not rc:
            return

        (articles_min, articles_max, regex, article_length, title_length, minlen_except) = rc

        #self._save_current_item()
        pd = MyProgressDialog(u"Автонарезка", u"Формирование списка",
            u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()

        old_text = unicode(self.textEdit.text())
        splitted = re.split(regex, old_text)
        pd.setRange(0, len(splitted))

        #print len(splitted[-1])

        debug("splitted for processing %i", len(splitted))

        length_current = 0
        frags = []
        articles = []

        testoverspaces = re.compile("[ \t\f\v\n]{1,}", re.M | re.S | re.I | re.U)
        delpunkt = re.compile("^[\.\s,!\?\:]{1,}")

        for i in range(len(splitted)):
            frag = splitted[i]
            frags.append(frag)
            length_current += len(frag)
            next_pred_len = len(splitted[i + 1]) if i < len(splitted) - 1 else minlen_except + 1

            if length_current > article_length and next_pred_len > minlen_except:
                text = "".join(frags)
                #text = text.strip(".").strip()
                text = delpunkt.sub("", text)
                title = do_truncate_html(text, length=title_length, end="")
                title = testoverspaces.sub(" ", title)
                #title = title.strip(".").strip()
                art = Article(title, text)
                articles.append(art)
                length_current = 0
                frags = []
                pd.setLabelText(u"Добавили страницу: %s" % title)
                debug("make %s", title)
            pd.setValue(pd.value() + 1)
            QtGui.qApp.processEvents()
        else:
            text = "".join(frags)
            if len(text) > 0:
                text = delpunkt.sub("", text)
                title = do_truncate_html(text, length=title_length, end="")
                art = Article(title, text)
                articles.append(art)

        debug("articles generated %i", len(articles))

        pd.setRange(0, len(articles))
        root = Article()
        cat_max = 0
        cat_cur = cat_max + 1
        for article in articles:
            if cat_cur > cat_max:
                cat_max = random.randint(articles_min, articles_max)
                cat_cur = 0
                last_cat = Article(article.title)
                root.add_child(last_cat)
                pd.setLabelText(u"Добавили категорию: %s" % last_cat.title)
            last_cat.add_child(article)
            cat_cur += 1
            pd.setValue(pd.value() + 1)
            QtGui.qApp.processEvents()
        pd.close()

        debug("categories generated %i", len(root.children))

        command = AutoSplitCommand(self.treeWidget, root)
        self.undo_stack.push(command)

        #self._reload_current_item()


    def find_in_text(self):
        dlg = FindDialog(self, self.textEdit, self.introTextEdit)
        dlg.exec_()

    def timerEvent(self, event):
        self.save_tmp()

    def _add_intro_to_current_article(self):
        if self.textEdit.hasSelectedText():
            selected_text = unicode(self.textEdit.selectedText())
            self.introTextEdit.setText(selected_text)
        self.introTextEdit.setVisible(True)

    def _set_wrap_text(self, val):
        if val:
            self.textEdit.setWrapMode(Qsci.QsciScintilla.WrapWord)
            self.introTextEdit.setWrapMode(Qsci.QsciScintilla.WrapWord)
        else:
            self.textEdit.setWrapMode(Qsci.QsciScintilla.WrapNone)
            self.introTextEdit.setWrapMode(Qsci.QsciScintilla.WrapNone)

    def generate_tags(self):
        debug("generate tags")
        comment = u"""Генератор меток на базе стеммера"""

        langs = ["russian", ("russian", u"Русский"),
            ("english", u"Английский"), ("german", u"Немецкий")]
        #print Stemmer.algorithms()

        ### read config
        settings = shelve.open(CONFIGFILE)
        config = settings.get("FastTagsDialog", {})
        current_lang = config.get("current_lang", "russian")
        langs[0] = current_lang
        minwordsize = config.get("minwordsize", 5)
        minenterscount = config.get("minenterscount", 4)
        settings.close()

        datalist = [
            (u"Язык текста:", langs),
            (u"Минимальный размер слова:", minwordsize),
            (u"Минимальное количество вхождений:", minenterscount)
        ]

        rc = fedit(datalist, title=u"Сгенерировать метки", parent=self, comment=comment)
        if not rc:
            return False

        (src_lang, min_len, min_count) = rc

        ### write config
        settings = shelve.open(CONFIGFILE)
        self.params = {"current_lang": src_lang, "minwordsize": min_len,
                       "minenterscount": min_count}
        settings["FastTagsDialog"] = self.params
        settings.close()

        stemmer = Stemmer.Stemmer(src_lang)

        ws = html_tags_re.sub("", unicode(self.textEdit.text()))
        ws = ws.lower()
        ws = re.split("(?misu)\W", ws)

        egg = {}
        for w in stemmer.stemWords(ws):
            if len(w) < min_len:
                continue
            if egg.has_key(w):
                egg[w] += 1
            else:
                egg[w] = 1

        spam = []
        for w, v in egg.items():
            #print w, v
            if v > min_count:
                spam.append(w)

        egg = ", ".join(spam)
        self.tags_le.setText(egg)
        #print egg

        return True

    def items_deleted(self):
        debug("items_deleted")
        self.clear_fields()

    def set_dirty(self, flag):
        if not self.current_edit_item:
            return

        self.dirty_flag = self.dirty_flag | flag

        """
        if self.dirty_flag&DirtyFlag.TITLE: #realtime title edit
            item=self.treeWidget.tree.itemFromIndex(self.current_edit_item)
            item.title=unicode(self.title_le.text())
        """

    def accept_item(self):
        curr = self.treeWidget.tree.itemFromIndex(self.current_edit_item)
        self.fields_to_widget(curr)

    def fields_to_widget(self, prev):
        if self.dirty_flag == DirtyFlag.CLEAN:
            return

        changes = {}
        if self.dirty_flag & DirtyFlag.TITLE:
            #prev.title=unicode(self.title_le.text())
            changes['title'] = unicode(self.title_le.text())
        if self.dirty_flag & DirtyFlag.TAGS:
            #prev.tags=unicode(self.tags_le.text())
            changes['tags'] = unicode(self.tags_le.text())
        if self.dirty_flag & DirtyFlag.TEXT:
            #prev.text=unicode(self.textEdit.text())
            changes['text'] = unicode(self.textEdit.text())
        if self.dirty_flag & DirtyFlag.INTRO:
            egg = self.introTextEdit.text()
            if egg:
                #prev.article.intro=unicode(egg)
                changes['intro'] = unicode(egg)
            else:
                del prev.article.intro
        if self.dirty_flag & DirtyFlag.DATE:
            #prev.article.date=self.datepub_de.date()
            changes['date'] = self.datepub_de.dateTime()

        if changes:
            command = EditArticleCommand(self.treeWidget.tree, prev, changes)
            self.undo_stack.push(command)

        self.dirty_flag = DirtyFlag.CLEAN

    def widget_to_fields(self, curr):
        """чтение полей из объекта в гуй"""

        #debug("%s" % self.treeWidget.tree.indexFromItem(curr).row())
        self.dirty_flag = DirtyFlag.CLEAN
        self.current_edit_item = self.treeWidget.tree.indexFromItem(curr)
        self.title_le.setText(curr.article.title)
        self.tags_le.setText(curr.tags)
        self.textEdit.clear()

        #print curr.article.text.encode("UTF-8")
        self.textEdit.setText(curr.article.text)

        """
        File "D:\work\cm2\src\edit\gui.py", line 559, in reload_item
            self.widget_to_fields(item)
          File "D:\work\cm2\src\edit\gui.py", line 838, in widget_to_fields
            self.datepub_de.setDateTime(curr.article.date)
        TypeError: QDateTimeEdit.setDateTime(QDateTime): argument 1 has unexpected type 'QDate'
        """
        #debug(type(curr.article.date))
        self.datepub_de.setDateTime(curr.article.date)
        #debug("w_to_f %s", curr.article.date)
        if hasattr(curr.article, "intro"):
            #debug("has intro")
            self.introTextEdit.setVisible(True)
            self.introTextEdit.clear()
            self.introTextEdit.setText(curr.article.intro)
        else:
            self.introTextEdit.setVisible(False)
            self.introTextEdit.clear()
            self.introTextEdit.setText("")
            #sizes = self.introTextEdit.sizes()
            #sizes[-1] = 0
            #self.splitter2.setSizes(sizes)

    def selected_amount(self):
        cache = []

        def recurse(items):
            for item in items:
                if item not in cache:
                    cache.append(item)
                if not item.isExpanded():
                    recurse([item.child(i) for i in range(item.childCount())])

        recurse(self.treeWidget.tree.selectedItems())
        return len(cache)

    def recalc_selected(self):
        self.stat_selected.setText(u"Выбрано статей: %i" % self.selected_amount())

    def selection_changed(self, curr, prev):
        #debug("selection_changed")
        if prev:
            self.fields_to_widget(prev)
        #            prev.update_count()
        if curr:
            self.widget_to_fields(curr)
            self.frame.setEnabled(True)
            self.article_toolbar.setEnabled(True)
        #            curr.update_count()
        else:
            self.clear_fields()
        self.dirty_flag = DirtyFlag.CLEAN
        return

    def clear_fields(self):
        self.current_edit_item = None
        self.title_le.setText(u"")
        self.tags_le.setText(u"")
        self.textEdit.setText(u"")
        self.introTextEdit.setText(u"")
        self.datepub_de.setDateTime(QtCore.QDateTime.currentDateTime())

        self.frame.setDisabled(True)
        self.article_toolbar.setDisabled(True)

    def set_current_filename(self, fname=None):
        lenlimit = 50
        if fname:
            if type(fname) != u"":
                fname = unicode(fname)
            egg = fname if len(fname) < lenlimit else "..%s" % fname[-lenlimit:]
            self.setWindowTitle(self.window_title_template % egg)
            self.filename = fname
        else:
            self.setWindowTitle(self.window_title_template % u"Без имени")
            if hasattr(self, "filename"):
                del self.filename

    def autoload(self, autofile):
        if os.path.isfile(autofile):
            finp = shelve.open(autofile, protocol=cPickle.HIGHEST_PROTOCOL)
            root = finp["root"]
            if finp.has_key("anchors"):
                self.anchor_view.set_list(finp["anchors"])
            else:
                self.anchor_view.clear()
            finp.close()
            self.treeWidget.set_tree_withundo(root, title=u"Автозагрузка")
            self.set_current_filename(autofile)

    def load_settings(self):
        self.frame.setDisabled(True)
        self.article_toolbar.setDisabled(True)

        settings = shelve.open(CONFIGFILE)
        config = settings.get("ArticlesTreeDialog", {})

        if "state" in config:
            self.restoreState(config["state"])
        if "geometry" in config:
            self.restoreGeometry(config["geometry"])
        if "splittersize" in config:
            self.splitter.setSizes(config["splittersize"])

        if "paths" in config:
            (self.current_load_path, self.current_save_path) = config["paths"]

        old_ver = settings.get("current_version", "0")
        new_ver = updater.get_version()
        self.show_about = old_ver != new_ver
        #debug("show_about o:%s n:%s show:%s", old_ver, new_ver, self.show_about)
        settings["current_version"] = new_ver

        settings.close()

    def save_prt_as(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, u"Сохранить...",
            self.current_save_path, "Promidol TreeText file (*.prt)")
        if fileName == "":
            return
        self.filename = unicode(fileName)
        self.current_save_path = os.path.split(self.filename)[0]
        self.save_prt()

    def test_saved_prt(self, fname):
        fname = fname.encode("mbcs")
        try:
            fout = shelve.open(fname, protocol=cPickle.HIGHEST_PROTOCOL)
        except anydbm.error:
            debug("test_saved_prt: pickle type")
            os.remove(fname)
            fout = shelve.open(fname, protocol=cPickle.HIGHEST_PROTOCOL)
        return fout

    def save_prt(self, tmpfile=False):
        if not hasattr(self, "filename"):
            self.save_prt_as()
            return
        else:
            fileName = self.filename
        try:
            self.set_current_filename(fileName)
            fileName = unicode(fileName)
            if self.current_edit_item:
                item = self.treeWidget.tree.itemFromIndex(self.current_edit_item)
                self.fields_to_widget(item)
            self.sbmessage(u"Формирование дерева")
            root = self.treeWidget.get_tree()
            #if self.w != self.q:
            #    exec self.c
            assert root is not None
            self.sbmessage(u"Открытие файла")
            fout = self.test_saved_prt(fileName)
            fout["root"] = root
            fout["anchors"] = self.anchor_view.get_list()
            #print len(fout["anchors"])
            fout.close()
            #cPickle.dump(root, open(fileName, "wb"), cPickle.HIGHEST_PROTOCOL)
            self.sbmessage(u"Файл сохранён")
        except Exception:
            self.errmsg.setWindowTitle(u"Ошибка записи")
            self.errmsg.showMessage(traceback.format_exc())

    def set_stat_curpos(self, line, pos):
        self.stat_curpos.setText(u"Позиция %i : %i" % (line, pos))

    def sbmessage(self, message, timeout=1000):
        self.statusbar.showMessage(message, timeout)

    def load_prt(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u"Открыть...", self.current_load_path,
            "Promidol TreeText file (*.prt)")
        if fileName:
            fileName = unicode(fileName)
            self.current_load_path = os.path.split(fileName)[0]
            try:
                finp = shelve.open(fileName.encode("mbcs"), protocol=cPickle.HIGHEST_PROTOCOL)
                root = finp["root"]
                if finp.has_key("anchors"):
                    self.anchor_view.set_list(finp["anchors"])
                else:
                    self.anchor_view.clear()
                finp.close()
                # self.treeWidget.set_tree(root)
                self.treeWidget.set_tree_withundo(root, title=u"Открытие файла")
                self.set_current_filename(fileName)
                self.sbmessage(u"Прочитан")
            except anydbm.error:
                root = cPickle.load(open(fileName.encode("mbcs"), "rb"))
                # self.treeWidget.set_tree(root)
                self.treeWidget.set_tree_withundo(root, title=u"Открытие файла")
                self.set_current_filename(fileName)
                self.sbmessage(u"Прочитан")
            except Exception:
                self.errmsg.setWindowTitle(u"Ошибка чтения")
                self.errmsg.showMessage(traceback.format_exc())

    def export_cm2xmlrpc(self):
        self.export_template(cm2xmlrpc)

    def export_bloggercom(self):
        self.export_template(bloggercom)

    def export_livejournalcom(self):
        self.export_template(livejournalcom)

    def article_plugin_template(self, articlefunction):
        if not self.current_edit_item:
            return
        title = unicode(self.title_le.text())
        text = unicode(self.textEdit.text())
        intro = unicode(self.introTextEdit.text())
        tags = unicode(self.tags_le.text())
        _date = self.datepub_de.dateTime().toPyDateTime()
        params = {"title": title,
                  "text": text,
                  "intro": intro,
                  "tags": tags,
                  "date": _date
        }
        try:
            rc = articlefunction(params, self)
            if "title" in rc:
                self.title_le.setText(rc["title"])
            if "text" in rc:
                self.textEdit.setText(rc["text"])
            if "intro" in rc:
                self.introTextEdit.setText(rc["intro"])
                self.introTextEdit.setVisible(True)
            if "tags" in rc:
                self.tags_le.setText(rc["tags"])
            if "date" in rc:
                egg = rc["date"]
                self.datepub_de.setDateTime(QtCore.QDateTime(egg.year, egg.month, egg.day,
                    egg.hour, egg.minute, egg.second))
        except Exception:
            self.errmsg.setWindowTitle(u"Ошибка в плагине")
            self.errmsg.showMessage(traceback.format_exc())

    def export_plugin_template(self, exportfunction):
        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setFixedWidth(320)
        pd.show()
        self._save_current_item()
        root = self.treeWidget.get_tree()
        pd.close()
        debug("let's export")
        try:
            exportfunction(root, parent=self)
        except Exception:
            self.errmsg.setWindowTitle(u"Ошибка в плагине")
            self.errmsg.showMessage(traceback.format_exc())

    def process_plugin_template(self, processfunction):
        self._save_current_item()
        arts = self.get_selected_items()
        try:
            processfunction(arts, self)
        except Exception:
            self.errmsg.setWindowTitle(u"Ошибка обработки")
            self.errmsg.showMessage(traceback.format_exc())
        self._reload_current_item()

    def import_plugin_template(self, importfunction):
        self._save_current_item()
        try:
            rc = importfunction(self)
        except Exception:
            self.errmsg.setWindowTitle(u"Ошибка в плагине")
            self.errmsg.showMessage(traceback.format_exc())
        else:
            if rc:
                self.treeWidget.set_tree_withundo(rc, title=u"Импорт")

    def export_template(self, exportmodule):
        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setFixedWidth(320)
        pd.show()
        self._save_current_item()
        root = self.treeWidget.get_tree()
        th = exportmodule.Export(root, progressdialog=pd, parent=self)
        if not th.config():
            pd.close()
            return
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()
        if hasattr(th, "error"):
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)

    def export_wprpc_file(self):
        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setFixedWidth(320)
        pd.show()
        self._save_current_item()
        root = self.treeWidget.get_tree()
        th = wprpc.Export(root, progressdialog=pd, parent=self)
        if not th.config():
            pd.close()
            return
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()
        if hasattr(th, "error"):
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)

    def export_wpxml_file(self):

        egg = self.current_save_path + os.sep + "wordpress.xml"
        mf = MyFile(egg);
        mf.mask = "WordPress XML (*.xml)";
        mf.mode = "w"
        modes = [u"Сохранять в EXCERPT",
            (0, u"Сохранять в EXCERPT"),
            (1, u"Через тег MORE"),
                 ]
        ptypes = [u"Статья",
            ("post", u"Статья"),
            ("page", u"Страница"),
                 ]
        datalist = [
            (u"Файл:", mf),
            (u"Вступительный текст", modes),
            (u"Тип публикаций", ptypes),
        ]
        rc = fedit(datalist, title=u"Экспорт", parent=self)
        if not rc:
            return
        fileName, mode, ptype = rc

        # fileName = QtGui.QFileDialog.getSaveFileName(self, u"Экспорт...", self.current_save_path, "WordPress XML (*.xml)")

        if fileName == "":
            return

        self.current_save_path = os.path.split(unicode(fileName))[0]

        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()

        if self.current_edit_item: # сохраним, если что-то редактировали
            item = self.treeWidget.tree.itemFromIndex(self.current_edit_item)
            self.fields_to_widget(item)

        root = self.treeWidget.get_tree()

        th = wpxml.Export(root, fileName, mode, pd, self)
        th.ptype = ptype
        th.start()

        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()

        if th.error:
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)

    def export_static_site(self):
        self._save_current_item()
        root = self.treeWidget.get_tree()
        th = static.Export(root, "static", progressdialog=None, parent=self)
        if not th.config():
            return
        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setFixedWidth(320)
        pd.show()
        th.pd = pd
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()
        if hasattr(th, "error"):
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)
        self._reload_current_item()

    def export_joomla_file(self):
        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()
        self._save_current_item()
        root = self.treeWidget.get_tree()
        th = joomla.Export(root, "export-j15.sql", progressdialog=pd, parent=self)
        if not th.config():
            pd.close()
            return
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()
        if hasattr(th, "error"):
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)
        self._reload_current_item()

    def export_zebrumlite_file(self):
        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()
        self._save_current_item()
        root = self.treeWidget.get_tree()
        th = zebrumlite.Export(root, "pages.txt", progressdialog=pd, parent=self)
        if not th.config():
            pd.close()
            return
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()
        if hasattr(th, "error"):
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)
        self._reload_current_item()

    def export_dle_file(self):
        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()
        self._save_current_item()
        root = self.treeWidget.get_tree()
        th = dle8.Export(root, "dle.sql", progressdialog=pd, parent=self)
        if not th.config():
            pd.close()
            return
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()
        if hasattr(th, "error"):
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)
        self._reload_current_item()

    def export_cmsimple_file(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, u"Экспорт...", self.current_save_path,
            "CMS Simple HTML (*.htm;*.html)")
        if fileName == "":
            return

        self.current_save_path = os.path.split(unicode(fileName))[0]

        pd = MyProgressDialog(u"Экспорт", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.show()

        if self.current_edit_item: # сохраним, если что-то редактировали
            item = self.treeWidget.tree.itemFromIndex(self.current_edit_item)
            self.fields_to_widget(item)

        root = self.treeWidget.get_tree()

        th = cmsimple.Export(root, fileName, pd, self)
        th.start()

        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        pd.close()

        if th.error:
            self.errmsg.setWindowTitle(u"Ошибка экспорта")
            self.errmsg.showMessage(th.error)

    def import_rssfeed(self):
        comment = u"Укажите адрес ленты на сайте, либо имя файла на диске."
        mf = MyFile("http://blap.ru/feed/")
        mf.mask = "RSS Feed (*.xml)"
        mf.mode = "r"
        datalist = [(u"Адрес ленты:", mf)]
        rc = fedit(datalist, title=u"Импорт RSS Feed", parent=self, comment=comment)
        if not rc:
            return
        (fileName,) = rc
        # fileName = r"d:\work\promidol\test\lipfrss.xml"
        # fileName = r"d:\work\promidol\test\forum.xml"
        self.import_template(rssfeed.Import, fileName)

    def import_template(self, import_class, fileName):
        if not fileName:
            return
        fileName = unicode(fileName)
        pd = MyProgressDialog(u"Импорт", u"Открытие", u"Отмена", 0, 0, self)
        pd.show()
        th = import_class(fileName, pd, self)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        canceled = pd.wasCanceled()
        pd.close()
        if th.result:
            # self.treeWidget.set_tree(th.result)
            self.treeWidget.set_tree_withundo(th.result, title=u"Импорт")
        elif not canceled:
            self.errmsg.setWindowTitle(u"Ошибка импорта")
            self.errmsg.showMessage(th.error)

    def import_wpxml_file(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u"Импорт...", self.current_load_path,
            "Wordpress XML (*.xml)")
        if not fileName:
            return
        self.current_load_path = os.path.split(unicode(fileName))[0]
        pd = MyProgressDialog(u"Импорт", u"Открытие файла", u"Отмена", 0, 0, self)
        pd.show()
        th = wpxml.Import(fileName, pd, self)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        canceled = pd.wasCanceled()
        pd.close()
        if th.result:
            # self.treeWidget.set_tree(th.result)
            self.treeWidget.set_tree_withundo(th.result, title=u"Импорт")
        elif not canceled:
            self.errmsg.setWindowTitle(u"Ошибка импорта")
            self.errmsg.showMessage(th.error)

    def import_uparser(self):
        root = Article()

        def add_article(rc):
            if not isinstance(rc[0], unicode):
                title = unicode(rc[0], "utf-8")
            else:
                title = rc[0]
            if not isinstance(rc[1], unicode):
                text = unicode(rc[1], "utf-8")
            else:
                text = rc[1]
            root.add_child(Article(title, text))

        dlg = SpiderDialog(self)
        QtCore.QObject.connect(dlg, QtCore.SIGNAL('addArticle(PyQt_PyObject)'), add_article)
        dlg.exec_()
        self.treeWidget.set_tree_withundo(root, title=u"Импорт")

    def import_textdir_file(self):
        fileName = QtGui.QFileDialog.getExistingDirectory(self, u"Импорт каталога",
            self.current_load_path)
        if not fileName:
            return
        self.current_load_path = os.path.split(unicode(fileName))[0]
        pd = MyProgressDialog(u"Импорт", u"Открытие каталог", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()
        th = textdir.Import(fileName, pd, self)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        canceled = pd.wasCanceled()
        pd.close()
        if th.result:
            # self.treeWidget.set_tree(th.result)
            self.treeWidget.set_tree_withundo(th.result, title=u"Импорт")
        elif not canceled:
            self.errmsg.setWindowTitle(u"Ошибка импорта")
            self.errmsg.showMessage(th.error)

    def import_cmsimple_file(self):
        fileName = QtGui.QFileDialog.getOpenFileNames(self, u"Импорт...", self.current_load_path,
            "CMS Simple HTML (*.htm;*.html)")
        if not fileName:
            return

        self.current_load_path = os.path.split(unicode(fileName))[0]
        pd = MyProgressDialog(u"Импорт", u"Открытие файла", u"Отмена", 0, 0, self)
        pd.show()
        th = cmsimple.Import(fileName, pd, self)
        th.start()

        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()

        debug("*** after while")

        canceled = pd.wasCanceled()
        #th.stop()

        debug("vvv pd.close")

        pd.close()

        debug("^^^ pd.close")

        if th.result:
            # self.treeWidget.set_tree(th.result)
            self.treeWidget.set_tree_withundo(th.result, title=u"Импорт")
        elif not canceled:
            self.errmsg.setWindowTitle(u"Ошибка импорта")
            self.errmsg.showMessage(th.error)

        debug("*** import.exit")

    def all_clear(self):
        if QtGui.QMessageBox.question(self, u"Новый документ",
            u"Все изменения будут утеряны.\nПродолжать?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.treeWidget.tree.clear()
            self.anchor_view.clear()
            self.clear_fields()
            self.undo_stack.clear()
            self.set_current_filename()
            self.sbmessage(u"Новый документ")

    def spell_check(self):
        if not self.current_edit_item:
            return
        if self.introTextEdit.hasFocus():
            text_widget = self.introTextEdit
        else:
            text_widget = self.textEdit
        if len(text_widget.text()) == 0:
            return
        try:
            dlg = spelldialog.SpellDialog(self, text_widget)
            dlg.exec_()
        except:
            pass

    def rewriter(self):
        if not self.current_edit_item:
            return
        if self.introTextEdit.hasFocus():
            text_widget = self.introTextEdit
        else:
            text_widget = self.textEdit
        if len(text_widget.text()) == 0:
            return
        try:
            dlg = ThesaurusDialog(self, text_widget)
            dlg.exec_()
        except:
            #exception("rewriter is down, i repeat, rewriter is down")
            pass

    def preview(self):
        if not self.current_edit_item:
            return
        if self.introTextEdit.hasFocus():
            text = self.introTextEdit.text()
        else:
            text = self.textEdit.text()
        dlg = QtGui.QDialog(self)
        dlg.setWindowTitle(u'Предпросмотр')
        dlg.setMinimumSize(640, 480)
        layout = QtGui.QGridLayout(dlg)
        view = QWebView(dlg)
        view.settings().setAttribute(QWebSettings.PluginsEnabled, True)
        #view.settings().setAttribute(QWebSettings.JavaEnabled, True)
        view.settings().setAttribute(QWebSettings.AutoLoadImages, True)
        #view.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        layout.addWidget(view, 0, 0, 1, 1)
        view.setHtml(text)
        dlg.exec_()

    def test(self):
        pass

    def _create_menu(self):
        filemenu = self.menubar.addMenu(u"Файл")
        self.filemenu = filemenu
        filemenu.addAction(u"Новый", self.all_clear, QtGui.QKeySequence("Ctrl+N"))
        filemenu.addAction(u"Открыть", self.load_prt, QtGui.QKeySequence("Ctrl+O"))
        filemenu.addAction(u"Сохранить", self.save_prt, QtGui.QKeySequence("Ctrl+S"))
        filemenu.addAction(u"Сохранить как...", self.save_prt_as)
        filemenu.addSeparator()

        importmenu = filemenu.addMenu(u"Импорт...")
        importmenu.setTearOffEnabled(True)
        importmenu.addAction(u"CMS Simple", self.import_cmsimple_file)
        #importmenu.addAction(u"WordPress XML", self.import_wpxml_file)
        ## importmenu.addAction(u"Каталог txt-файлов", self.import_textdir_file)
        importmenu.addAction(u"RSS Feed", self.import_rssfeed)
        importmenu.addAction(u"Универсальный парсер", self.import_uparser)

        #if self.w == self.q:
        plugs = plugmanager.getImportPlugins()
        #else:
        #    plugs = []
        if plugs:
            importmenu.addSeparator()
            for v in plugs:
                importmenu.addAction(unicode(v[1], "utf-8"), lambda f=v[0]:
                    self.import_plugin_template(f.run), QtGui.QKeySequence(v[2]))

        exportmenu = filemenu.addMenu(u"Экспорт...")
        self.exportmenu = exportmenu
        self.exportmenu.setTearOffEnabled(True)
        # exportmenu.addAction(u"CMS Simple", self.export_cmsimple_file)
        # exportmenu.addAction(u"WordPress XML файл", self.export_wpxml_file)
        # exportmenu.addAction(u"WordPress XML-RPC(WP/metaWeblog)", self.export_wprpc_file)
        # exportmenu.addAction(u"Joomla 1.5", self.export_joomla_file)
        # exportmenu.addAction(u"Datalife Engine 8", self.export_dle_file)
        # exportmenu.addAction(u"Zebrum Lite", self.export_zebrumlite_file)
        # exportmenu.addAction(u"Статичный сайт", self.export_static_site)
        # exportmenu.addAction(u"Livejournal.com", self.export_livejournalcom)
        # exportmenu.addAction(u"Blogger.com", self.export_bloggercom)

        filemenu.addSeparator()
        filemenu.addAction(u"Выход", self.close, QtGui.QKeySequence("Ctrl+Q"))

        findmenu = self.menubar.addMenu(u"Поиск")
        findmenu.addAction(u"Найти/заменить(пакетно)", self.search)
        findmenu.addAction(u"Найти в текущем", self.find_in_text,
            QtGui.QKeySequence("Ctrl+F"))
        findmenu.setTearOffEnabled(True)

        self.articlemenu = articlemenu = self.menubar.addMenu(u"Статья")
        articlemenu.addAction(u"Добавить вступление", self._add_intro_to_current_article)
        articlemenu.addAction(u"Автонарезка", self._auto_splitter)
        articlemenu.addAction(u"Разделить на две", self.split_article)
        articlemenu.addAction(u"Проверка орфографии", self.spell_check)
        articlemenu.addAction(u"Рерайтер", self.rewriter)
        articlemenu.setTearOffEnabled(True)

        articlesmenu = self.menubar.addMenu(u"Обработка")
        articlesmenu.addAction(u"Случайная дата", self.randomize_date)
        articlesmenu.addAction(u"Генератор заголовков", self.title_generator)
        articlesmenu.addAction(u"Обработка заголовков", self.title_sanitizer)
        articlesmenu.addAction(u"Очистка страниц", self.bleacher)
        articlesmenu.addAction(u"Вставка изображений", self.insert_images_from_dir)
        articlesmenu.addAction(u"Замена синонимов", self.sinonimization)
        articlesmenu.addAction(u"Автометки", self.autotags)
        articlesmenu.addAction(u"Вступительный текст", self.intro_generator)
        articlesmenu.addAction(u"Вставка ссылок", self.insertlinks)
        articlesmenu.addAction(u"Проверка уникальности", self.unicheck)
        articlesmenu.setTearOffEnabled(True)
        #if self.w == self.q:
        plugs = plugmanager.getProcessPlugins()
        #else:
        #    plugs = []
        if plugs:
            articlesmenu.addSeparator()
            for v in plugs:
                articlesmenu.addAction(unicode(v[1], "utf-8"), lambda f=v[0]:
                    self.process_plugin_template(f.run), QtGui.QKeySequence(v[2]))

        #if self.w == self.q:
        plugs = plugmanager.getUtilitePlugins()
        #else:
        #    plugs = []
        if plugs:
            menu = self.menubar.addMenu(u"Утилиты")
            for v in plugs:
                menu.addAction(unicode(v[1], "utf-8"), lambda f=v[0]: f.run(self),
                    QtGui.QKeySequence(v[2]))

        self.viewmenu = self.menubar.addMenu(u"Окна")

        helpmenu = self.menubar.addMenu(u"Справка")

        helpmenu.addAction(u"Сайт программы",
            lambda url="http://content-monster.com": self.open_url(url))
        helpmenu.addAction(u"Форум поддержки",
            lambda url="http://blap.ru/forum/index.php?board=75.0": self.open_url(url))

        #helpmenu.addSeparator()
        #helpmenu.addAction(u"Регистрация", self.registration)

        helpmenu.addSeparator()
        helpmenu.addAction(u"Логи", self.show_logs)
        helpmenu.addAction(u"О программе", self.about)

    def show_logs(self):
        dir_ = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation)
        tedir = 'file:///' + unicode(dir_) + '/treeedit'
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(tedir, QtCore.QUrl.TolerantMode))

    def registration(self):
        RegisterDialog(self).exec_()

    def about(self):
        from about_dialog import AboutDialog

        AboutDialog(self).exec_()
        #QtGui.QMessageBox.information(self, u"О программе",
        #    "CM2 TreeEdit v%i.%i.%i" % tuple(updater.__version__))

    def unicheck(self):
        self._save_current_item()
        arts = self.get_selected_items()
        try:
            unicheck.run(arts, self)
        except:
            self.errmsg.setWindowTitle(u"Ошибка обработки")
            self.errmsg.showMessage("%s" % traceback.format_exc())
        self._reload_current_item()

    def insertlinks(self):
        self._save_current_item()
        arts = self.get_selected_items()
        try:
            InsertLinksDialog(arts, self).exec_()
        except Exception, err:
            self.errmsg.setWindowTitle(u"Ошибка обработки")
            self.errmsg.showMessage(err)
        self._reload_current_item()

    def search(self):
        """
        def arts():
            iter = QtGui.QTreeWidgetItemIterator(self.treeWidget.tree)
            while iter.value():
                yield(iter.value())#.article)
                iter += 1
        """
        self._save_current_item()
        arts = self.get_selected_items()
        dlg = SearchDialog(arts, self)
        dlg.exec_()
        #if rc:
        self._reload_current_item()
        if hasattr(dlg, "open_item"):
            self.treeWidget.tree.setCurrentItem(dlg.open_item)

    def autotags(self):
        """
        - генерация меток по выделенным статьям(мин длина, мин вхождений, язык)
        - импорт меток из файла
        - проставление меток по найденым леммам
        - ограничение кол-ва меток на статью
        """
        self._save_current_item()
        #self.save_tmp()
        articles = self.get_selected_items()
        dlg = AutotagsDialog(articles, self)
        rc = dlg.exec_()
        if rc:
            self._reload_current_item()

    def title_generator(self):
        langs = [u"Русский"]
        for k in spelldialog.config:
            langs.append((k, k))

        datalist = [
            (u"Разделитель:", "([\.\?\!]+)"),
            (u"Язык текста:", langs),
            (u"Удалять прилагательные:", True),
            (u"Исправлять регистр:", False),
            (u"Слов, не более:", 10),
        ]

        rc = fedit(datalist, title=u"Генерация заголовков", parent=self)
        if not rc:
            return False

        (delimiter, langkey, remove_prils, capitalize_text, overwords) = rc

        pd = MyProgressDialog(u"Генерация заголовков", u"Загрузка словаря", u"Отмена", 0, 0, self)
        pd.show()
        QtGui.qApp.processEvents()

        hobj, henc = spelldialog.load_spell(langkey)

        pd.setLabelText(u"Формирование списка")

        self._save_current_item()
        articles = self.get_selected_items()

        pd.setValue(0)
        pd.setRange(0, len(articles))
        pd.setLabelText(u"Обработка")

        self.undo_stack.beginMacro(u"Генерация заголовков")

        delimiter_c = re.compile(delimiter, re.U)

        for article in articles:
            article_title = article.article.text
            article_title = html_tags_re.sub("", article_title)
            if not article_title:
                continue
            if remove_prils:
                egg = delimiter_c.split(article_title)[0]
                egg = re.split("(?u)([\s,\:\.\?;]+)", egg)
                spam = []
                for src in egg:
                    word = hobj.analyze(src.encode(henc, "replace"))
                    if not word:
                        spam.append(src)
                        continue
                        # print "|".join(word).decode(henc)
                    word = word[0]
                    word = unicode(word, henc)
                    if "fl:A" not in word: #not pril
                        spam.append(src)
                article_title = "".join(spam)

            article_title = re.sub("(?usmi)[\s]+", " ", article_title)

            article_title = article_title.strip()

            article_title = " ".join(article_title.split(" ")[:overwords])

            if capitalize_text:
                article_title = article_title.capitalize()

            changes = {'title': article_title}
            self.undo_stack.push(EditArticleCommand(self.treeWidget.tree, article, changes))

            pd.setValue(pd.value() + 1)
            QtGui.qApp.processEvents()

        self.undo_stack.endMacro()

        pd.close()

        self._reload_current_item()

    def title_sanitizer(self):
        datalist = [
            (u"Ограничить длину(символов):", 100),
            (u"Учитывать слова:", True),
            (u"Добавлять при ограничении", "..."),
            (u"Исправить регистр:", False),
            (u"Удалять теги:", True)
        ]

        rc = fedit(datalist, title=u"Обработка заголовоков", parent=self)

        if not rc:
            return

        (maxlen, killsword, endstring, _capitalize, clear_html) = rc

        pd = MyProgressDialog(u"Обработка заголовков", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.show()

        self._save_current_item()

        articles = self.get_selected_items()

        pd.setValue(0)
        pd.setRange(0, len(articles))

        pd.setLabelText(u"Обработка")

        self.undo_stack.beginMacro(u"Обработка заголовков")

        for article in articles:
            article_title = article.title
            if clear_html:
                article_title = html_tags_re.sub("", article_title)
            if maxlen:
                article_title = do_truncate(article_title, maxlen, not killsword, endstring)
            if _capitalize:
                article_title = article_title.capitalize()

                changes = {'title': article_title}
                self.undo_stack.push(EditArticleCommand(self.treeWidget.tree, article, changes))

            pd.setValue(pd.value() + 1)
            QtGui.qApp.processEvents()

        self.undo_stack.endMacro()

        pd.close()

        self._reload_current_item()

    def get_selected_items(self, overall=False):
        self.sbmessage(u"Формируется список")

        self.statprogress.setRange(0, 0)

        articles = []
        tree = self.treeWidget.tree
        selected = tree.selectedItems()
        #self.save_tmp()
        if not selected or overall:
            selected = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]

        if not selected:
            self.statprogress.setRange(0, 100)
            return articles

        def recurse_tree(item):
            if item in articles:
                articles.remove(item)
            articles.append(item)
            for i in range(item.childCount()):
                child = item.child(i)
                if child in articles:
                    articles.remove(child)
                articles.append(child)
                #self.statprogress.setValue(self.statprogress.value()+1)
                QtGui.qApp.processEvents()
                recurse_tree(child)

        for item in selected:
            recurse_tree(item)

        self.statprogress.setRange(0, 100)

        return articles

    def _save_current_item(self):
        """ сохраним, если что-то редактировали """
        if self.current_edit_item:
            item = self.treeWidget.tree.itemFromIndex(self.current_edit_item)
            self.fields_to_widget(item)

    def _reload_current_item(self):
        """  обновим, если что-то редактировали """
        if self.current_edit_item:
            curr = self.treeWidget.tree.itemFromIndex(self.current_edit_item)
            self.widget_to_fields(curr)
        self.dirty_flag = DirtyFlag.CLEAN

    def insert_images_from_dir(self):
        comment = u"""<b>Внимание.</b> Каталог изображений должен содержать файлы
        имеющие в названиях только латинские<br/>буквы и цифры. В противном случае
        возможны проблемы с отображением на сайте."""

        lgns = [("", u"Без выравнивания"), (" align=\"left\"", u"Слева"),
            (" align=\"right\"", u"Справа"), (" align=\"center\"", u"Центр")]

        pos = [0, (0, u"В начале страницы"), (1, u"В конце страницы"), (None, u"Случайно")]
        dest = [0, (0, u"Текст"), (1, u"Вступление")]
        lgn = [""]
        lgn.extend(lgns)
        lgn.append((None, u"Случайно"))

        datalist = [
            (u"Каталог изображений:", MyPath(self.current_load_path)),
            (None,
             u"<small>При формировании списка учитываются расширения: <font color=\"#ff0000\">jpg, png, gif</font></small>")
            ,
            (None, None),
            (u"Путь на сайте:", "http://mysite.ru/images/"),
            (u"Перемешать:", True),
            (u"Размещение:", pos),
            (u"Выравнивание:", lgn),
            (u"Добавлять class:", ""),
            (u"Добавлять style:", ""),
            (u"Вставлять в:", dest),
            (u"Обёртка ссылкой:", False),
        ]

        rc = fedit(datalist, title=u"Вставка изображений", parent=self, comment=comment)
        if not rc:
            return

        (srcpath, urlpath, shufflezo, pos_id, align_id, add_class, add_style, dest, wrap) = rc

        self.current_load_path = srcpath

        pd = MyProgressDialog(u"Вставка изображений", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setFixedWidth(320)
        pd.show()

        exts = [".jpg", ".gif", ".png"]
        images_list = get_dir_content(srcpath, exts)

        if not images_list:
            pd.close()
            QtGui.QMessageBox.information(self, u"Все плохо",
                u"В указанном каталоге подходящие изображения отсутсвуют.",
                buttons=QtGui.QMessageBox.Ok)
            return

        if shufflezo:
            pd.set_text(u"Случайный порядок")
            random.shuffle(images_list)
        else:
            pd.set_text(u"Сортировка")
            images_list.sort()

        self._save_current_item()
        articles = self.get_selected_items()
        iterfname = itertools.cycle(images_list)

        pd.set_text(u"Обработка страниц")
        pd.set_range(0, len(articles))

        self.undo_stack.beginMacro(u"Вставка изображений")

        for article in articles:
            align = random.choice(lgns)[0] if align_id == None else align_id
            pos = random.randint(0, 1) if pos_id == None else pos_id
            classegg = " class=\"%s\"" % add_class if add_class else ""
            styleegg = " style=\"%s\"" % add_style if add_style else ""
            fname = iterfname.next()
            params = {
                "urlpath": urlpath,
                "fname": fname,
                "align": align,
                "classegg": classegg,
                "styleegg": styleegg,
                "title": encode_html_entities(article.article.title)
            }
            eggtag = "<img src=\"%(urlpath)s%(fname)s\"%(align)s%(classegg)s%(styleegg)s title=\"%(title)s\" alt=\"%(title)s\"/>" % params

            if wrap:
                link = "%(urlpath)s%(fname)s" % params
                eggtag = "<a href=\"%s\" title=\"%s\">%s</a>" % (link, params["title"], eggtag)

            if dest == 0:
                article_text = eggtag + article.article.text if pos == 0 else article.article.text + eggtag
                self.undo_stack.push(EditArticleCommand(self.treeWidget.tree,
                    article, {"text": article_text}))
            else:
                intro_text = getattr(article.article, "intro", "")
                intro_text = eggtag + intro_text if pos == 0 else intro_text + eggtag
                self.undo_stack.push(EditArticleCommand(self.treeWidget.tree,
                    article, {"intro": intro_text}))

            pd.setValue(pd.value() + 1)
            QtGui.qApp.processEvents()

        self.undo_stack.endMacro()

        self._reload_current_item()

        pd.close()

    def bleacher(self):
        CONFIG_TAG = "gui.ArticleTreeDialog.bleacher"
        settings = shelve.open(CONFIGFILE)
        config = settings.get(CONFIG_TAG, {})
        settings.close()

        datalist = [
            (u"Разрешенные теги:", config.get("tags", "b i strong img h br p em")),
            (u"Разрешенные атрибуты:", config.get("attrs", "src title alt")),
            (u"Новая строка после br:", config.get("newline", True)),
            (u"Сжатие пробелов:", config.get("removeoverspace", True)),
            (None, u"<b>Очистка:</b>"),
            (u"Текста", config.get("cleantext", True)),
            (u"Интро", config.get("cleanintro", True)),
            (u"Заголовков", config.get("cleanintro", True)),
        ]

        rc = fedit(datalist, title=u"Обработка текста", parent=self)
        if not rc:
            return

        (tags, attrs, newline, removeoverspace, cleantext, cleanintro, cleantitle) = rc

        settings = shelve.open(CONFIGFILE)
        self.params = {"tags": tags,
                       "attrs": attrs,
                       "newline": newline,
                       "removeoverspace": removeoverspace,
                       "cleantext": cleantext,
                       "cleanintro": cleanintro,
                       "cleantitle": cleantitle,
                       }
        settings[CONFIG_TAG] = self.params
        settings.close()

        testoverspaces = re.compile("[ \t\f\v]{1,}", re.U | re.M | re.S)
        TAGS = tags.split(" ")
        ATTRS = attrs.split(" ")

        self._save_current_item()

        pd = MyProgressDialog(u"Очистка текста", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()

        articles = self.get_selected_items()
        pd.setRange(0, len(articles))

        debug("articles for processing %i" % len(articles))
        #dates = []

        self.undo_stack.beginMacro(u"Очистка страниц")

        for article in articles:
            pd.setLabelText(u"Обрабатываем: %s" % article.article.title)
            changes = {}
            if cleantext:
                article_text = clear_html(article.article.text, TAGS, ATTRS, newline)
                if removeoverspace:
                    article_text = testoverspaces.sub(" ", article_text)
                article_text = article_text.strip()
                changes["text"] = article_text
            if cleanintro and hasattr(article.article, "intro") and article.article.intro:
                article_intro = clear_html(article.article.intro, TAGS, ATTRS, newline)
                if removeoverspace:
                    article_intro = testoverspaces.sub(" ", article_intro)
                article_intro = article_intro.strip()
                changes["intro"] = article_intro
            if cleantitle:
                egg = re.sub(html_tags_re, " ", article.article.title)
                if removeoverspace:
                    egg = testoverspaces.sub(" ", egg)
                egg = egg.strip()
                changes["title"] = egg
            self.undo_stack.push(EditArticleCommand(self.treeWidget.tree, article, changes))

            pd.setValue(pd.value() + 1)
            QtGui.qApp.processEvents()

        self.undo_stack.endMacro()

        pd.close()

        self._reload_current_item()

    def randomize_date(self):
        """
        configfile = os.path.join(pluginpath, "randomize_data.pkl")
        try:
            settings = cPickle.load(open(configfile, "rt"))
        except IOError:
        """

        weekdays = {
            u"пн": 0,
            u"вт": 1,
            u"ср": 2,
            u"чт": 3,
            u"пт": 4,
            u"сб": 5,
            u"вс": 6
        }

        td = datetime.datetime.now()
        de = datetime.timedelta(days=90)
        bf = datetime.timedelta(days=365)
        settings = (td - bf, td + de, True)

        datalist = [
            (u"Начальная дата:", settings[0]),
            (u"Конечная дата:", settings[1]),
            (u"Перемешивать:", settings[2])
        ]

        params = [
            (u"Часы публикации", u"9:00-13:00 14:00-18:00"),
            (u"Дни недели", u"пн вт ср чт пт"),
            (None, u"<i>пример: пн вт ср чт пт сб вс</i>"),
            (u"Нерабочие дни", u"1-10.1 23.02 22.04 1.5 22.6 1.9 7.11"),
            (None, u"<i>пример периода: 1-10.1 - январские праздники</i>"),
        ]

        if not hasattr(sys, "frozen"):
            params[0] = (u"Часы публикации", u"9:00-9:10")

        datagroup = (
            (datalist, u"Период", u"Период публикации статей"),
            (params, u"Настройки", u"Настройки ограничений времени публикации%s" % (" " * 30))
            )

        rc = fedit(datagroup, title=u"Случайные даты", parent=self)

        if not rc:
            return

        timespatt = "(?P<from_h>\d{1,2})\:(?P<from_m>\d{1,2})-(?P<to_h>\d{1,2})\:(?P<to_m>\d{1,2})"
        times = []
        for d in re.finditer(timespatt, rc[1][0]):
            egg = d.groupdict()
            times.append((datetime.time(int(egg["from_h"]), int(egg["from_m"])),
                          datetime.time(int(egg["to_h"]), int(egg["to_m"]))))

        days = []
        for k, v in weekdays.items():
            if rc[1][1].find(k) > -1:
                days.append(v)

        datetempp = "((?P<from>\d+)-(?P<to>\d+\.\d+))|(?P<date>\d+\.\d+)"

        holydays = []
        for d in re.finditer(datetempp, rc[1][2]):
            egg = d.groupdict()
            if egg["date"]:
                day, month = map(int, egg["date"].split("."))
                holydays.append({"date": (day, month)})
            if egg["from"] and egg["to"]:
                fday = int(egg["from"])
                tday, tmonth = map(int, egg["to"].split("."))
                holydays.append({"period": (fday, tday, tmonth)})

        #print holydays

        #settings = rc
        #cPickle.dump(settings, open(configfile, "wt"))

        (from_date, to_date, shuffle) = rc[0]
        from_date = time.mktime(from_date.timetuple())
        to_date = time.mktime(to_date.timetuple())

        if from_date > to_date:
            from_date, to_date = to_date, from_date

        pd = MyProgressDialog(u"Случайные даты", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.show()

        debug("%i %i %s" % (from_date, to_date, shuffle))

        self._save_current_item()

        articles = self.get_selected_items()

        debug("articles for processing %i" % len(articles))

        dates = []

        wrongtimes = len(articles) * 200

        pd.setLabelText(u"Генерация дат")

        while len(dates) < len(articles):
            rnd = random.randint(from_date, to_date)
            egg = datetime.datetime.fromtimestamp(rnd)
            skip = True
            for row in times:
                if egg.time() > row[0] and egg.time() < row[1]:
                    skip = False
                    debug("skip=False causes [%s]<[%s]<[%s]", row[0], egg.time(), row[1])
                    break
            if egg.weekday() in days and not skip:
                skip = False

            for hd in holydays:
                if hd.has_key("date"):
                    if egg.day == hd["date"][0] and egg.month == hd["date"][1]:
                        debug("nahren date %s", egg)
                        skip = True
                elif hd.has_key("period"):
                    if (egg.month == hd["period"][2] and
                        egg.day >= hd["period"][0] and egg.day <= hd["period"][1]):
                        debug("nahren date %s", egg)
                        skip = True
                else:
                    skip = False

            if not skip or wrongtimes < 0:
                debug("append [%s] causes skip[%s] and wrongtimes[%i]", egg, skip, wrongtimes)
                dates.append(rnd)
            else:
                wrongtimes -= 1
                debug("wrongtimes--")
                if wrongtimes == 0:
                    debug("limits off")
            QtGui.qApp.processEvents()

        if not shuffle:
            dates.sort()

        pd.setLabelText(u"Обработка")

        self.undo_stack.beginMacro(u"Случайная дата")

        for article in articles:
            newdate = datetime.datetime.fromtimestamp(dates.pop(0))
            #article.article.date=QtCore.QDate(newdate.year, newdate.month, newdate.day)
            #article_date=QtCore.QDate(newdate.year, newdate.month, newdate.day)
            command = RandomDateCommand(self.treeWidget.tree, article, newdate)
            self.undo_stack.push(command)
            #debug(article.title)
            QtGui.qApp.processEvents()

        self.undo_stack.endMacro()

        pd.close()

        self._reload_current_item()

    def split_article(self):
        """
        Поставил курсор в нужное место в тексте
 нажимаю "разделить на две"
После курсора текст исчез, вторая часть не создалась

В лог файле пишет:

Traceback (most recent call last):
  File "commands.pyo", line 111, in redo
  File "mytreeitem.pyo", line 67, in text
AttributeError: 'MyTreeItem' object has no attribute 'set_icon'
        """

        widget = self.textEdit
        orig_text = unicode(widget.text())
        if not widget.hasSelectedText():
            from_selection = widget.getCursorPosition()
            lines = widget.lines()
            len_last_line = widget.lineLength(lines)
            widget.setSelection(from_selection[0], from_selection[1], lines, len_last_line)
        selected_text = unicode(widget.selectedText())
        if not selected_text:
            return

        self._save_current_item()

        #'v'*10
        widget.removeSelectedText()
        new_text = unicode(widget.text())
        try:
            first_line = selected_text.split(".")[0]
        except IndexError: #one line
            first_line = selected_text
        finally:
            first_line = html_tags_re.sub("", first_line)
        art = Article(first_line, selected_text)

        orig_item = self.treeWidget.tree.itemFromIndex(self.current_edit_item)

        new_item = MyTreeItem(art, None)

        command = SplitTextCommand(self.treeWidget.tree, orig_item, orig_text, new_text, new_item)
        self.undo_stack.push(command)

        self.dirty_flag = DirtyFlag.CLEAN
        self.treeWidget.tree.setCurrentItem(new_item)

    def sinonimization(self):
        dlg = YazzyDialog(self)
        rc = dlg.exec_()
        if not rc:
            return

        self._save_current_item()
        pd = MyProgressDialog(u"Синонимы", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()

        articles = self.get_selected_items()
        th = SynoThread(articles, dlg.params, pd, self)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
                break
            QtGui.qApp.processEvents()
        canceled = pd.wasCanceled()
        pd.close()

        if hasattr(th, "result"):
            if th.result:
                QtGui.QMessageBox.information(self, u"Замена синонимов",
                    u"Найдено и обработано %i синонимов." % th.result, buttons=QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.information(self, u"Замена синонимов",
                    u"Синонимов не найдено.\n"\
                    u"Убедитесь, что выделили все статьи в дереве которые хотите обработать.\n"\
                    u"Проверьте выбранные словари и расстояним между словами.", buttons=QtGui.QMessageBox.Ok)
        elif not canceled:
            self.errmsg.setWindowTitle(u"Ошибка обработки")
            self.errmsg.showMessage(th.error)

        self._reload_current_item()
        pd.close()

    def intro_generator(self):
        testoverspaces = re.compile("[ \t\f\v]{1,}")
        splitwords = re.compile("(\s|</{0,1}[^>]*?>)", re.M | re.I | re.S)
        datalist = [
            (u"Слов во вступительном тексте", 30),
            (u"Удалять HTML теги", True),
            (u"Удалять интро из текста", False)
        ]
        rc = fedit(datalist, title=u"Вступительный текст", parent=self)
        if not rc:
            return
        (maxwords, deltags, remove_from_main) = rc

        self._save_current_item()
        pd = MyProgressDialog(u"Вступительный текст", u"Формирование списка", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()
        articles = self.get_selected_items()
        pd.setRange(0, len(articles))

        debug("articles for processing %i" % len(articles))

        self.undo_stack.beginMacro(u"Вступительный текст")
        lcleaner = Cleaner(embedded=False, frames=False, safe_attrs_only=False)

        for article in articles:
            pd.setLabelText(u"Обрабатываем: %s" % article.article.title)
            words = splitwords.split(article.article.text)
            if remove_from_main:
                article_text = "".join(words[maxwords * 2:])
            else:
                article_text = article.article.text
            intro_text = "".join(words[:maxwords * 2])
            if deltags:
                intro_text = clear_html(intro_text, [], [], False)
                intro_text = testoverspaces.sub(" ", intro_text).strip()
            else:
                try:
                    # debug("title: %s (%i,%i)", article.article.title, len(intro_text), len(article_text))
                    if intro_text:
                        intro_text = lcleaner.clean_html(intro_text)
                    if article_text:
                        pass  # нафига чистить исходный текст?
                        #article_text = lcleaner.clean_html(article_text)
                except XMLSyntaxError:
                    warning("wrong xml syntax")

            pd.setValue(pd.value() + 1)

            self.undo_stack.push(
                EditArticleCommand(self.treeWidget.tree, article,
                    {
                        "intro": intro_text,
                        "text": article_text
                    }
                )
            )

            QtGui.qApp.processEvents()

        self.undo_stack.endMacro()

        pd.close()
        self._reload_current_item()

    def closeEvent(self, event):
        debug("closed")

        if self.undo_stack.count() > 0:
            rc = QtGui.QMessageBox.question(self, u"Выход",
                u"Документ был изменён. Продолжить?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Save)
            if rc == QtGui.QMessageBox.No:
                event.ignore()
                return
            if rc == QtGui.QMessageBox.Save:
                self.save_prt()

        if self._tess:
            self._tess.shutdown()

        settings = shelve.open(CONFIGFILE)
        self.params = {}
        self.params["state"] = self.saveState()
        self.params["geometry"] = self.saveGeometry()
        self.params["splittersize"] = self.splitter.sizes()

        self.params["paths"] = (self.current_load_path, self.current_save_path)
        self.params["splittersize"] = self.splitter.sizes()

        settings["ArticlesTreeDialog"] = self.params
        settings.close()

        event.accept()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    #app.setStyle("Plastique")
    ico = QtGui.QIcon(':/ico32/img/cm2.png')
    app.setWindowIcon(ico)

    MainWindow = ArticlesTreeDialog("autoload.prt")
    MainWindow.show()

    sys.exit(app.exec_())

    #root = import_cmsimple(u"d:\\work\\wptr\\html\\Сибирская поэзия2.html")
    #cPickle.dump(root, open("siberia_poetry.prt","wb"), cPickle.HIGHEST_PROTOCOL )
