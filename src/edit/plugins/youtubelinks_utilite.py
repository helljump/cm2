#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

try:
    from plugtypes import IUtilitePlugin #@UnresolvedImport
    from utils.formlayout import fedit
    from utils.qthelpers import MyProgressDialog
except ImportError:
    IUtilitePlugin = object

from PyQt4 import QtGui, QtCore
import time
import traceback
import re
import logging
#from engine.browser import Browser, FormMethod
import requests
import lxml.html

log = logging.getLogger(__name__)

TIMEOUT = 60
PROXYLIST = None

class SearchEngine(object):
    def __init__(self, timeout=30):
        self.sess = requests.session()
        if PROXYLIST:
            self.sess.proxies = {"http":random.choice(PROXYLIST)}

class YouTube(SearchEngine):
    URL = "http://www.youtube.com"
    def search(self, q):
        params = {"search_query": q, "aq": "f"}
        url = "%s/results" % self.URL
        while True:
            rc = self.sess.get(url, params=params)
            soup = lxml.html.fromstring(rc.text)
            """
            <a href="/watch?v=lDjIpvC_OUU" class="ux-thumb-wrap yt-uix-sessionlink yt-uix-contextlink contains-addto "
             data-sessionlink="ei=w0y7UeuYL4T7wQPaloHoCQ&amp;ved=CAQQwBs">
            """
            for row in soup.xpath("//a[contains(@class,'ux-thumb-wrap yt-uix-sessionlink yt-uix-contextlink contains-addto')]/@href"):
                egg = "%s%s" % (self.URL, row)
                yield egg
            """
            <a href="/results?search_query=%D0%A0%D0%BE%D0%B1%D0%BE%D1%82%D1%8B&amp;page=2" class="yt-uix-button  yt-uix-pager-button yt-uix-sessionlink yt-uix-button-default" data-sessionlink="ei=CMKrhJPLmrUCFSWScAod_S3FiA%3D%3D" data-page="2"><span class="yt-uix-button-content">Следующая »</span></a>
            """
            egg = soup.xpath("//a[contains(@class,'yt-uix-pager-button')]/@href")
            if not egg:
                raise StopIteration()
            url = "%s%s" % (self.URL, egg[-1])

class Dialog(QtGui.QDialog):
    def __init__(self, links, parent):
        super(Dialog, self).__init__(parent)
        self.setWindowTitle(u"YouTube ссылки")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(500, 500 * 0.75)
        layout = QtGui.QGridLayout(self)
        self.textedit = QtGui.QTextEdit(self)
        self.textedit.setText("\n".join(links))
        layout.addWidget(self.textedit, 0, 0)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        layout.addWidget(buttonBox, 1, 0)
        buttonBox.accepted.connect(self.accept)

class Thread(QtCore.QThread):
    def __init__(self, query, amount, pd, parent, timeout=30):
        super(Thread, self).__init__(parent)
        self.error = None
        self.query = query
        self.pd = pd
        self.amount = amount
        self.timeout = timeout
    def run(self):
        try:
            self.result = []
            self.pd.set_text(u"Получение данных")
            it = YouTube(self.timeout).search(self.query)
            c = 0
            for link in it:
                if link in self.result:
                    self.result.append(link) # хм, уже в списке
                else:
                    self.result.append(link)
                c += 1
                self.pd.set_value(c)
                if c>self.amount:
                    break
        except:
            self.error = traceback.format_exc()

class Plugin(IUtilitePlugin):
    def run(self, parent):
        datalist = [(u"Запрос:", u"роботы"), (u"Количество:", 100)]
        rc = fedit(datalist, title=u"YoutTube ссылки", parent=parent)
        if not rc:
            return
        query, amount = rc
        pd = MyProgressDialog(u"YoutTube ссылки", u"Подключение к серверу",
                              u"Отмена", 0, amount, parent)
        pd.setFixedWidth(320)
        pd.show()
        tout = parent.config_dialog.config.get('connect_timeout', 15)
        th = Thread(query, amount, pd, parent, timeout=tout)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.terminate()
                break
            time.sleep(0.0123)
            QtGui.qApp.processEvents()
        pd.close()
        if th.error:
            parent.errmsg.setWindowTitle(u"Ошибка обработки")
            parent.errmsg.showMessage(th.error)
        elif th.result:
            dlg = Dialog(th.result, parent)
            dlg.exec_()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    y = YouTube()
    for row in y.search(u"Роботы"):
        print row
