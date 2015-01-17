#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

"""
Диалог поиска в текущем тексте
"""

from PyQt4 import QtCore, QtGui
import itertools
import re
import logging

log = logging.getLogger(__name__)

class FindDialog(QtGui.QDialog):
    def __init__(self, parent, fulltext_widget, introtext_widget):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Поиск текста")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(320, 130)
        self.parent = parent
        self.textEdit = fulltext_widget
        self.introTextEdit = introtext_widget
        mainlayout = QtGui.QGridLayout(self)

        fields_l = QtGui.QFormLayout()
        self.find_le = QtGui.QLineEdit(self)
        self.find_le.textChanged.connect(self.clear)
        fields_l.addRow(u"Поиск", self.find_le)
        self.case_cb = QtGui.QCheckBox(u"С учетом регистра", self)
        self.case_cb.stateChanged.connect(self.clear)
        fields_l.addRow(self.case_cb)
        self.regex_cb = QtGui.QCheckBox(u"Regex", self)
        self.regex_cb.stateChanged.connect(self.clear)
        fields_l.addRow(self.regex_cb)
        #self.whole_cb = QtGui.QCheckBox(u"Фраза полностью", self)
        #self.whole_cb.stateChanged.connect(self.clear)
        #fields_l.addRow(self.whole_cb)
        self.wrap_cb = QtGui.QCheckBox(u"Зациклено", self)
        self.wrap_cb.stateChanged.connect(self.clear)
        self.wrap_cb.setChecked(True)
        fields_l.addRow(self.wrap_cb)
        
        buttons_l = QtGui.QFormLayout()
        find_pb = QtGui.QPushButton(u"Найти", self)
        find_pb.clicked.connect(self.cycle_find)
        buttons_l.addRow(find_pb)
        close_pb = QtGui.QPushButton(u"Закрыть", self)
        close_pb.clicked.connect(self.hide)
        buttons_l.addRow(close_pb)

        mainlayout.addLayout(fields_l, 0, 0)
        mainlayout.addLayout(buttons_l, 0, 1)

        self.clear()

        egg = ""
        if self.textEdit.hasSelectedText():
            egg = self.textEdit.selectedText()
        elif self.introTextEdit.hasSelectedText():
            egg = self.introTextEdit.selectedText()
        self.find_le.setText(egg)
        
        egg1 = unicode(self.textEdit.text())
        egg2 = unicode(self.introTextEdit.text()) if self.introTextEdit.isVisible() else ""
        self.fulltextborder = len(egg1)
        self.fulltext = "%s%s" % (egg1, egg2)
        
    def clear(self):
        self.finditer = None

    def cycle_find(self):
        egg = True
        cnt = 0
        while egg:
            egg = self.find()
            cnt += 1
            if cnt > 1:
                break

    def find(self):
        if not self.fulltext:
            return False
        if self.finditer:
            try:
                val = self.finditer.next()
                log.debug(val.span())
                t_from, t_to = val.span()
                if t_from < self.fulltextborder and t_to < self.fulltextborder:
                    self.textEdit.setFocus(True)
                    self.textEdit.setSelection(0, t_from, 0, t_to)
                    self.introTextEdit.setSelection(0, 0, 0, 0)
                else:
                    self.textEdit.setSelection(0, 0, 0, 0)
                    self.introTextEdit.setFocus(True)
                    self.introTextEdit.setSelection(0, t_from - self.fulltextborder
                        , 0, t_to - self.fulltextborder)
            except StopIteration:
                if self.finditer_backup:
                    self.finditer, self.finditer_backup = itertools.tee(self.finditer_backup)
                    #self.find()
                    return True
                else:
                    return False
        else:
            find_str = unicode(self.find_le.text())
            params = re.S | re.M | re.U
            if not self.case_cb.isChecked():
                params |= re.I
            if not self.regex_cb.isChecked(): 
                find_str = re.escape(find_str)
            self.finditer = re.finditer(find_str, self.fulltext, params)
            if not self.finditer:
                self.clear()
                return False
            if self.wrap_cb.isChecked():
                self.finditer, self.finditer_backup = itertools.tee(self.finditer)
            else:
                self.finditer_backup = None
            #self.find()
            return True
            
        return False
        
