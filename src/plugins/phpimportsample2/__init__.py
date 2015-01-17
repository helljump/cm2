#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__date__ = "06.11.2010 23:45:20"
__author__ = "snöa"

import os
from functools import partial
from plugtypes import IImportPlugin
from PyQt4 import QtGui, QtCore
import pyphp
from utils.article import Article
from datetime import datetime


scriptpath = os.path.dirname(__file__)


class Dialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Отчет работы")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(500, 375)
        layout = QtGui.QGridLayout(self)
        self.textedit = QtGui.QPlainTextEdit(self)
        self.textedit.setReadOnly(True)
        layout.addWidget(self.textedit)
        self.connect(self, QtCore.SIGNAL("debug(QString)"),
                     self.textedit, QtCore.SLOT("appendHtml(QString)"))
        self.connect(self, QtCore.SIGNAL("scrolldown()"),
                     self.textedit, QtCore.SLOT("centerCursor()"))

class PHPIng(IImportPlugin):
    def print_cb(self, s):
        if type(s) is not unicode:
            s = unicode(s,"utf-8","replace")
        self.dlg.emit(QtCore.SIGNAL("debug(QString)"), s)
        self.dlg.emit(QtCore.SIGNAL("scrolldown()"))
        QtGui.qApp.processEvents()

    def add_article(self, title, text, date, tags):
        tags = [tag.strip() for tag in tags.split(",")]
        pydate = datetime.strptime(date, "%Y-%m-%d")
        self.root.add_child(Article(title, text, tags, pydate))
        return 1

    def run(self, parent):
        egg = partial(PHPIng.print_cb, self)
        pyphp.log = egg
        pyphp.parent = parent
        pyphp.add_article = self.add_article
        if pyphp.init() != 0:
            return
        self.dlg = Dialog(parent)
        self.dlg.setModal(True)
        self.dlg.show()
        self.root = Article()
        try:
            pyphp.execute(os.path.join(scriptpath, "script.php"))
            self.print_cb(u"<font color=\"green\">*** Готово ***</font>")
        finally:
            pyphp.shutdown()
        return self.root
