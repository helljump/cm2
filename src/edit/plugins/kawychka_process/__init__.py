#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__date__ = "06.11.2010 23:45:20"
__author__ = "snöa"

import os
scriptpath = os.path.join(*__file__.split(os.path.sep)[-3:-1])
from functools import partial
from plugtypes import IProcessPlugin #@UnresolvedImport
from PyQt4 import QtGui, QtCore
from utils.qthelpers import MyProgressDialog
import pyphp
import time

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

class PHPIng(IProcessPlugin):
    def print_cb(self, s):
        if type(s) is not unicode:
            s = unicode(s,"utf-8","replace")
        self.dlg.emit(QtCore.SIGNAL("debug(QString)"), s)
        self.dlg.emit(QtCore.SIGNAL("scrolldown()"))
        QtGui.qApp.processEvents()

    def run(self, items, parent):
        egg = partial(PHPIng.print_cb, self)
        pyphp.log = egg
        if pyphp.init() != 0:
            return
        self.dlg = Dialog(parent)
        self.dlg.show()
        try:
            for item in items:
                if not self.dlg.isVisible():
                    break
                text = item.article.text.encode("utf-8")
                title = item.article.title.encode("utf-8")
                if hasattr(item.article, "intro"):
                    intro = item.article.intro
                else:
                    intro = u""
                tags = ",".join(item.article.tags).encode("utf-8")
                
                itemparent = item.parent()
                if itemparent:
                    pyphp.set_var("category", itemparent.article.title.encode("utf-8"))
                else:
                    pyphp.set_var("category", u"".encode("utf-8"))
                
                pyphp.set_var("text", text)
                pyphp.set_var("title", title)
                pyphp.set_var("intro", intro.encode("utf-8"))
                pyphp.set_var("tags", tags)
                pyphp.set_var("pubdate", item.article.date.isoformat())
                
                pyphp.execute(os.path.join(scriptpath, "script.php"))
                
                item.article.text = pyphp.get_var("text").decode("utf-8")
                item.article.title = pyphp.get_var("title").decode("utf-8")
                intro = pyphp.get_var("intro").decode("utf-8")
                if intro:
                    item.article.intro = intro
                item.article.tags = pyphp.get_var("tags").decode("utf-8").split(",")
                
                time.sleep(0.013)
            self.print_cb(u"<font color=\"green\">*** Готово ***</font>")
        finally:
            pyphp.shutdown()
