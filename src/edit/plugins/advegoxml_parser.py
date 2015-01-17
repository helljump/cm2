#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

try:
    from plugtypes import IImportPlugin #@UnresolvedImport
except ImportError:
    IImportPlugin = object
from lxml import etree
from utils.article import Article
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
from utils.formlayout import fedit
from utils.qthelpers import MyProgressDialog
import time
from datetime import datetime
import traceback

class Thread(QThread):
    def __init__(self, rc, pd, parent):
        super(Thread, self).__init__(parent)
        self.error = None
        self.pd = pd
        self.rc = rc
    def run(self):
        try:
            self.pd.set_text(u"Получение данных")
            tree = etree.parse(self.rc[0]) # 0:url
            root = Article()
            for item in tree.iterfind("{http://www.w3.org/2005/Atom}entry"):
                title = item.find("{http://www.w3.org/2005/Atom}title").text
                published = item.find("{http://www.w3.org/2005/Atom}published").text
                try:
                    pubdate = datetime.strptime(published, "%a %b %d %H:%M:%S %Z %Y")
                except ValueError:
                    pubdate = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                text = item.find("{http://www.w3.org/2005/Atom}content").text
                root.add_child(Article(title, text, date = pubdate))
                self.result = root
        except Exception, err:
            print err
            self.error = traceback.format_exc()

default = "http://advego.ru/order/atom/"

class Plugin(IImportPlugin):
    def run(self, parent):
        datalist = [(u"Адрес ленты:", default),
                    (None, u"пример: <i>http://advego.ru/order/atom/123456/789012/34567890.xml</i>")]
        rc = fedit(datalist, title=u"Advego XML импорт", parent=parent)
        if not rc:
            return
        pd = MyProgressDialog(u"Импорт", u"Подключение к серверу", u"Отмена", 
                              0, 0, parent)
        pd.setFixedWidth(320)
        pd.show()
        th = Thread(rc, pd, parent)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.terminate()
                break
            time.sleep(0.0123)
            qApp.processEvents()
        pd.close()
        if th.error:
            parent.errmsg.setWindowTitle(u"Ошибка импорта")
            parent.errmsg.showMessage(th.error)
        return th.result

if __name__ == "__main__":
    pass
    #import sys
    #app = QApplication(sys.argv)
    #Plugin().run(None)
