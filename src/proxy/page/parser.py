#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread
import Queue
from engine.browser import Browser, BrowserError
from proxy.se.parser import SEDialog
from utils.qthelpers import addPopup, ToolBarWithPopup, MyProgressDialog
from logging import debug, error
import os
import page_rc #@UnusedImport
import proxy.checker.proxyform_rc #@UnusedImport
import re
import shelve
import sys, time

#address_template = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{2,4})")
address_template = re.compile("((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\w\-]{2,20}\.\w{2,4})\:(\d{2,6}))")

class Codes(object): (URL, PROXY, VALUE) = range(3)

class PageParserThread(QThread):
    def __init__(self, task_queue, done_queue, parent):
        QtCore.QThread.__init__(self, parent)
        self.task_queue = task_queue
        self.done_queue = done_queue

    def run(self):
        i = 0
        debug("run thread")
        for url in iter(self.task_queue.get, "STOP"):
            try:
                debug("open url %s" % url)
                self.done_queue.put((Codes.URL, url))
                br = Browser(timeout=20)
                br.open(url)
                debug("let's iterate") 
                for item in address_template.finditer(br.source):
                    debug("%s -> queue" % item.groups(0)[0])
                    self.done_queue.put((Codes.PROXY, str(item.groups(0)[0])))
            except BrowserError, e:        
                error("page parser error %s" % e)
            i += 1
            debug("put value")
            self.done_queue.put((Codes.VALUE, i))    

class ParserDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi()
        self.load_config()
    
    def setupUi(self):
        self.resize(640, 480)
        self.setWindowTitle(self.tr("Search Engine Parser"))
        self.setWindowFlags(QtCore.Qt.Window) 

        self.gridLayout = QtGui.QGridLayout(self)
        #setMargin(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)
                
        tbframe = ToolBarWithPopup(self)

        tbframe.addAction(QtGui.QIcon(":/ico/run.png"), self.tr("Parse"), self.run)
        tbframe.addAction(QtGui.QIcon(":/ico/internet.png"), self.tr("Queries"), self.import_from_se)
        tbframe.addAction(QtGui.QIcon(":/ico/import.png"), self.tr("Import"), self.import_from_file)
        tbframe.addAction(QtGui.QIcon(":/ico/proxy.png"), self.tr("Default proxy"), self.set_default_proxyurl)
        self.gridLayout.addWidget(tbframe, 0, 0, 1, 2)        
        
        self.listbox_frame = QtGui.QFrame(self)
        self.listbox_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.listbox_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout_2 = QtGui.QGridLayout(self.listbox_frame)
        self.pages_lb = QtGui.QLabel(self.tr("Pages"), self.listbox_frame)
        self.gridLayout_2.addWidget(self.pages_lb, 0, 0, 1, 1)
        self.pages_lw = QtGui.QListWidget(self.listbox_frame)
        self.pages_lw.setSortingEnabled(True)
        addPopup(self.pages_lw, self.pages_popup)
        self.gridLayout_2.addWidget(self.pages_lw, 1, 0, 1, 1)
        self.proxy_lw = QtGui.QListWidget(self.listbox_frame)
        self.proxy_lw.setSortingEnabled(True)
        addPopup(self.proxy_lw, self.proxies_popup)
        self.gridLayout_2.addWidget(self.proxy_lw, 1, 1, 1, 1)
        self.proxy_lb = QtGui.QLabel(self.tr("Proxy"), self.listbox_frame)
        self.gridLayout_2.addWidget(self.proxy_lb, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.listbox_frame, 7, 0, 1, 2)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        
    def import_from_file(self):
        file_name = QtGui.QFileDialog.getOpenFileName(self, self.tr("Import proxy pages"),
                                                      ".", "proxy pages file (*.txt)")
        if file_name == "":
            return
        
        debug("getting pages from file")
        for page in open(file_name).readlines():
            page = page.strip()
            m = self.pages_lw.findItems(page, QtCore.Qt.MatchFixedString)
            if not m:
                QtGui.QListWidgetItem(page, self.pages_lw)
        
    def proxies_popup(self, point):
        index = self.proxy_lw.indexAt(point)
        if not index.isValid(): 
            return
        menu = QtGui.QMenu(self)
        menu.addAction(self.tr("Remove selected proxy(s)"),
            self.remove_selected_proxies).setIcon(QtGui.QIcon(":/ico/delete.png"))
        menu.exec_(QtGui.QCursor.pos())
        
    def pages_popup(self, point):
        debug("pages popup")

        menu = QtGui.QMenu(self)
        menu.addAction(self.tr("Add page"), self.add_page).setIcon(QtGui.QIcon(":/ico/add.png"))
        
        index = self.pages_lw.indexAt(point)
        if index.isValid(): 
            menu.addAction(self.tr("Parse selected page(s)"), self.parse_selected_pages).setIcon(QtGui.QIcon(":/ico/run.png"))
            menu.addSeparator()
            menu.addAction(self.tr("Remove selected page(s)"), self.remove_selected_pages).setIcon(QtGui.QIcon(":/ico/delete.png"))
        
        menu.exec_(QtGui.QCursor.pos())

    def add_page(self):
        debug("add page")
        item = QtGui.QListWidgetItem("http://www.yandex.ru", self.pages_lw)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | 
                       QtCore.Qt.ItemIsEnabled)
        self.pages_lw.editItem(item)
        
    def parse_selected_pages(self):
        urllist = []
        for item in self.pages_lw.selectedItems():
            urllist.append(unicode(item.text()))
        self.run(urllist)
        
    def remove_selected_pages(self):
        indexes = []
        for item in self.pages_lw.selectedItems():
            indexes.append(self.pages_lw.indexFromItem(item).row())
        indexes.sort(reverse=True)
        for item_index in indexes:
            self.pages_lw.takeItem(item_index)

    def remove_selected_proxies(self):
        indexes = []
        for item in self.proxy_lw.selectedItems():
            indexes.append(self.proxy_lw.indexFromItem(item).row())
        indexes.sort(reverse=True)
        for item_index in indexes:
            self.proxy_lw.takeItem(item_index)

    def test(self, q, w):
        debug("test")

    '''
    def parse_page_thread(self, task_queue, done_queue):
        i = 0
        debug("run thread")
        for url in iter(task_queue.get, "STOP"):
            try:
                debug("open url %s" % url)
                done_queue.put((Codes.URL, url))
                br = Browser(timeout=20)
                br.open(url)
                for item in address_template.finditer(br.source):
                    #debug("%s -> queue" % item.groups(0)[0])
                    done_queue.put((Codes.PROXY, str(item.groups(0)[0])))
            except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException, BrowserError), e:        
                error("page parser error %s" % e)
            i += 1
            debug("put value")
            done_queue.put((Codes.VALUE, i))
    '''
    
    def run(self, urllist=None):
        
        if not urllist:
            urllist = [ unicode(self.pages_lw.item(i).text()) for i in range(self.pages_lw.count()) ]        

        #pd = QtGui.QProgressDialog(self)
        pd = MyProgressDialog(self.tr("Parse pages"), self.tr("Open url"),
                              self.tr("Cancel"), 0, len(urllist), self)
        pd.setMaximumWidth(480)
        pd.forceShow()
        
        debug("put urls in queue")
        
        task_queue = Queue.Queue()
        done_queue = Queue.Queue()

        for url in urllist:
            task_queue.put(url)

        task_queue.put("STOP")
        
        debug("start")
        #task = Process(target=self.test, args=(task_queue, done_queue))
        #task = Process(target=self.parse_page_thread, args=(task_queue, done_queue))
        
        task = PageParserThread(task_queue, done_queue, pd)
        task.start()
    
        while task.isRunning():
            if not done_queue.empty():
                spam = done_queue.get()
                if spam[0] == Codes.URL:
                    urltext = spam[1] if (spam[1]) < 30 else "%s.." % spam[1][:30]
                    pd.setLabelText("Parse %s" % urltext)
                elif spam[0] == Codes.VALUE:
                    pd.setValue(spam[1])
                elif spam[0] == Codes.PROXY:
                    #logging.debug("queue -> %s" % spam[1])
                    if not self.proxy_lw.findItems(spam[1], QtCore.Qt.MatchFixedString):
                        QtGui.QListWidgetItem(spam[1], self.proxy_lw)
            
            if pd.wasCanceled():
                task.terminate()
                debug("terminated")
                break
            QtGui.qApp.processEvents()
            time.sleep(0.01)
            
        debug("queue task [%s] queue done [%s]", task_queue.empty(), done_queue.empty())
        #task_queue.close()
        #done_queue.close()
        pd.close()
        debug("thread done")
                
    def import_from_se(self):
        dlg = SEDialog(self)
        if dlg.exec_():
            debug("getting pages")
            for i in range(dlg.result_lw.count()):
                page = dlg.result_lw.item(i).text()
                m = self.pages_lw.findItems(page, QtCore.Qt.MatchFixedString)
                if not m:
                    QtGui.QListWidgetItem(page, self.pages_lw)

    def set_default_proxyurl(self):
        self.pages_lw.clear()
        defaultproxyurl = QtCore.QResource(":/proxy_page_tester/defaultproxyurl.txt").data()
        for url in defaultproxyurl.split("\r\n"):
            QtGui.QListWidgetItem(unicode(url), self.pages_lw)

    def clear_pages(self):
        debug("clear pages")
        self.pages_lw.clear()

    def clear_proxies(self):
        debug("clear proxies")
        self.proxy_lw.clear()

    def accept(self):
        self.save_config()
        self.hide()
        self.setResult(1)
        debug("pp done")

    def load_config(self):
        if not os.path.isfile("proxy.cfg"):
            self.set_default_proxyurl()
            
        settings = shelve.open("proxy.cfg")
        pages = settings.get("proxy.page.pages", [])
        proxies = settings.get("proxy.page.proxies", [])
        settings.close()
        
        for page in pages:
            QtGui.QListWidgetItem(page, self.pages_lw)
        
        if proxies:
            for proxy in proxies:
                QtGui.QListWidgetItem(proxy, self.proxy_lw)

    def save_config(self):
        pages = [ unicode(self.pages_lw.item(i).text()) 
                        for i in range(self.pages_lw.count()) ]
        proxies = [ unicode(self.proxy_lw.item(i).text()) 
                        for i in range(self.proxy_lw.count()) ]
        
        settings = shelve.open("proxy.cfg")
        settings["proxy.page.pages"] = pages
        settings["proxy.page.proxies"] = proxies
        settings.close()

if __name__ == "__main__":    
    app = QtGui.QApplication(sys.argv)
    #tr = Translator( None, 'parser_%s.qm' % QLocale.system().name() )
    #app.installTranslator( tr )
    Dialog = ParserDialog()
    Dialog.exec_()
    debug("app done")
