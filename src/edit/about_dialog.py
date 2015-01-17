#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import sys
from PyQt4 import QtCore, QtGui
from updater import get_version

sver = get_version()

changes = u"""<h2>Список изменений в версии %s</h2>
<p>
<ul>
    <li>Исправлена ошибка с гобонизаторе</li>
    <li>Обновлена сетевая библиотека</li>
    <li>Улучшена работы модуля морфологии. Теперь он еще точнее определяет словоформу.</li>
</ul>
</p>
""" % sver


class AboutDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        self.setWindowTitle(u"Content Monster 2 TreeEdit free")
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.resize(500, 300)

        layout = QtGui.QGridLayout(self)

        self.about_tb = QtGui.QTextEdit(self)
        self.about_tb.setReadOnly(True)
        layout.addWidget(self.about_tb, 0, 0, 1, 1)

        bbox = QtGui.QDialogButtonBox(self)
        bbox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.connect(bbox, QtCore.SIGNAL("accepted()"), self.accept)
        layout.addWidget(bbox, 1, 0, 1, 1)

        self.about_tb.setHtml(changes)
        #self.about_tb.mouseReleaseEvent = self.test
        self.about_tb.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonRelease and source is self.about_tb.viewport()):
            s = self.about_tb.anchorAt(event.pos())
            if s:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(s))
            return True
        return QtGui.QWidget.eventFilter(self, source, event)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    AboutDialog().exec_()
