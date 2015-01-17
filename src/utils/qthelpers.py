#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QDateTimeEdit, QCalendarWidget
from PyQt4.QtCore import Qt
from logging import debug
import os
import pyDes
import hashlib
from UserString import UserString
import sys
import datetime, time
import random

def flatter(root, skip_empty=True):
    def _recurse(item):
        sublist = []
        for subitem in item.children:
            if skip_empty and len(subitem.text) == 0:
                pass
            else:
                sublist.append(subitem)
            spam = _recurse(subitem)
            sublist.extend(spam)
        return sublist
    flatlist = _recurse(root)
    debug("flatter size: %i", len(flatlist))
    return flatlist

class MyFile(UserString):
    def __init__(self, data, mask="Text File(*.*)", mode="r"):
        super(MyFile, self).__init__(data)
        self.mode = mode
        self.mask = mask
    def __unicode__(self):
        return self.data
        
class MyPath(UserString):
    def __unicode__(self):
        return self.data
    
class MyString(UserString):
    def __init__(self, data, width, height):
        super(MyString, self).__init__(data)
        self.width = width
        self.height = height
    def __unicode__(self):
        return self.data

class MyDirEdit(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.lineEdit = QtGui.QLineEdit(self)
        layout.addWidget(self.lineEdit, 0, 0, 1, 1)
        toolButton = QtGui.QToolButton(self)
        toolButton.setText("...")
        toolButton.setAutoRaise(True)
        layout.addWidget(toolButton, 0, 1, 1, 1)
        self.textChanged = self.lineEdit.textChanged
        toolButton.clicked.connect(self.select_dir)
    def text(self):
        return self.lineEdit.text()
    def setText(self, s):
        return self.lineEdit.setText(unicode(s))
    def select_dir(self):
        fileName = QtGui.QFileDialog.getExistingDirectory(self, u"", self.text())
        if not fileName:
            return 
        self.setText(fileName)

hasher = "do8fg1243fviubg237fgilowdffv139f424a1e7f4c0b2a33e56b8asdvcrgbwret435e20"

class MyFileEdit(QtGui.QWidget):
    def __init__(self, parent, fname, mask, mode="w"):
        QtGui.QWidget.__init__(self, parent)
        self.fname = fname
        self.mask = mask
        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.lineEdit = QtGui.QLineEdit(self)
        layout.addWidget(self.lineEdit, 0, 0, 1, 1)
        toolButton = QtGui.QToolButton(self)
        toolButton.setText("...")
        toolButton.setAutoRaise(True)
        layout.addWidget(toolButton, 0, 1, 1, 1)
        self.textChanged = self.lineEdit.textChanged
        toolButton.clicked.connect(self.select_file)
        self.mode = mode
        self.setText(fname)
    def text(self):
        return self.lineEdit.text()
    def setText(self, s):
        return self.lineEdit.setText(unicode(s))
    def select_file(self):
        #print self.fname
        egg = os.path.split(self.fname)
        if self.mode == "w":
            fileName = QtGui.QFileDialog.getSaveFileName(self, u"Сохранить файл...", self.fname, self.mask)
        else:
            fileName = QtGui.QFileDialog.getOpenFileName(self, u"Открыть файл...", egg[0], self.mask)
        if not fileName: 
            return 
        self.setText(fileName)
        self.fname = unicode(fileName)

class RndDateTimeEdit(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)       
        
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        
        self.button = QtGui.QToolButton(maximumWidth=22)
        self.button.setText("rnd")
        self.button.setToolTip(u"Случайная дата")
        self.button.setIcon(QtGui.QIcon(":/ico/img/arrow_rotate_clockwise.png"))
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.clicked.connect(self.set_rnd)
        self.dtedit = QtGui.QDateTimeEdit()
        
        layout.addWidget(self.dtedit)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def set_rnd(self,text):
        date_to = datetime.datetime.now()
        date_from = datetime.datetime(2000,1,1,0,0,0)
        a = time.mktime(date_from.timetuple())
        b = time.mktime(date_to.timetuple())
        rnd = random.randint(a, b)
        egg = datetime.datetime.fromtimestamp(rnd)
        self.dtedit.setDateTime(egg)
        
    def __getattr__(self, attr):
        return getattr(self.dtedit, attr)

        
class MyDateTimeEdit(QDateTimeEdit):
    def __init__(self, parent=None):
        QDateTimeEdit.__init__(self, parent)
        self.button=QtGui.QToolButton(self)
        self.button.setCursor(Qt.ArrowCursor)
        self.button.show()
        self.button.setText("...")
        self.button.setFocusPolicy(Qt.NoFocus)
        #self.button.setIcon(QtGui.QIcon.fromTheme("edit-clear"))
        #self.button.setStyleSheet("border: none;")
        self.button.clicked.connect(self.set_rnd)

        layout=QtGui.QVBoxLayout(self)
        layout.addWidget(self.button, 0, Qt.AlignLeft)
        layout.setSpacing(0)
        layout.setMargin(0)
        
        debug("set MyDateTimeEdit")

    def set_rnd(self,text):
        pass

    def sizeHint(self):
        qs.setWidth(5)
        return qs
        
        
class MyDateEdit(QDateTimeEdit):
    def __init__(self, parent=None):
        QDateTimeEdit.__init__(self, parent)
        self.setCalendarPopup(True)
        self.__cw = None
        self.setDisplayFormat("dd MMMM yyyy hh:mm:ss")

    def mousePressEvent(self, event):
        QDateTimeEdit.mousePressEvent(self, event)
        if not self.__cw:
            self.__cw = self.findChild(QCalendarWidget)
            if self.__cw:
                self.__cw.setFirstDayOfWeek(Qt.Monday)

                
def gen(params):
    d = pyDes.des(hasher[5:13], padmode=pyDes.PAD_PKCS5)
    egg = hashlib.sha384()
    egg.update(hasher[9:23])
    for v in sorted(params.values()):
        egg.update(str(v))
    egg = d.encrypt(egg.digest())
    return "".join(egg)

class MyProgressDialog(QtGui.QProgressDialog):
    def __init__(self, title, label, cancel, from_, to_, parent):
        QtGui.QWidget.__init__(self, label, cancel, from_, to_, parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setValue(from_)
        self.setMinimumDuration(1)
        self.setFixedWidth(400)
        self.connect(self, QtCore.SIGNAL("set_value(int)"), 
                     self, QtCore.SLOT("setValue(int)"))
        self.connect(self, QtCore.SIGNAL("set_range(int,int)"), 
                     self, QtCore.SLOT("setRange(int,int)"))
        self.connect(self, QtCore.SIGNAL("set_text(QString)"), 
                     self, QtCore.SLOT("setLabelText(QString)"))
        
    def inc_value(self, v=1):
        egg = self.value() + v
        self.emit(QtCore.SIGNAL("set_value(int)"), int(egg))
        
    def set_value(self, value):
        self.emit(QtCore.SIGNAL("set_value(int)"), int(value))
        #QtGui.qApp.processEvents()
        
    def set_range(self, _from, _to):
        self.emit(QtCore.SIGNAL("set_range(int,int)"), int(_from), int(_to))
        #QtGui.qApp.processEvents()
        
    def set_text(self, text):
        self.emit(QtCore.SIGNAL("set_text(QString)"), unicode(text))
        #QtGui.qApp.processEvents()

class ToolBarWithPopup(QtGui.QToolBar):
    def __init__(self, parent, style=QtCore.Qt.ToolButtonTextUnderIcon, *args):    
        QtGui.QWidget.__init__(self, parent, *args)
        self.setToolButtonStyle(style)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_toolbar_menu)
        
    def show_toolbar_menu(self, p):
        menu = QtGui.QMenu(self)
        menu.addAction(self.tr("Only icons"),
                       lambda : self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly))
        menu.addAction(self.tr("Text beside icon"),
                       lambda : self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon))
        menu.addAction(self.tr("Text under icon"),
                       lambda : self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon))
        menu.exec_(QtGui.QCursor.pos())

def setMargin(layout):
    pass
    #layout.setMargin(4)
    #layout.setSpacing(2)

class MyToolButton(QtGui.QToolButton):
    def __init__(self, parent, text, icon, action=None, beside=False):
        QtGui.QWidget.__init__(self, parent)
        self.setText(text)
        self.setToolTip(text)
        self.setIcon(QtGui.QIcon(icon))
        if beside:
            self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setIconSize(QtCore.QSize(20, 20))
        if action:
            self.clicked.connect(action)

def addPopup(widget, callback, selection=True):
    '''добавляет контекстное меню к виджету и правит метод выделения'''
    if selection:
        widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    QtCore.QObject.connect(widget, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), callback)
