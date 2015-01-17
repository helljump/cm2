#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL
import logging
import sys

class TestWidget( QtGui.QWidget ):
    def __init__( self, parent=None ):
        QtGui.QWidget.__init__( self, parent )
        self.verticalLayout = QtGui.QVBoxLayout(self)        
        self.label = QtGui.QPushButton("TestLabel", self)
        self.verticalLayout.addWidget(self.label)

    def pizdets(self):
        logging.debug("Widget closeEvent")

class TestDialog( QtGui.QDialog ):
    def __init__( self, *args ):
        QtGui.QWidget.__init__( self, *args )        
        gridLayout = QtGui.QGridLayout(self)
        self.widget = TestWidget(self)        
        self.connect(self,SIGNAL("pizdets()"),self.widget.pizdets)
        gridLayout.addWidget( self.widget, 0, 0, 1, 1)
            
    def closeEvent(self, event):
        self.emit( SIGNAL("pizdets()") )
        logging.debug("Dialog closeEvent")
        event.accept()
    
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    td = TestDialog()
    td.exec_()
