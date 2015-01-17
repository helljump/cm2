#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
from PyQt4 import QtCore, QtGui
import logging

log = logging.getLogger(__name__)

label = u"""<center>Скопируйте в текстовое поле присланый вам ключ и нажмите <b>OK</b>
</center>
"""

from utils.paths import KEY_FILENAME

class RegisterDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Регистрация")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(320, 240)

        gridLayout = QtGui.QGridLayout(self)
                
        gridLayout.addWidget(QtGui.QLabel(label), 0, 0)
                
        self.key_te = QtGui.QPlainTextEdit(self)
        gridLayout.addWidget(self.key_te, 1, 0)
                
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        gridLayout.addWidget(buttonBox, 2, 0)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
    def accept(self):
        obj = unicode(self.key_te.toPlainText())
        with open(KEY_FILENAME, "wb") as fout:
            fout.write(obj)
        rc = QtGui.QMessageBox.information(self, u"Регистрация", #@UnusedVariable
                u"Ключ сохранен. Перезапустите программу.",
                QtGui.QMessageBox.Ok)
        self.hide()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    RegisterDialog(None).exec_()
