#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import pickle
import qthelpers
import os


class Dialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        egg = os.path.join(os.path.dirname(__file__), 'unkey.ui')
        uic.loadUi(egg, self)

    @pyqtSlot(name='on_hash_textEdit_textChanged')
    def decode(self):
        egg = str(self.hash_textEdit.toPlainText())
        params = pickle.loads(egg.decode("base64"))
        self.src_textEdit.setPlainText(unicode(params))
        k = params['key']
        del params['key']
        a = qthelpers.gen(params)
        b = k
        if a == b:
            self.rc_lineEdit.setText('OK')
        else:
            self.rc_lineEdit.setText('WRONG')

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    Dialog(None).exec_()
