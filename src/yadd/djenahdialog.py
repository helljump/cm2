#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
from logging import debug
import rc.rc #@UnusedImport
import shelve
import sys

class DjenahDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)        
        self.setWindowTitle(self.tr("Djenah Links editor"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(640, 480)
        layout = QtGui.QVBoxLayout(self)
        
        toolbar = QtGui.QToolBar(self)
        toolbar.addAction(QtGui.QIcon(":/yadd/add.png"), self.tr("Add link(s)"), self.add_link)
        toolbar.addAction(QtGui.QIcon(":/yadd/remove.png"), self.tr("Remove link(s)"),
            self.remove_link)
        toolbar.addSeparator()
        toolbar.addAction(QtGui.QIcon(":/yadd/import.png"), self.tr("Insert from file") ,
            self.import_from_file)
        toolbar.addAction(QtGui.QIcon(":/yadd/import_2.png"), self.tr("Insert from buffer"),
            self.import_from_clipboard)
        toolbar.addAction(QtGui.QIcon(":/yadd/disk.png"), self.tr("Export to file"), self.export_to_file)
        layout.addWidget(toolbar)
        
        self.djenah_lw = QtGui.QListWidget(self)
        self.djenah_lw.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.djenah_lw.setAlternatingRowColors(True)
        self.djenah_lw.setSortingEnabled(True)
        layout.addWidget(self.djenah_lw)
        
        bbox = QtGui.QDialogButtonBox(self)
        bbox.setStandardButtons(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)
        self.connect(bbox, QtCore.SIGNAL("rejected()"), self.reject)
        self.connect(bbox, QtCore.SIGNAL("accepted()"), self.accept)
        layout.addWidget(bbox)
        self.editedIted = None
        self.load_config()
        
    def export_to_file(self):
        try:
            fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"), ".", "Text file (*.txt)")
            if fileName == "": 
                return
            debug("save to %s" % fileName)
            with open(fileName, "wt") as fout:
                for i in range(self.djenah_lw.count()):
                    link = unicode(self.djenah_lw.item(i).text())
                    fout.write("%s\n" % link)
        except IOError:
            QtGui.QMessageBox.error(self, self.tr("Save file"), self.tr("File not saved"))
            
    def import_from_clipboard(self):
        text = unicode(QtGui.QApplication.clipboard().text())
        for link in text.split("\n"):
            if not link.strip():
                continue
            item = QtGui.QListWidgetItem(link.strip(), self.djenah_lw)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    def import_from_file(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Import links"), ".",
            "djenah links (*.txt)")
        if fileName:
            debug("import from %s" % fileName)
            for link in open(fileName).readlines():
                link = link.strip()
                if len(link)<3:
                    continue
                item = QtGui.QListWidgetItem(link.strip(), self.djenah_lw)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    def add_link(self):
        #cnt = self.djenah_lw.count()
        item = QtGui.QListWidgetItem("http://test.ru/[SITEURL]", self.djenah_lw)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        self.djenah_lw.addItem(item)
        self.djenah_lw.scrollToItem(item)
        self.djenah_lw.editItem(item)
        
    def remove_link(self):
        indexes = []
        for item in self.djenah_lw.selectedItems():
            indexes.append(self.djenah_lw.row(item))
        indexes.sort(reverse=True)
        for item_index in indexes:
            self.djenah_lw.takeItem(item_index)

    def accept(self):
        if self.save_config():
            self.hide()
        debug("done")
    
    def save_config(self):
        links = []
        for i in range(self.djenah_lw.count()):
            link = unicode(self.djenah_lw.item(i).text())
            if link.find("[SITEURL]") == -1:
                QtGui.QMessageBox.critical(self, self.tr("Save error"),
                                           self.tr("Djenah link not include template [SITEURL]"))
                self.djenah_lw.setCurrentRow(i)
                self.djenah_lw.scrollToItem(self.djenah_lw.item(i))
                return False
            links.append(link)
            
        cfg = shelve.open("yadd.cfg")
        cfg["yadd.djenah_links"] = links
        cfg.close()
        return True

    def load_config(self):
        cfg = shelve.open("yadd.cfg")
        links = cfg.get("yadd.djenah_links", [])
        cfg.close()
        for link in links:
            item = QtGui.QListWidgetItem(link, self.djenah_lw)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable 
                | QtCore.Qt.ItemIsEnabled)

    def closeEvent(self, event):
        event.accept()
        debug("done")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    DjenahDialog().exec_()
