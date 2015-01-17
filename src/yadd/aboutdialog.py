#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
#from proxy.checker.proxyform import ProxyForm
#from rss.rss import RSSWidget
#from utils.translator import Translator
import logging
#import rc.rc
import shelve
import sys

class AboutDialog( QtGui.QDialog ):
    def __init__( self, *args ):
        QtGui.QWidget.__init__( self, *args )        
        self.setWindowTitle( self.tr("About") )
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(370, 240)
        layout = QtGui.QFormLayout(self)
                
        about_tb = QtGui.QTextBrowser(self)
        layout.addRow(about_tb)
        about_tb.setOpenExternalLinks(True)
        about_tb.anchorClicked.connect( self.launchBrowser )
        
        '''
        self.antigatekey_le = QtGui.QLineEdit(self)
        self.antigatekey_le.setFocus()
        layout.addRow( self.tr("Antigate key"), self.antigatekey_le )
        '''
        
        bbox = QtGui.QDialogButtonBox(self)
        bbox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.connect(bbox, QtCore.SIGNAL("accepted()"), self.accept)
        layout.addRow(bbox)

        html_text = QtCore.QResource( ":/yadd/about.html" ).data()
        about_tb.setText( unicode(html_text) )

        #self.load_config()
        
    def launchBrowser(self, url):
        logging.debug("browse %s" % url)
        QtGui.QDesktopServices.openUrl( url )
        return True

    def accept(self):
        logging.debug("done")
        #self.save_config()
        self.hide()
    
    def save_config(self):
        agkey = unicode(self.antigatekey_le.text())
        cfg = shelve.open("yadd.cfg")
        cfg["yadd.antigate_key"] = agkey
        cfg.close()

    def load_config(self):
        cfg = shelve.open("yadd.cfg")
        agkey = cfg.get("yadd.antigate_key","")
        cfg.close()
        self.antigatekey_le.setText(agkey)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    AboutDialog().exec_()
