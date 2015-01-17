#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import proxyform_rc #@UnusedImport
from logging import debug, error
from rss.rss import RSSDialog
from proxy.page.parser import ParserDialog
from progressdialog import ProgressDialog
import shelve
from utils.qthelpers import ToolBarWithPopup

target_urls = {
    "http://www.google.com":u"<title>Google</title>",
    "http://www.yandex.ru":u"<title>Яндекс</title>"
}

class Codes(object): (TEST, DONE) = range(2)

class MyTreeItem(QtGui.QTreeWidgetItem):
    
    def __init__(self, parent, address, stat):
        self.status = stat
        self.address = address
        self.tr = parent.tr
        self.parentwidget = parent
        super(MyTreeItem, self).__init__((address, self.get_status()),
                                         type=QtGui.QTreeWidgetItem.UserType)
        self.setIcon(0, QtGui.QIcon(":/ico/proxy.png"))
        
    def get_status(self):        
        if self.status is None:
            return self.tr("Tested...")
        elif self.status == 0:
            return self.tr("Unknown")
        elif self.status > 0:
            return "%.3f " % self.status
        else:
            return self.tr("Bad")
        
    def emitDataChanged(self):
        self.setText(1, self.get_status())
        
    def __ge__(self, other):
        debug("call __ge__")
        
    def __lt__(self, other):
        col = self.parentwidget.header().sortIndicatorSection()
        #order = self.parentwidget.header().sortIndicatorOrder()
        if col==0: #ips
            return self.address < other.address
        elif col==1: #status
            return self.status < other.status 
        
class MyProxyList(QtGui.QTreeWidget):
    def __init__(self, parent):
        super(MyProxyList, self).__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels((self.tr("Proxy address"), self.tr("Status")))        
        self.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(False)
        self.setSortingEnabled(True)
        self.sortItems(1, QtCore.Qt.AscendingOrder)

