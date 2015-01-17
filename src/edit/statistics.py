#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
import re
from utils.qthelpers import MyProgressDialog
from utils.tidy import html_tags_re

def ShowStatistics(arts, parent):
    
    despace = re.compile("\s")
    
    pd = MyProgressDialog(u"Сбор статистики", u"Обработка", u"Отмена", 0, len(arts), parent)
    pd.setFixedWidth(320)
    pd.show()
    cats_amount = 0
    arts_amount = 0
    tags = set()
    total_chars = 0
    total_chars_wospace = 0
    for item in arts:
        
        if item.childCount():
            cats_amount += 1
        else:
            arts_amount += 1
            
        for tag in item.article.tags:
            tags.add(tag)
        
        egg = html_tags_re.sub("", unicode(item.article.text))
        total_chars += len(egg)
        egg = despace.sub("", egg)
        total_chars_wospace += len(egg)

        pd.set_text(item.article.title)
        pd.set_value(pd.value() + 1)
        if pd.wasCanceled():
            break
    else:
        dlg = QtGui.QDialog(parent)
        dlg.setWindowTitle(u"Статистика")
        dlg.layout = QtGui.QFormLayout(dlg)
        dlg.layout.addRow(u"Страниц всего:", QtGui.QLabel("%i" % (len(arts))))
        dlg.layout.addRow(u"Категорий:", QtGui.QLabel("%i" % (cats_amount)))
        dlg.layout.addRow(u"Статей:", QtGui.QLabel("%i" % (arts_amount)))
        dlg.layout.addRow(u"Меток:", QtGui.QLabel("%i" % len(tags)))
        dlg.layout.addRow(u"Знаков:", QtGui.QLabel("%i" % total_chars))
        dlg.layout.addRow(u"Знаков без пробелов:", QtGui.QLabel("%i" % total_chars_wospace))
        buttonBox = QtGui.QDialogButtonBox(dlg)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        dlg.layout.addRow(buttonBox)
        buttonBox.accepted.connect(dlg.accept)
        dlg.exec_()
    pd.close()
