#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
import sys
import logging
import google_com, google_ru, yandex
import proxy.checker.proxyform_rc #@UnusedImport
import threading
import Queue
from rss.rss import RSSWidget
import shelve
from engine.browser import BrowserError
from utils.qthelpers import ToolBarWithPopup
import time

engines = { 
    "Google.ru":google_ru.get_links,
    "Google.com":google_com.get_links,
    "Yandex.ru":yandex.get_links 
}

class Codes(object): (PROCESS, SE, VALUE, URL) = range(4)

def parse_proxy(queue, queries, selist, nums, stopevent):
    try:
        i = 0
        for q in queries:
            logging.debug("process %s" % q)
            for k, v in selist.items():
                queue.put_nowait((Codes.SE, "[%s] from [%s]" % (q, k)))
                queue.put_nowait((Codes.VALUE, i))
                try:
                    links = v(q, nums)
                except BrowserError, err:
                    logging.error("parser proxy [%s]" % err)
                for link in links:
                    queue.put_nowait((Codes.URL, link))
                if stopevent.is_set():
                    raise RuntimeError
                i += 1
    except RuntimeError:
        logging.debug("thread stopped")

class MyListItem(QtGui.QListWidgetItem):
    def __init__(self, parent, engine_name, engine_func):
        QtGui.QListWidgetItem.__init__(self, parent)
        self.engine_func = engine_func
        self.engine_name = engine_name
        self.setText(engine_name)
        self.setFlags(QtCore.Qt.ItemIsSelectable | 
                       QtCore.Qt.ItemIsUserCheckable | 
                       QtCore.Qt.ItemIsEnabled)
        self.setCheckState(QtCore.Qt.Checked)

class SEDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)        
        self.setWindowTitle(self.tr("Search Engine Parser"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(640, 480)
        self.set_ui()
        
    def set_ui(self):
        self.gridLayout = QtGui.QGridLayout(self)
        self.se_lw = QtGui.QListWidget(self)
        self.se_lw.setAlternatingRowColors(True)
        self.gridLayout.addWidget(self.se_lw, 0, 0, 1, 1)
        
        self.frame = QtGui.QFrame(self)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        
        tbframe = ToolBarWithPopup(self)
        tbframe.addAction(QtGui.QIcon(":/ico/run.png"), self.tr("Parse SE"), self.run)
        tbframe.addAction(QtGui.QIcon(":/ico/add.png"), self.tr("Add query"), self.add_query)
        tbframe.addAction(QtGui.QIcon(":/ico/delete.png"), self.tr("Remove query"), self.del_query)  
        tbframe.addSeparator()
        tbframe.addWidget(QtGui.QLabel(self.tr("Links")))
        self.num_sb = QtGui.QSpinBox(tbframe)
        tbframe.addWidget(self.num_sb)
        self.gridLayout_2.addWidget(tbframe, 0, 0, 1, 4)

        self.label_2 = QtGui.QLabel(self.tr("Query"), self.frame)
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 4)
        
        self.query_lw = QtGui.QListWidget(self.frame)
        self.gridLayout_2.addWidget(self.query_lw, 2, 0, 1, 4)
                
        self.label_3 = QtGui.QLabel(self.tr("Result links"), self.frame)
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 4)
        
        self.result_lw = QtGui.QListWidget(self.frame)
        self.result_lw.setAlternatingRowColors(True)
        self.gridLayout_2.addWidget(self.result_lw, 4, 0, 1, 4)
        
        self.gridLayout.addWidget(self.frame, 0, 1, 1, 1)
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)

        self.result_lw.setSortingEnabled(True)
        
        #self.addRSS()
        self.load_config()

    def addRSS(self):
        rssWidget = RSSWidget(self)
        self.connect(self, QtCore.SIGNAL("pizdets()"), rssWidget.closeEvent)
        self.gridLayout.addWidget(rssWidget, 2, 0, 1, 2)
        
    def add_query(self):
        item = QtGui.QListWidgetItem("query", self.query_lw)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | 
                       QtCore.Qt.ItemIsEnabled)
        self.query_lw.editItem(item)
        
    def del_query(self):
        selected = self.query_lw.currentRow()
        self.query_lw.takeItem(selected)
        
    def run(self):
        logging.debug("run")        
        nums = int(self.num_sb.value())
        selist = {}
        for i in range(self.se_lw.count()):
            item = self.se_lw.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selist[item.engine_name] = item.engine_func
        queries = [ unicode(self.query_lw.item(i).text()) for i in range(self.query_lw.count()) ]

        queue = Queue.Queue()
        stopevent = threading.Event()
        pd = QtGui.QProgressDialog(self)
        pd.setModal(True)
        pd.setWindowTitle(self.tr(u"Parse SE"))
        pd.setRange(0, len(queries) * len(selist))
        pd.setMaximumWidth(480)
        pd.forceShow()

        th = threading.Thread(target=parse_proxy, args=(queue, queries, selist, nums, stopevent))
        th.start()
        logging.debug("thread start")

        while th.isAlive():
            try:
                spam = queue.get(False)
                if spam[0] == Codes.VALUE:
                    pd.setValue(spam[1])
                elif spam[0] == Codes.SE:
                    pd.setLabelText("Parse %s" % spam[1])
                elif spam[0] == Codes.URL:
                    if not self.result_lw.findItems(spam[1], QtCore.Qt.MatchFixedString):
                        QtGui.QListWidgetItem(spam[1], self.result_lw)
                    logging.debug("add page %s" % spam[1])
            except Queue.Empty:
                pass
            if pd.wasCanceled():
                stopevent.set()
                th.join()
            QtGui.qApp.processEvents()
            time.sleep(0.01)
        pd.close()

        logging.debug("thread stop")

    def accept(self):
        self.save_config()
        self.emit(QtCore.SIGNAL("pizdets()"))
        logging.debug("done")
        self.hide()
        self.setResult(1)
        
    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL("pizdets()"))
        event.accept()
        
    def save_config(self):
        selist = {}
        for i in range(self.se_lw.count()):
            item = self.se_lw.item(i)
            l = unicode(item.text())
            c = bool(item.checkState() == QtCore.Qt.Checked)
            selist[l] = c
            
        queries = [ unicode(self.query_lw.item(i).text()) 
            for i in range(self.query_lw.count()) ]
                
        links_num = int(self.num_sb.value())

        settings = shelve.open("proxy.cfg")
        settings["proxy.se.selist"] = selist
        settings["proxy.se.queries"] = queries
        settings["proxy.se.links_num"] = links_num
        settings.close()

    def load_config(self):
        settings = shelve.open("proxy.cfg")
        selist = settings.get("proxy.se.selist", {})
        queries = settings.get("proxy.se.queries", ["free proxy list", "free socks list"])
        links_num = settings.get("proxy.se.links_num", 10)
        settings.close()
        
        for k, v in engines.items():
            item = MyListItem(self.se_lw, k, v)
            state = selist.get(k, True)
            item.setCheckState(QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)
        
        for query in queries:
            QtGui.QListWidgetItem(query, self.query_lw)
            
        self.num_sb.setValue(links_num)

if __name__ == "__main__":    
    app = QtGui.QApplication(sys.argv)
    #tr = Translator( None, 'parser_%s.qm' % QLocale.system().name() )
    #app.installTranslator( tr )
    SEDialog().exec_()
    logging.debug("__main__ over")
