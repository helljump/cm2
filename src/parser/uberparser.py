#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

#import psyco
#psyco.full()

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QDesktopServices
from PyQt4.QtCore import Qt, QLocale, QSettings, QThread
from proxy.proxychecker import ProxyMainDialog
from rss.rss import RSSDialog
from scripts.articles.rusarticles import parse_rusarticles, parse_articlesbase, \
    ParserCode
from utils.qthelpers import ToolBarWithPopup, MyProgressDialog
from utils.translator import Translator
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement
import Queue
import logging
import random
import rc.rc #@UnusedImport
import shelve
import sys
import time
import os

USERHOME = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
HOMEPATH = os.path.join(unicode(USERHOME), "uberparser2").encode("mbcs")
if not os.path.isdir(HOMEPATH):
    os.mkdir(HOMEPATH)

HTML_HEAD = "<html><head><meta http-equiv=\"content-type\" content=\"text/html;charset=%s\"></head><body>\n"
HTML_TAIL = "</body></html>"

engines = {
    "Articlesbase.com":parse_articlesbase,
    "Rusarticles.com":parse_rusarticles
}

class TextViewer(QtGui.QDialog):
    def __init__(self, title, text, *args):
        QtGui.QTreeWidgetItem.__init__(self, *args)
        self.resize(640, 480)
        self.setWindowTitle(title)
        layout = QtGui.QVBoxLayout(self)
        text_br = QtGui.QTextBrowser(self)
        text_br.setText(text)
        layout.addWidget(text_br)

class MyTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, title, text, *args):
        QtGui.QTreeWidgetItem.__init__(self, *args)
        self.setIcon(0, QtGui.QIcon(":/ico/text_block.png"))
        self.title = title
        self.text = text
        self.setText(0, title)
        self.setText(1, str(len(text)))

class ParserThread(QThread):
    def __init__(self, parse_func, query, amount, proxy, queue, parent):
        QtCore.QThread.__init__(self, parent)
        self.parse_func = parse_func
        self.query = query
        self.amount = amount
        self.proxy = proxy
        self.queue = queue

    def run(self):
        self.parse_func(self.query, self.amount, self.proxy, self.queue)

class ParserDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)        
        self.setupUi()
        self.load_config()

    def setupUi(self):
        self.resize(800, 600)
        self.setWindowTitle(self.tr("Uberparser 2"))
        self.setWindowFlags(QtCore.Qt.Window) 
        verticalLayout = QtGui.QVBoxLayout(self)
        
        toolbar = ToolBarWithPopup(self)
        toolbar.addAction(QtGui.QIcon(':/ico/run.png'), self.tr("Run"), self.run_parser)
        toolbar.addAction(QtGui.QIcon(':/ico/view_tree.png'), self.tr("Expand tree"), self.expand_tree)
        toolbar.addAction(QtGui.QIcon(':/ico/delete.png'), self.tr("Clear"), self.clear_tree)
        toolbar.addWidget(QtGui.QLabel(self.tr("Query:"), self))
        self.query_le = QtGui.QLineEdit(self)
        toolbar.addWidget(self.query_le)
        toolbar.addWidget(QtGui.QLabel(self.tr("Source:"), self))
        self.source_cb = QtGui.QComboBox(self)
        for k, v in engines.items():
            self.source_cb.addItem(self.tr(k), v)
        toolbar.addWidget(self.source_cb)
        toolbar.addWidget(QtGui.QLabel(self.tr("Articles:"), self))
        self.articles_amount_sb = QtGui.QSpinBox(self)
        self.articles_amount_sb.setRange(1, 150)
        toolbar.addWidget(self.articles_amount_sb)
        toolbar.addSeparator()
        toolbar.addAction(QtGui.QIcon(':/ico/save_all.png'), self.tr("Save"), self.save_as)
        toolbar.addSeparator()
        toolbar.addAction(QtGui.QIcon(':/ico/proxy.png'), self.tr("Proxylist"), self.proxychecker)
        toolbar.addAction(QtGui.QIcon(':/ico/rss.png'), self.tr("Rss"), self.viewrss)
        
        verticalLayout.addWidget(toolbar)
        self.articles_tw = QtGui.QTreeWidget(self)
        self.articles_tw.headerItem().setText(0, self.tr("Article"))
        self.articles_tw.headerItem().setText(1, self.tr("Size"))
        
        #self.articles_tw.header().setResizeMode(0, QtGui.QHeaderView.Interactive)
        #self.articles_tw.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.articles_tw.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.articles_tw.header().setStretchLastSection(False)
        self.articles_tw.setAlternatingRowColors(True)
        #self.articles_tw.setSortingEnabled(True)
        self.articles_tw.setAutoExpandDelay(10)
        self.articles_tw.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.articles_tw.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
           
        verticalLayout.addWidget(self.articles_tw)

        self.articles_tw.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.articles_tw, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"),
            self.mouse_clicked)
        self.connect(self.articles_tw, QtCore.SIGNAL("doubleClicked(const QModelIndex &)"),
            self.itemDoubleClicked)

    def _expand_tree(self):
        from cProfile import Profile
        from pstats import Stats
        p = Profile()
        p.runcall(self._expand_tree)
        stats = Stats(p)
        stats.sort_stats('time', 'calls')
        stats.print_stats() 

    def expand_tree(self):
        iter = QtGui.QTreeWidgetItemIterator(self.articles_tw)
        while iter.value():
            iter.value().setExpanded(True)
            iter += 1
            #QtGui.qApp.processEvents()

    def itemDoubleClicked(self, modelindex):
        self._view_text()

    def mouse_clicked(self, point):
        index = self.articles_tw.indexAt(point)
        if not index.isValid(): 
            return

        menu = QtGui.QMenu(self)
        menu.addAction(self.tr("View text"), self._view_text).setIcon(QtGui.QIcon(":/ico/text_block.png"))
        menu.addAction(self.tr("Rename"), self._edit_title).setIcon(QtGui.QIcon(":/ico/edit.png"))
        menu.addSeparator()
        menu.addAction(self.tr("Remove"), self._remove_article).setIcon(QtGui.QIcon(":/ico/delete.png"))
        menu.exec_(QtGui.QCursor.pos())

    def _view_text(self):
        selected = self.articles_tw.selectedItems()
        if selected:
            TextViewer(selected[0].title, selected[0].text, self).exec_()

    def _remove_article(self):
        selected = self.articles_tw.selectedItems()
        map(lambda i: self.articles_tw.removeItemWidget(i, 0), selected)
        
    def _edit_title(self):
        selected = self.articles_tw.selectedItems()
        if not selected:
            return
        text, rc = QtGui.QInputDialog.getText(self, self.tr("Rename article"), self.tr("New name:"),
            text=selected[0].title)
        if rc:
            selected[0].title = text
            selected[0].setText(0, text)

    def clear_tree(self):
        if not self.articles_tw.topLevelItemCount():
            return
        rc = QtGui.QMessageBox.question(self, self.tr("Clear articles"), self.tr("Are you sure?"),
                                        buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if rc == QtGui.QMessageBox.Yes:
            self.articles_tw.clear()
        
    def run_parser(self):
        
        logging.debug("run_parser")
        
        query = unicode(self.query_le.text())
        amount = self.articles_amount_sb.value()
        ndx = self.source_cb.currentIndex()
        parse_func = self.source_cb.itemData(ndx).toPyObject()

        settings = shelve.open(os.path.join(HOMEPATH, "proxy.cfg"))
        proxylist = settings.get("proxy.checker.proxylist", [])
        settings.close()
        
        proxy = {"http":random.choice(proxylist)[0]} if proxylist else {}

        queue = Queue.Queue()

        pd = MyProgressDialog(self.tr(u"Parse pages"), self.tr(u"Open"), self.tr(u"Cancel"), 0, amount, self)
        pd.forceShow()
        
        if proxy:
            pd.setLabelText(self.tr("Use proxy: ") + proxy["http"])

        task = ParserThread(parse_func, query, amount, proxy, queue, pd)
        task.start()
        
        while task.isRunning():
            try:
                data = queue.get_nowait()
                if data[0] == ParserCode.DATA:
                    article = data[1]
                    MyTreeItem(article["title"], article["text"], self.articles_tw)
                    pd.setValue(pd.value() + 1)
                    title = article["title"] if article["title"] < 30 else "%s.." % article["title"][:30]
                    pd.setLabelText(title)
                    logging.debug("add article %s" % article["title"])
                elif data[0] == ParserCode.NOLINKS:
                    QtGui.QMessageBox.warning(self, self.tr("Warning"), self.tr("No more links"))
                elif data[0] == ParserCode.ERROR:
                    pd.setValue(pd.value() + 1)
                    pd.setLabelText("%s" % data[1])
            except Queue.Empty:
                pass            
            if pd.wasCanceled():
                task.terminate()
                logging.debug("terminated")
                break
            time.sleep(0.01)
            QtGui.qApp.processEvents()
        #queue.close()
        pd.close()
        
        logging.debug("thread stop")
        
    def autosplit(self):
        logging.debug("autosplit")
        
    def save_as(self):
        logging.debug("save_as")
        try:
            fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"), ".", "cmsimple content (*.html)")
            if fileName == "": return
            logging.debug("save to %s" % fileName)
            with open(fileName, "wt") as fout:
                def _recurse(element, deep=1):
                    for article in element.findall("article"):
                        title = article.find("title").text
                        text = article.find("text").text
                        fout.write("<h%i>%s</h%i>\n" % (deep, title, deep))
                        fout.write("%s\n" % text)
                        _recurse(article, deep + 1)
                fout.write(HTML_HEAD % "utf-8")
                _recurse(self._make_tree())
                fout.write(HTML_TAIL)
        except IOError, err:
            logging.error("import error %s" % err)
            QtGui.QMessageBox.error(self, self.tr("Save file"), self.tr("File not saved"))

    def viewrss(self):
        dlg = RSSDialog(self)
        dlg.setWindowModality(QtCore.Qt.NonModal)
        dlg.exec_()
    
    def proxychecker(self):
        dlg = ProxyMainDialog(self)
        dlg.resize(640, 480)
        dlg.exec_()
    
    def load_config(self):
        settings = shelve.open(os.path.join(HOMEPATH,"parser.cfg"))
        query = settings.get("uberparser.query", u"Цифровое фото")
        engine = settings.get("uberparser.source", "")
        root = settings.get("uberparser.tree", None)
        articles_amount = settings.get("uberparser.articles_amount", 20)
        settings.close()
        
        self.query_le.setText(query)
        
        i = self.source_cb.findText(engine)
        if i > -1:
            self.source_cb.setCurrentIndex(i)
            
        self.articles_amount_sb.setValue(articles_amount)
        
        if root:
            self._recurse_tree_read(root, self.articles_tw)
                
    def _recurse_tree_read(self, element, treeitem):
        for article in element.findall("article"):
            treesubitem = MyTreeItem(article.find("title").text, article.find("text").text, treeitem)
            self._recurse_tree_read(article, treesubitem)

    def _make_article_node(self, parent, item):
        article = SubElement(parent, "article")
        title = SubElement(article, "title")
        title.text = item.title
        text = SubElement(article, "text")
        text.text = item.text
        return article

    def _recurse_tree(self, parent, item):
        for subitem in (item.child(i) for i in range(item.childCount())):
            article = self._make_article_node(parent, subitem)
            self._recurse_tree(article, subitem)

    def _make_tree(self):
        root = ElementTree.Element("articles")
        for i in range(self.articles_tw.topLevelItemCount()):
            item = self.articles_tw.topLevelItem(i)
            article = self._make_article_node(root, item)
            self._recurse_tree(article, item)
        return root

    def save_config(self):
        settings = shelve.open(os.path.join(HOMEPATH,"parser.cfg"))
        settings["uberparser.query"] = unicode(self.query_le.text())
        settings["uberparser.source"] = unicode(self.source_cb.currentText())
        settings["uberparser.articles_amount"] = self.articles_amount_sb.value()
        settings["uberparser.tree"] = self._make_tree()
        settings.close()

    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL("pizdets()"))
        self.save_config()
        event.accept()

if __name__ == "__main__":
    if hasattr(sys, "setdefaultencoding"): sys.setdefaultencoding("utf-8")
    app = QtGui.QApplication(sys.argv)

    """
    if hasattr(sys, "frozen"):
        settings = QSettings(QSettings.NativeFormat, QSettings.UserScope, "Snoa", "Uberparser2")
        v = settings.value("Installed", "Figly")
        if v.toString() != "Maybe":
            sys.exit()
    """
    
    if hasattr(sys, "frozen"):
        sys.stderr = open(os.path.join(HOMEPATH, "cm2te.log"), "w")

    app.setWindowIcon(QtGui.QIcon(':/ico/uberparser.png'))
    tr = Translator(None, 'uberparser_%s.qm' % QLocale.system().name())
    app.installTranslator(tr)
    try:
        ParserDialog().exec_()
    except:
        logging.exception("Unhandled exception")
    logging.debug("__main__ over")
