#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QThread
import xmlrpclib
import logging 
from utils.formlayout import fedit
import socket
import traceback 

log = logging.getLogger(__name__)

class ExportThread(QThread):
    def __init__(self, tree, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.tree = tree
        self.pd = progressdialog
        self.parent = parent        
    def run(self):
        try:
            self.write()
        except:
            log.exception("export error")
            self.error = traceback.format_exc()
    def stop(self):
        log.debug("terminate")
        self.terminate()
        log.debug("wait")
        self.wait()
                
class Export(ExportThread):
    
    def testConnection(self, rc, parent):
        try:
            (url, timeout) = rc
            socket.setdefaulttimeout(timeout)
            conn = xmlrpclib.ServerProxy(url)
            if conn.check_connection():
                QtGui.QMessageBox.information(parent, u"Связь установлена", u"Удачно подключились")
            else:
                raise Exception("wrong answer")
        except:
            QtGui.QMessageBox.warning(parent, u"Ошибка",
                u"Ошибка подключения. Проверьте настройки.")
            log.exception("testConnection:")
    
    def config(self):
        datalist = [
            (u"Адрес CM2 XML-RPC сервера:", "http://localhost:8000"),
            (u"Таймаут:", 60)
        ]
        rc = fedit(datalist, title=u"Параметры экспорта",
            parent=self.parent, apply=self.testConnection)
        if not rc:
            return False
        (self.url, self.timeout) = rc
        return True

    def addArticle(self, item, parent_title):
        log.debug(u"addArticle %s", item.title)
        if self.pd:
            self.pd.set_text(u"Добавление статьи %s" % item.title)
        self.conn.new_article(parent_title, item.title, item.text, item.tags, item.date)

    def articles_count(self, root):
        def _recurse(item):
            egg = 1
            for subitem in item.get_children():
                egg += _recurse(subitem)
            return egg
        return _recurse(root)

    def write(self):
        socket.setdefaulttimeout(self.timeout)
        self.conn = xmlrpclib.ServerProxy(self.url)
        
        def recurse_tree(tree):
            for item in tree.get_children():
                self.addArticle(item, tree.title)
                recurse_tree(item)
                if self.pd:
                    self.pd.set_value(self.pd.value() + 1)
                    
        if self.pd:
            self.pd.set_range(0, self.articles_count(self.tree))
            
        recurse_tree(self.tree)

if __name__ == "__main__":
    import shelve, cPickle
    fname = r"d:\work\promidol\src\edit\snoa_ru.prt"
    finp = shelve.open(fname, protocol=cPickle.HIGHEST_PROTOCOL)
    root = finp["root"]
    finp.close()

    writer = Export(root)
    writer.config()
    writer.write()
