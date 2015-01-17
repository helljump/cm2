#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
from engine.anticaptcha import get_antigate_balance, WrongKey
import shelve
from utils.qthelpers import MyProgressDialog
from logging import debug
from engine.browser import BrowserError

class BalanceThread(QtCore.QThread):
    def __init__(self, agkey, parent):
        QtCore.QThread.__init__(self)
        self.agkey = agkey
        self.exc = Exception("no value")
        debug("ideal thread count: %i", QtCore.QThread.idealThreadCount())
        
    def run(self):
        try:
            self.rc = get_antigate_balance(self.agkey)
        except WrongKey as exc:
            self.exc = exc
            
    def result(self):
        if not hasattr(self, "rc"):
            raise self.exc                
        return self.rc

class SettingsDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)        
        self.setWindowTitle(self.tr("Settings"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.setupUi()
            
    def setupUi(self):
        self.resize(420, 140)
        
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.frame = QtGui.QFrame(self)
        self.gridLayout = QtGui.QGridLayout(self.frame)
        
        label = QtGui.QLabel(self.tr("Antigate key"), self.frame)
        self.gridLayout.addWidget(label, 0, 0, 1, 1)
        self.key_le = QtGui.QLineEdit(self.frame)
        self.gridLayout.addWidget(self.key_le, 0, 1, 1, 1)

        label_2 = QtGui.QLabel(self.tr("Connection timeout"), self.frame)
        self.gridLayout.addWidget(label_2, 1, 0, 1, 1)
        self.timeout_sb = QtGui.QSpinBox(self.frame)
        self.timeout_sb.setSuffix(self.tr(" s"))
        self.timeout_sb.setRange(1, 180)
        self.gridLayout.addWidget(self.timeout_sb, 1, 1, 1, 1)
        
        label_3 = QtGui.QLabel(self.tr("Stop after"), self.frame)
        self.gridLayout.addWidget(label_3, 2, 0, 1, 1)
        self.errors_sb = QtGui.QSpinBox(self.frame)
        self.errors_sb.setSuffix(self.tr(" % errors"))
        self.errors_sb.setRange(1, 100)
        self.gridLayout.addWidget(self.errors_sb, 2, 1, 1, 1)
                
        self.pushButton = QtGui.QPushButton(self.tr("Check"), self.frame)        
        self.pushButton.clicked.connect(self._check_balance)
        self.gridLayout.addWidget(self.pushButton, 0, 2, 1, 1)
        
        self.verticalLayout.addWidget(self.frame)
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        
        self.verticalLayout.addWidget(self.buttonBox)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

        self._load_config()

    def _check_balance(self):
        agkey = unicode(self.key_le.text())
        pd = MyProgressDialog(self.tr("Checking"), self.tr("Connect to server"), self.tr("Cancel"), 0, 0, self)
        pd.show()
        task = BalanceThread(agkey, pd)
        task.start()
        while task.isRunning():
            QtGui.qApp.processEvents()
            if pd.wasCanceled():
                task.terminate()
                debug("killing task")
                task.wait(1)
                break
        debug("pd close")
        #task.exit()
        pd.close()
        try:
            balance = task.result()
            QtGui.QMessageBox.information(self, self.tr("Antigate balance"),
                self.tr("Antigate balance: ") + balance)
        except WrongKey:
            QtGui.QMessageBox.critical(self, self.tr("Antigate balance"), self.tr("Wrong key"))
        except BrowserError:
            QtGui.QMessageBox.critical(self, self.tr("Antigate balance"), self.tr("Connection error"))
        except:
            pass
        debug("stop check")

    def _load_config(self):
        cfg = shelve.open("yadd.cfg")
        agkey = cfg.get("yadd.antigate_key", "")
        timeout = cfg.get("yadd.connection_timeout", 30)
        stoperrors = cfg.get("yadd.stop_after_errors", 100)
        cfg.close()
        
        self.key_le.setText(agkey)
        self.errors_sb.setValue(stoperrors)
        self.timeout_sb.setValue(timeout)
    
    def _save_config(self):
        agkey = unicode(self.key_le.text())
        stoperrors = self.errors_sb.value()
        timeout = self.timeout_sb.value()
        
        cfg = shelve.open("yadd.cfg")
        cfg["yadd.antigate_key"] = agkey
        cfg["yadd.connection_timeout"] = timeout
        cfg["yadd.stop_after_errors"] = stoperrors
        cfg.close()
    
    def accept(self):
        self._save_config()
        self.hide()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SettingsDialog().exec_()
