#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = 'helljump'


from lxml import html
import sys
import spynner
from urlparse import urlsplit
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import codecs
import os


class SpynnerDialog(QDialog):

    USERAGENT = "Mozilla/5.0 (Windows NT 6.1; rv:17.0.2) Gecko/20100101 Firefox/17.0.2"

    def __init__(self, parent):
        spynner.SpynnerQapplication = qApp
        QDialog.__init__(self, parent)
        self.setWindowTitle(u'Импорт')
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(640, 480)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setMargin(0)
        self.browser = spynner.Browser(debug_level=spynner.WARNING, user_agent=SpynnerDialog.USERAGENT)
        self.browser.set_html_parser(html.fromstring)
        self.browser.set_url_filter(self._filter_ext)
        self.browser.create_webview()
        self.browser.show(False)
        self.gridLayout.addWidget(self.browser.webview, 0, 0)
        self.gridLayout.setRowStretch(0, 1)
        self.sb = QStatusBar(self)
        self.gridLayout.addWidget(self.sb, 1, 0)

    def message(self, s):
        self.sb.showMessage(s)

    def _filter_ext(self, operation, url):
        egg = urlsplit(url)
        if egg[2].lower()[-3:] in ['jpg', 'png', 'gif', 'css']:
            return False
        else:
            return True

    def __getattr__(self, attr):
        try:
            return getattr(self.browser, attr)
        except AttributeError:
            return getattr(self, attr)

    def closeEvent(self, rc):
        self.browser.hide()
        self.browser.webview.stop()
        self.browser.destroy_webview()

    def extract_image(self, selector, frmt='PNG'):
        """выделение данных изображение из QWebElement"""
        el = self.browser.webframe.findFirstElement(selector)
        image = QImage(el.geometry().size(), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        el.render(painter)
        painter.end()
        buf = QBuffer()
        image.save(buf, frmt)
        return buf.data().data()

    def dump(self):
        dn = os.path.join(os.path.dirname(__file__), 'dump.html')
        fout = codecs.open(dn, 'wb', 'UTF-8', 'replace')
        fout.write(self.html)
        fout.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = SpynnerDialog(None)
    dlg.show()
    dlg.message(u'Подключаемся')
    dlg.load('http://www.rusarticles.com/', load_timeout=60)
    dlg.wait_load(30)
    dlg.dump()
