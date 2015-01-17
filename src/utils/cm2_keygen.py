#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import cPickle
import qthelpers
import datetime
from binascii import a2b_base64
from PyQt4 import QtCore, QtGui

class Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.resize(559, 241)
        gridLayout = QtGui.QGridLayout(self)
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.returnPressed.connect(self.calc)
        gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.textEdit = QtGui.QTextEdit(self)
        gridLayout.addWidget(self.textEdit, 1, 0, 1, 1)

    def calc(self):
        params = {}
        params['username']=unicode(self.lineEdit.text())
        params['product']="content-monster-2-treeedit"
        params['version']="1.0"
        params['date']=str(datetime.datetime.today())
        params['key']=qthelpers.gen(params)
        obj = cPickle.dumps(params, cPickle.HIGHEST_PROTOCOL)
        self.textEdit.setText(obj.encode("base64"))


def save():
    params = {}
    params['username']="Z286647715832-2" #имя тут
    params['product']="treeedit"
    params['version']="1.0"
    params['date']=str(datetime.datetime.today())
    params['key']=qthelpers.gen(params)
    obj = cPickle.dumps(params, cPickle.HIGHEST_PROTOCOL)
    with open("keyfile","wb") as fout:
        fout.write(obj.encode("base64"))

def test():
    finp = open("keyfile","rb")
    obj = a2b_base64(finp.read())
    params = cPickle.loads(obj)
    k = params['key']
    del params['key']
    a = qthelpers.gen(params)
    b = k
    #print a, "\n", b
    assert(a==b)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog().exec_()
