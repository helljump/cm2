#!/usr/bin/env python 
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import sys
import datetime, time
import random
from PyQt4 import QtCore, QtGui

class RndDateTimeEdit(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
       
        self.button = QtGui.QToolButton(maximumWidth=100)
        self.button.setText("rnd")
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.clicked.connect(self.set_rnd)
        
        self.dtedit = QtGui.QDateTimeEdit()
        
        layout.addWidget(self.dtedit)
        layout.addWidget(self.button)
        
        self.setLayout(layout)

    def set_rnd(self,text):
        date_to = datetime.datetime.now()
        date_from = datetime.datetime(2000,1,1,0,0,0)
        a = time.mktime(date_from.timetuple())
        b = time.mktime(date_to.timetuple())
        rnd = random.randint(a, b)
        egg = datetime.datetime.fromtimestamp(rnd)
        self.dtedit.setDateTime(egg)
        
    def __getattr__(self, attr):
        return getattr(self.dtedit, attr)
        
if __name__ == "__main__":
    app=QtGui.QApplication(sys.argv)
    egg = RndDateTimeEdit(None)
    egg.show()
    app.exec_()
    egg.dateTime()
    sys.exit()