#! /usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
import os
import Queue

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport

log = logging.getLogger(__name__)

class ProgressDialog(QProgressDialog):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setWindowModality(Qt.WindowModal)
        self.setFixedWidth(320)
        self.connect(self, SIGNAL("setValue(int)"), self, SLOT("setValue(int)"))
        self.connect(self, SIGNAL("setText(QString)"), self, SLOT("setLabelText(QString)"))
        self.connect(self, SIGNAL("incValue()"), self.inc_value)
    def inc_value(self):
        self.setValue(self.value() + 1)

class ProgressLogDialog(QDialog):
    def __init__(self, title, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.resize(400, 400 * 0.75)
        l = QGridLayout(self)
        self.label = QLabel(self)
        l.addWidget(self.label)
        self.progress = QProgressBar(self)
        l.addWidget(self.progress)
        self.tlog = QTextEdit(self)
        self.tlog.setReadOnly(True)
        l.addWidget(self.tlog)
    def set_label(self, text):
        self.label.setText(text)
    def set_range(self, from_, to_):
        self.progress.setRange(from_, to_)
        self.set_value(0)
    def set_value(self, v):
        self.progress.setValue(v)
    def get_value(self):
        return self.progress.value()
    def get_max(self):
        return self.progress.maximum()
    def inc_value(self, v=1):
        self.progress.setValue(self.progress.value()+1)
    def log(self, s):
        self.tlog.append(s)
        self.tlog.ensureCursorVisible()
    def clear(self):
        self.tlog.clear()
        self.set_range(0,0)

class ToolBar(QToolBar):
    def __init__(self, parent, style=Qt.ToolButtonTextBesideIcon, *args):
        QWidget.__init__(self, parent, *args)
        self.setToolButtonStyle(style)
        self.setIconSize(QSize(20, 20))

class Button(QToolButton):
    SIZE = 100
    def __init__(self, icon, text, action, parent):
        QPushButton.__init__(self, parent)
        self.setIconSize(QSize(32,32))
        self.setIcon(QIcon(icon))
        self.setMinimumWidth(64)
        self.setText(text)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.clicked.connect(action)

class FileEdit(QWidget):
    def __init__(self, fname, mask, mode="r", parent=None):
        QWidget.__init__(self, parent)
        self.fname = fname
        self.mask = mask
        layout = QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.lineEdit = QLineEdit(self)
        layout.addWidget(self.lineEdit, 0, 0, 1, 1)
        toolButton = QToolButton(self)
        toolButton.setText("...")
        toolButton.setAutoRaise(True)
        layout.addWidget(toolButton, 0, 1, 1, 1)
        self.textChanged = self.lineEdit.textChanged
        toolButton.clicked.connect(self.select_file)
        self.mode = mode
    def text(self):
        return self.lineEdit.text()
    def setText(self, s):
        return self.lineEdit.setText(s)
    def select_file(self):
        egg = os.path.split(self.fname)
        if self.mode == "w":
            fileName = QFileDialog.getSaveFileName(self, u"Сохранить файл...", 
                egg[0], self.mask)
        else:
            fileName = QFileDialog.getOpenFileName(self, u"Открыть файл...", 
                egg[0], self.mask)
        if not fileName:
            return 
        self.setText(fileName)
        self.fname = unicode(fileName)

class Worker(QThread):
    def __init__(self, queue, parent=None):
        QThread.__init__(self, parent)
        self.queue = queue
        self.online = True
    def run(self):
        log.debug("start %s" % QThread.currentThread())
        while self.online:
            try:
                task = self.queue.get_nowait()
                result = task()
                self.emit(SIGNAL('taskDone(PyQt_PyObject)'), result)
            except Queue.Empty:
                QThread.usleep(10)
        log.debug("stop %s" % QThread.currentThread())
    def die(self):
        self.online = False
        self.wait(100)
        self.terminate()

