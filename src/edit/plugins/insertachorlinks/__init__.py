#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

try:
    from plugtypes import IProcessPlugin
except ImportError:
    IProcessPlugin = object
from helpers import ProgressLogDialog, ToolBar, Worker
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging 
import random
import sys
from itertools import cycle
import operator
import ires
from inserter import Inserter
import Queue
import os

LANGS = [("russian", u"Русский"),("english", u"Английский"),("german", u"Немецкий")]

class Task(object):
    def __init__(self, obj, article):
        self.article = article
        self.obj = obj
    def __call__(self):
        try:    
            founded, self.article.text = self.obj.process(self.article.text)
            rc = (founded, self.article.title)
        except Exception, err:
            rc = err
        return rc
        
class Plugin(IProcessPlugin):
    def run(self, items, parent):        
        dlg = Dialog(parent)
        if not dlg.exec_():
            return
        self.pd = pd = ProgressLogDialog(u"Обработка статей", parent)
        pd.set_label(u"Вставка ссылок..")
        pd.setModal(True)
        pd.set_range(0,len(items))
        pd.show()
        test_dic = dlg.table.model().cache
        limit = dlg.limit_sb.value()
        lang = unicode(dlg.lang_cb.itemData(dlg.lang_cb.currentIndex()).toString())
        ins = Inserter(test_dic, limit, lang)
        queue = Queue.Queue()
        for item in items:
            queue.put(Task(ins, item.article))
        t = Worker(queue)
        QObject.connect(t, SIGNAL('taskDone(PyQt_PyObject)'), self.process_done)
        t.start()
        pd.exec_()
        t.die()
    def process_done(self, rc):
        if type(rc) is tuple:
            self.pd.log(u"Обработан: %s(%i)" % (rc[1], rc[0]))
        else:
            egg = rc.__str__()
            egg = unicode(egg, sys.getdefaultencoding(), "replace")
            self.pd.log(u"<font color=\"red\">Ошибка: %s</font>" % egg)
        self.pd.inc_value()
        if self.pd.get_value()==self.pd.get_max():
            self.pd.log(u"<b>Готово</b>")            

default_dict = [
    [u"счастье","http://schastie.ru"],
    [u"орган","http://organ.ru"],
    [u"рык","http://ryk.ru"],
    [u"отливал","http://litt.ru"]
]

class Model(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self)
        self.labels = [u"Анкор", u"Ссылка"]
        if not hasattr(sys, "frozen"):
            self.cache = default_dict
        else:
            self.cache = []
    def rowCount(self, parent=None):
        return len(self.cache)
    def columnCount(self, parent=None):
        return len(self.labels)
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section + 1)
        return QVariant()
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
    def sort(self, col, order):
        colkey = operator.itemgetter(col)
        reverse = order != Qt.AscendingOrder
        self.cache.sort(key=colkey, reverse=reverse)
        ifrom = self.createIndex(0, 0)
        ito = self.createIndex(self.rowCount(), self.columnCount())
        self.dataChanged.emit(ifrom, ito)                
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()
        row = index.row()
        col = index.column()
        value = self.cache[row][col]
        return QVariant(value)
    def setData(self, index, data, role):
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return False
        row = index.row()
        col = index.column()
        self.cache[row][col] = unicode(data.toString())
        return True
        
class Dialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Вставка ссылок по анкорам")
        self.resize(600, 600*0.75)
        l = QGridLayout(self)
        tb = ToolBar(self)
        tb.addAction(QIcon(":/add.png"), u"&Добавить", self.insert_row)
        tb.addAction(QIcon(":/delete.png"), u"&Удалить", self.remove_rows)
        tb.addAction(QIcon(":/page_white_put.png"), u"&Импорт", self.import_file)
        l.addWidget(tb)
        hl = QHBoxLayout()
        hl.addWidget(QLabel(u"Ссылок на статью(не более)"))
        self.limit_sb = QSpinBox(self)
        self.limit_sb.setValue(1)
        hl.addWidget(self.limit_sb)
        hl.addWidget(QLabel(u"Язык"))
        self.lang_cb = QComboBox(self)
        for row in LANGS:
            self.lang_cb.addItem(row[1], QVariant(row[0]))
        hl.addWidget(self.lang_cb)
        hl.addStretch(1)
        l.addLayout(hl,1,0)
        self.table = QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(
            self.table.verticalHeader().fontMetrics().height() + 4)
        model = Model(self.table)
        self.table.setModel(model)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        l.addWidget(self.table)
        bb = QDialogButtonBox(self)
        bb.setOrientation(Qt.Horizontal)
        bb.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        l.addWidget(bb)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)
    def import_file(self):
        fileName = QFileDialog.getOpenFileName(self, u"Импорт", self.parent().current_load_path,
            u"список ссылок (*.csv)")
        if not fileName:
            return
        fileName = unicode(fileName)
        self.parent().current_load_path = os.path.split(fileName)[0]
        cache = self.table.model().cache
        lines = open(fileName).readlines()
        self.table.model().beginInsertRows(QModelIndex(), 0, len(lines)-1)
        for row in lines:
            row = unicode(row,"utf-8")
            cache.append(row.split(";")[:2])
        self.table.model().endInsertRows()
    def insert_row(self):
        selected = self.table.selectedIndexes()
        if selected:
            last = selected[-1]
            row = last.row() + 1
        else:
            row = 0
        model = self.table.model()
        model.beginInsertRows(QModelIndex(), row, row)
        model.cache.insert(row, ["",""])
        model.endInsertRows()
    def remove_rows(self):
        rows = [ndx.row() for ndx in self.table.selectedIndexes() if ndx.column() == 0]
        rows.sort(reverse=True)
        model = self.table.model()
        for row in rows:
            model.beginRemoveRows(QModelIndex(), row, row);
            model.cache.pop(row)
            model.endRemoveRows()

def main():
    app = QApplication(sys.argv)
    Dialog().exec_()

if __name__ == "__main__":
    main()
