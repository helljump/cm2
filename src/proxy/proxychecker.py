#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
from PyQt4 import QtGui
from PyQt4.QtCore import QLocale
from proxy.checker.proxyform import MainDialog as ProxyMainDialog 
from utils.translator import Translator
import logging
import proxychecker_rc #@UnusedImport

reload(sys)
if hasattr(sys, "setdefaultencoding"): sys.setdefaultencoding("utf-8")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    #app.setStyle("Cleanlooks")
    app.setWindowIcon(QtGui.QIcon(':/ico/proxychecker.png'))
    tr = Translator(None, 'proxychecker_%s.qm' % QLocale.system().name())
    app.installTranslator(tr)
    try:
        ProxyMainDialog().exec_()
    except:
        logging.exception("Unhandled exception")
    logging.debug("__main__ over")
