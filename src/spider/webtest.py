#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
log = logging.getLogger(__name__)

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *


class MyWebView(QWebView):
    qrect = None
    qpoint = None

    def __init__(self, parent=None):
        super(MyWebView, self).__init__(parent)
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.linkClicked.connect(self.alt_click)

    def alt_click(self, url):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            self.load(url)

    def dompath(self, elem):
        egg = elem.tagName()
        attrs = ["@%s=\"%s\"" % (name, elem.attribute(name)) for name in elem.attributeNames() if name in ["id", "class"]]
        if attrs:
            egg += "[%s]" % " and ".join(attrs)
        if elem.tagName():
            egg = self.dompath(elem.parent()) + "/" + egg
        return egg

    def mousePressEvent(self, e):
        QWebView.mousePressEvent(self, e)
        pos = e.pos()
        page = self.page()
        frame = page.frameAt(pos)
        self.qpoint = frame.scrollPosition()
        content = frame.hitTestContent(pos)
        elem = content.enclosingBlockElement() #.element()
        self.qrect = elem.geometry()
        self.repaint()
        print "/" + self.dompath(elem)

    def paintEvent(self, e):
        QWebView.paintEvent(self, e)
        if not self.qrect:
            return
        qp = QPainter()
        qp.begin(self)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        xp1, yp1, xp2, yp2 = self.qrect.getRect()
        xp1 -= self.qpoint.x()
        yp1 -= self.qpoint.y()
        qp.setPen(pen)
        qp.drawRect(xp1, yp1, xp2, yp2)
        qp.end()
        self.qrect = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    web = MyWebView()
    web.load(QUrl("http://gorodbaku.ru"))
    web.show()
    sys.exit(app.exec_())
