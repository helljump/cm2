#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from plugtypes import IProcessPlugin #@UnresolvedImport
from utils.qthelpers import MyProgressDialog
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
import logging 
import random
from itertools import cycle

class Plugin(IProcessPlugin):
    def run(self, items, parent):        
        dlg = Dialog(parent)
        if not dlg.exec_():
            return
        pd = MyProgressDialog(u"Вставка заголовков в статьи", u"Обработка", u"Отмена", 0, 
            len(items), parent)
        pd.setMaximumWidth(320)
        pd.show()
        egg = unicode(dlg.textedit.toPlainText()).split("\n")
        #random.shuffle(egg)
        iter = cycle(egg)
        for item in items:
            newtitle = iter.next()
            item.article.title = "%s %s" % (item.article.title, newtitle)
            pd.inc_value()
            pd.set_text(item.article.title)
            qApp.processEvents()
        pd.close()
        
class Dialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Вставка заголовков в статьи")
        self.resize(500, 500*0.75)
        l = QGridLayout(self)
        l.addWidget(QLabel(u"Строки для вставки"), 0, 0)
        self.textedit = QPlainTextEdit(self)
        l.addWidget(self.textedit)
        bb = QDialogButtonBox(self)
        bb.setOrientation(Qt.Horizontal)
        bb.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        l.addWidget(bb)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)