class ProxyForm(QtGui.QWidget):
    #proxycfgfile = "proxylist.cfg"
    #cfgfile = "proxyconfig.cfg"

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setui()
        self.load_config()
        
    def setui(self):
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setMargin(0)

                
        tbframe = ToolBarWithPopup(self)
        
        tbframe.addAction(QtGui.QIcon(":/ico/run.png"), self.tr("Check list"), self.run)
        tbframe.addAction(QtGui.QIcon(":/ico/remove.png"), self.tr("Remove bad"), self.clear_bad_proxies)
        tbframe.addSeparator()
        tbframe.addAction(QtGui.QIcon(":/ico/internet.png"), self.tr("Import from pages"), self.parse_proxies_from_pages)
        tbframe.addSeparator()
        tbframe.addAction(QtGui.QIcon(":/ico/import.png"), self.tr("Import file"), self.import_from_file)
        tbframe.addAction(QtGui.QIcon(":/ico/export.png"), self.tr("Export file"), self.export_to_file)
        tbframe.addSeparator()
        tbframe.addAction(QtGui.QIcon(":/ico/rss.png"), self.tr("RSS"), self._viewrss)

        self.verticalLayout.addWidget(tbframe)
        
        tbframe2 = QtGui.QFrame(self)
        tbframe = QtGui.QHBoxLayout(tbframe2)

        tbframe.addWidget(QtGui.QLabel(self.tr("Threads")))
        self.threads_sb = QtGui.QSpinBox(self)
        self.threads_sb.setMinimum(1)
        self.threads_sb.setValue(3)
        tbframe.addWidget(self.threads_sb)

        tbframe.addWidget(QtGui.QLabel(self.tr("Url")))

        self.url_le = QtGui.QComboBox(self)
        for k, v in target_urls.items():
            self.url_le.addItem(k, v)
        tbframe.addWidget(self.url_le)

        '''
        self.url_le = QtGui.QLineEdit(self)
        self.url_le.setText("http://www.google.com")
        tbframe.addWidget( self.url_le )
        '''

        tbframe.addWidget(QtGui.QLabel(self.tr("Timeout(s)")))
        self.timeout_sb = QtGui.QSpinBox(self)
        self.timeout_sb.setMinimum(1)
        self.timeout_sb.setMaximum(180)
        self.timeout_sb.setValue(90)
        tbframe.addWidget(self.timeout_sb)
        
        tbframe.addItem(QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding))
        
        self.verticalLayout.addWidget(tbframe2)

        self.proxy_tw = MyProxyList(self)
        
        self.verticalLayout.addWidget(self.proxy_tw)
        
        self.proxy_tw.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.proxy_tw.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.proxy_tw, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.mouse_clicked)
                
    def _viewrss(self):
        dlg = RSSDialog(self)
        dlg.exec_()
        
    def parse_proxies_from_pages(self):
        dlg = ParserDialog(self)
        if dlg.exec_():
            debug("getting proxies")
            for i in range(dlg.proxy_lw.count()):
                url = unicode(dlg.proxy_lw.item(i).text())
                m = self.proxy_tw.findItems(url, QtCore.Qt.MatchFixedString)
                if not m:
                    spam = MyTreeItem(self.proxy_tw, url, 0)
                    self.proxy_tw.addTopLevelItem(spam)
        
    def mouse_clicked(self, point):
        index = self.proxy_tw.indexAt(point)
        if not index.isValid(): return
        menu = QtGui.QMenu(self)
        menu.addAction(self.tr("Test selected proxy"),
            self.test_selected_proxies).setIcon(QtGui.QIcon(":/ico/run.png"))
        menu.addSeparator()
        menu.addAction(self.tr("Remove proxy"),
            self.remove_selected_proxies).setIcon(QtGui.QIcon(":/ico/delete.png"))
        menu.exec_(QtGui.QCursor.pos())
        
    def test_selected_proxies(self):
        indexes = []
        for item in self.proxy_tw.selectedItems():
            indexes.append(self.proxy_tw.indexOfTopLevelItem(item))
        self.run(indexes)
        
    def remove_selected_proxies(self):
        indexes = []
        for item in self.proxy_tw.selectedItems():
            indexes.append(self.proxy_tw.indexOfTopLevelItem(item))
        indexes.sort(reverse=True)
        for item_index in indexes:
            self.proxy_tw.takeTopLevelItem(item_index)
        #self.proxies_le.setText("%i" % self.proxy_tw.topLevelItemCount())

    def export_to_file(self):
        try:
            fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Export proxies"), ".", "proxies file (*.txt)")
            if fileName == "": return
            debug("save to %s" % fileName)
            with open(fileName, "wt") as fout:
                for i in range(self.proxy_tw.topLevelItemCount()):
                    item = self.proxy_tw.topLevelItem(i)
                    fout.write("%s\n" % item.address) 
        except IOError, err:
            error("import error %s" % err)
        
    def import_from_file(self):
        try:
            fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Import proxies"), ".", "proxies file (*.txt)")
            if fileName:
                debug("import from %s" % fileName)
                proxy_list = {}
                for item in open(fileName).readlines():
                    proxy_list[item.strip()] = 0
                for i in range(self.proxy_tw.topLevelItemCount()):
                    item = self.proxy_tw.topLevelItem(i)
                    proxy_list[item.address] = item.status
                self.proxy_tw.clear()
                for k, v in proxy_list.items():
                    item = MyTreeItem(self.proxy_tw, k, v)
                    self.proxy_tw.addTopLevelItem(item)
        except IOError, err:
            error("import error %s" % err)
        #self.proxies_le.setText("%i" % self.proxy_tw.topLevelItemCount())

    def load_config(self):
        settings = shelve.open("proxy.cfg")
        threads_amount = settings.get("proxy.checker.threads_amount", 10)
        timeout = settings.get("proxy.checker.timeout", 15)
        proxylist = settings.get("proxy.checker.proxylist", [])
        engine = settings.get("proxy.checker.test_url", "")
        settings.close()

        for proxy in proxylist:
                item = MyTreeItem(self.proxy_tw, proxy[0], proxy[1])
                self.proxy_tw.addTopLevelItem(item)

        self.threads_sb.setValue(threads_amount)
        self.timeout_sb.setValue(timeout)

        i = self.url_le.findText(engine)
        if i > -1:
            self.url_le.setCurrentIndex(i)
        
    def clear_bad_proxies(self):
        fordel = []
        for i in range(self.proxy_tw.topLevelItemCount()):
            if self.proxy_tw.topLevelItem(i).status == -1:
                fordel.append(i)
        fordel.sort(reverse=True)
        for item in fordel:
            self.proxy_tw.takeTopLevelItem(item)
        
    def test(self):
        debug("test")
        
    def run(self, proxylist=None):
        if not self.proxy_tw.topLevelItemCount():
            return
        if not proxylist:
            proxylist = range(self.proxy_tw.topLevelItemCount()) #all items
        poolsize = int(self.threads_sb.value())
        
        #урл теперь будет кортежем (урл,содержимое ответа)
        ndx = self.url_le.currentIndex()
        egg_url = unicode(self.url_le.currentText())
        egg_answer = unicode(self.url_le.itemData(ndx).toPyObject())
        target_url = (egg_url, egg_answer)
        #target_url = str(self.url_le.text())
        
        timeout = int(self.timeout_sb.value())

        spam = []
        for i in proxylist:
            item = self.proxy_tw.topLevelItem(i)
            spam.append(item)

        pd = ProgressDialog(spam, target_url, timeout, poolsize, self)
        pd.exec_()
        
        for item in spam:
            item.emitDataChanged()

    def save_config(self):
        threads_amount = int(self.threads_sb.value())
        timeout = int(self.timeout_sb.value())
        proxylist = []
        for i in range(self.proxy_tw.topLevelItemCount()):
            item = self.proxy_tw.topLevelItem(i)
            status = item.status if item.status != None else 0
            proxylist.append([ item.address, status ])
        test_url = unicode(self.url_le.currentText())
            
        settings = shelve.open("proxy.cfg")
        settings["proxy.checker.threads_amount"] = threads_amount
        settings["proxy.checker.timeout"] = timeout
        settings["proxy.checker.proxylist"] = proxylist
        settings["proxy.checker.test_url"] = test_url
        settings.close()
        
        debug("config saved")
        
class MainDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)        
        self.setWindowTitle(self.tr("Proxy checker"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(800, 600)
        
        verticalLayout = QtGui.QVBoxLayout(self)
        self.proxy_widget = ProxyForm(self)
        verticalLayout.addWidget(self.proxy_widget)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Save)
        verticalLayout.addWidget(buttonBox)
        buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def accept(self):
        self.proxy_widget.save_config()
        self.hide()
            
    def closeEvent(self, event):
        rc = QtGui.QMessageBox.question(self, self.tr("Exit"), self.tr("Are you sure?\nAll changes will be lost."), 
                                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.No )
        if rc == QtGui.QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    #tr = Translator( None, 'proxyform_%s.qm' % QLocale.system().name() )
    #app.installTranslator( tr )
    MainDialog().exec_()
    debug("__main__ over")
