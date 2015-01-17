#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread
from logging import debug, error
from engine.browser import Browser

class ButtonLineEdit(QtGui.QFrame):
    def __init__(self, text, buttontext, callable, *args):
        QtGui.QWidget.__init__(self, *args)        
        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.lineedit = QtGui.QLineEdit(self)
        self.lineedit.setText(text)
        layout.addWidget(self.lineedit)
        self.button = QtGui.QToolButton(self)
        self.button.setText(buttontext)
        self.button.clicked.connect(callable)
        layout.addWidget(self.button)
        self.connect(self, QtCore.SIGNAL("disable()"), self.disable)
        self.connect(self, QtCore.SIGNAL("enable(char*)"), self.enable)
        
    def disable(self):
        self.setDisabled(True)
        self.button.setText("Wait..")
        
    def enable(self, text):
        self.setEnabled(True)
        self.button.setText("...")
        self.lineedit.setText(text)
        
    def setText(self, text):
        self.lineedit.setText(text)
        
    def setButton(self, text):
        self.button.setText(text)
        
    def text(self):
        return self.lineedit.text()

class GetMetaThread(QThread):
    def __init__(self, field, value, parent):
        QtCore.QThread.__init__(self, parent)
        self.field = field
        self.url = None
        self.value = value

    def setUrl(self, url):
        self.url = url

    def run(self):
        if not self.url:
            return
        self.field.emit(QtCore.SIGNAL("disable()"))
        br = Browser(timeout=11)
        try:
            br.open(self.url)
            data = br.soup.find("meta", {"name":self.value})["content"]
        except:
            error("getting keywords data from site")
            data = ""
        self.field.emit(QtCore.SIGNAL("enable(char*)"), data)
        
    def stop(self):
        self.terminate()
        self.wait()

class LinkDialog(QtGui.QDialog):
    def __init__(self, url="", desc="", keys="", usedjenah=False, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle(self.tr("Link editor"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(500, 160)
        layout = QtGui.QFormLayout(self)
        
        self.url_le = QtGui.QLineEdit(self)
        self.url_le.setText(url)
        layout.addRow(self.tr("Url"), self.url_le)

        self.desc_le = ButtonLineEdit("", "...", self.get_site_description, self)
        if desc:
            self.desc_le.setText(desc)
        layout.addRow(self.tr("Description"), self.desc_le)
        
        self.keywords_le = ButtonLineEdit("", "...", self.get_site_keywords, self)
        if keys:
            self.keywords_le.setText(keys)
        layout.addRow(self.tr("Keywords"), self.keywords_le)

        self.usedjenah_cb = QtGui.QCheckBox(self.tr("Use Djenah") , self)
        self.usedjenah_cb.setChecked(usedjenah)
        layout.addRow(self.usedjenah_cb)
        
        bbox = QtGui.QDialogButtonBox(self)
        bbox.setStandardButtons(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)
        self.connect(bbox, QtCore.SIGNAL("rejected()"), self.reject)
        self.connect(bbox, QtCore.SIGNAL("accepted()"), self.accept)
        layout.addRow(bbox)

        self.keywords_thread = GetMetaThread(self.keywords_le, "keywords", self)         
        self.desc_thread = GetMetaThread(self.desc_le, "description", self)         

    def get_site_keywords(self):
        debug("getting site keys")
        url = unicode(self.url_le.text())
        self.keywords_thread.setUrl(url)
        self.keywords_thread.start()
        
    def get_site_description(self):
        debug("getting site desc")
        url = unicode(self.url_le.text())
        self.desc_thread.setUrl(url)
        self.desc_thread.start()

    def _sanitize(self):
        self.desc_thread.stop()
        self.keywords_thread.stop()
        debug("done")

    def reject(self):
        self._sanitize()
        self.setResult(0)
        self.hide()

    def accept(self):
        self._sanitize()
        self.setResult(1)
        self.hide()

    def closeEvent(self, event):
        self._sanitize()
        event.accept()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ld = LinkDialog("http://lipf.ru", usedjenah=True)
    if ld.exec_():
        debug("%s\n%s\n%s\n%s" % (
            ld.url_le.text(),
            ld.desc_le.text(),
            ld.keywords_le.text(),
            ld.usedjenah_cb.isChecked()
        ))
    
