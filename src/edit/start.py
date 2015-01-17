#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
import os
import logging

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
import spynner

from utils.translator import Translator

import icons  # @UnusedImport

curdir = os.getcwd()

progpath = os.path.dirname(sys.argv[0])
if progpath:
    os.chdir(progpath)

USERHOME = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
HOMEPATH = os.path.join(unicode(USERHOME), "treeedit").encode(sys.getfilesystemencoding())
if not os.path.isdir(HOMEPATH):
    os.mkdir(HOMEPATH)

if hasattr(sys, "frozen"):
    sys.stderr = open(os.path.join(HOMEPATH, "cm2te.log"), "wt")
    sys.stdout = open(os.path.join(HOMEPATH, "cm2te2.log"), "wt")
    egg = sys.argv[0]
else:
    egg = __file__
os.environ['PATH'] = os.path.join(os.path.dirname(egg),'tesseract') + ';' + os.environ['PATH']

from gui import ArticlesTreeDialog

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("plugmanager")
log.setLevel(logging.WARNING)

#certs patch
"""
from requests import utils
if hasattr(sys, 'frozen'):
    f = os.path.split(sys.argv[0])[0]
else:
    f = os.path.split(__file__)[0]
utils.POSSIBLE_CA_BUNDLE_PATHS.append(f)
"""

app = QApplication(sys.argv)
ico = QIcon(':/ico32/img/cm2.png')
app.setWindowIcon(ico)
spynner.SpynnerQapplication = app

tr = Translator(None, 'qt_%s.qm' % QLocale.system().name())
app.installTranslator(tr)

AUTOFILE = u"autoload.prt"
if len(sys.argv) == 2:
    AUTOFILE = unicode(sys.argv[1], sys.getfilesystemencoding())


MainWindow = ArticlesTreeDialog(AUTOFILE)
'''
MainWindow.setStyleSheet("""
QMainWindow{
background-image:url(':/ico32/img/elka.png');
background-repeat:no-repeat;
background-position:bottom left;
}
""")
'''
MainWindow.show()

rc = app.exec_()

os.chdir(curdir)

sys.exit(rc)
