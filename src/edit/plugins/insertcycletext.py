#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

try:
    from plugtypes import IProcessPlugin #@UnresolvedImport
except:
    IProcessPlugin = object #test
from utils.qthelpers import MyProgressDialog
from PyQt4 import QtGui, QtCore
import logging 
from utils.paths import pluginpath
import re
import os
import pickle
from itertools import cycle

log = logging.getLogger(__name__)

smartsize = lambda width: (width, width * 0.75)

class InsertMode(object): TOP, BOTTOM, INSERT = range(3)

fname = os.path.basename(__file__) + ".pkl"
configfile = os.path.join(pluginpath, fname.encode("mbcs"))

try:
    settings = pickle.load(open(configfile, "rt"))
except IOError:
    settings = {"strings":[], "mode":InsertMode.TOP, "after":1, 
                "splitter":"(<br.?>|</p>)"}   

class Plugin(IProcessPlugin):
    def run(self, items, parent):        
        dlg = Dialog(parent)
        if not dlg.exec_():
            return
        pd = MyProgressDialog(u"Циклическая вставка текста", u"Обработка", u"Отмена",
                              0, len(items), parent)
        pd.setMaximumWidth(320)
        pd.show()
        iter = cycle(settings["strings"])
        splitter = re.compile(settings["splitter"], re.U | re.I | re.M | re.S)
        for item in items:
            txt = item.article.text
            s = iter.next()
            if settings["mode"] == InsertMode.TOP:
                item.article.text = "%s\n%s" % (s, txt) 
            elif settings["mode"] == InsertMode.BOTTOM:
                item.article.text = "%s\n%s" % (txt, s)
            elif settings["mode"] == InsertMode.INSERT:
                egg = splitter.split(item.article.text)
                egg.insert(settings["after"], s)
                item.article.text = "".join(egg)
            pd.set_value(pd.value() + 1)
            pd.set_text(item.article.title)
            QtGui.qApp.processEvents()
        pd.close()
        
class Dialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Циклическая вставка текста")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(*smartsize(500))

        layout = QtGui.QGridLayout(self)
        
        layout.addWidget(QtGui.QLabel(u"Строки для вставки"), 0, 0)
        self.textedit = QtGui.QPlainTextEdit(self)
        layout.addWidget(self.textedit)
        
        egg = QtGui.QHBoxLayout()
        egg.addWidget(QtGui.QLabel(u"Вставка:", self))
        self.top_rb = QtGui.QRadioButton(u"В начале", self)
        egg.addWidget(self.top_rb)
        self.bottom_rb = QtGui.QRadioButton(u"В конце", self)
        egg.addWidget(self.bottom_rb)
        self.insert_rb = QtGui.QRadioButton(u"Вставить после(regexp)", self)
        egg.addWidget(self.insert_rb)
        self.insert_sb = QtGui.QSpinBox(self)
        self.insert_rb.toggled.connect(self.disable)
        egg.addWidget(self.insert_sb)
        self.insert_le = QtGui.QLineEdit(self)
        egg.addWidget(self.insert_le)
        layout.addLayout(egg, 2, 0)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        layout.addWidget(buttonBox)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)

        self.textedit.setPlainText("\n".join(settings["strings"]))
        self.insert_sb.setValue(settings["after"])
        self.insert_le.setText(settings["splitter"])
        if settings["mode"] == InsertMode.TOP:
            self.top_rb.setChecked(True)
        elif settings["mode"] == InsertMode.BOTTOM:
            self.bottom_rb.setChecked(True)
        elif settings["mode"] == InsertMode.INSERT:
            self.insert_rb.setChecked(True)
        self.disable(settings["mode"] == InsertMode.INSERT)

    def disable(self, v):
        self.insert_sb.setEnabled(v)
        self.insert_le.setEnabled(v)

    def accept(self):
        settings["strings"] = unicode(self.textedit.toPlainText()).split("\n")
        settings["splitter"] = unicode(self.insert_le.text())
        settings["after"] = self.insert_sb.value()
        if self.top_rb.isChecked():
            settings["mode"] = InsertMode.TOP
        elif self.bottom_rb.isChecked():
            settings["mode"] = InsertMode.BOTTOM
        elif self.insert_rb.isChecked():
            settings["mode"] = InsertMode.INSERT
       
        pickle.dump(settings, open(configfile, "wt"))
        
        self.setResult(1)
        self.hide()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog(None).exec_()
    #Plugin().run(None)
