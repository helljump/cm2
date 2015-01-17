#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

import logging
log = logging.getLogger(__name__)

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport

from utils.qthelpers import ToolBarWithPopup, MyProgressDialog
from utils.formlayout import fedit
from commands import DeleteArticlesCommand
import operator
import icons #@UnusedImport
from edit.leven import Unic
import time

class PagesListModel(QAbstractTableModel):
    """хранит MyTreeItem """

    def __init__(self, parent):
        QAbstractTableModel.__init__(self)
        self.parent = parent
        self.labels = [u"Страница", u"Страница", u"Совпадение(%)"]
        self.cache = []
    def rowCount(self, parent):
        return len(self.cache)
    def columnCount(self, parent):
        return len(self.labels)
    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return QVariant()
        row = index.row()
        col = index.column()
        egg = self.cache[row]
        if col == 0:
            parent = '-' if egg[0].parent() is None else egg[0].parent().title
            value = "%s (%s)" % (egg[0].title, parent)
        elif col == 1:
            if egg[1].parent():
                value = "%s (%s)" % (egg[1].title, egg[1].parent().title)
            else:
                value = u"Удалён"
        elif col == 2:
            value = self.cache[row][2]
        return QVariant(value)
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section + 1)
        return QVariant()
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    def sort(self, col, order):
        colkey = operator.itemgetter(col)
        reverse = order != Qt.AscendingOrder
        self.cache.sort(key=colkey, reverse=reverse)
        ifrom = self.createIndex(0, 0)
        ito = self.createIndex(len(self.cache), len(self.labels))
        self.dataChanged.emit(ifrom, ito)
    def removeRows(self, pos, rows, index=QModelIndex()):
        self.beginRemoveRows(index, pos, pos + rows - 1);
        for i in range(rows): #@UnusedVariable
            self.cache.pop(pos)
        self.endRemoveRows()
        return True
    def appendRow(self, item1, item2, ratio, index=QModelIndex()):
        egg = len(self.cache)
        self.beginInsertRows(index, egg, egg);
        self.cache.append((item1, item2, ratio))
        self.endInsertRows()

class ViewDialog(QDialog):
    def __init__(self, item1, item2, parent=None):
        QWidget.__init__(self, parent)
        self.item1 = item1
        self.item2 = item2
        self.parent = parent
        self.setWindowTitle(u"Просмотр повторов")
        self.resize(700, 700 * 0.75)
        layout = QGridLayout(self)

        le = QLineEdit(self)
        le.setReadOnly(True)
        le.setText(self.item1.title)
        layout.addWidget(le, 0, 0)

        le = QLineEdit(self)
        le.setReadOnly(True)
        le.setText(self.item2.title)
        layout.addWidget(le, 0, 1)

        le = QLineEdit(self)
        le.setReadOnly(True)
        if self.item1.parent():
            le.setText(self.item1.parent().title)
        layout.addWidget(le, 1, 0)

        le = QLineEdit(self)
        le.setReadOnly(True)
        if self.item2.parent():
            le.setText(self.item2.parent().title)
        layout.addWidget(le, 1, 1)

        item1_te = QPlainTextEdit(self)
        s1 = item1_te.verticalScrollBar()
        item1_te.setReadOnly(True)
        item1_te.setPlainText(self.item1.article.text)
        layout.addWidget(item1_te, 2, 0)

        item2_te = QPlainTextEdit(self)
        s2 = item2_te.verticalScrollBar()
        item2_te.setReadOnly(True)
        item2_te.setPlainText(self.item2.article.text)
        layout.addWidget(item2_te, 2, 1)

        self.connect(s1, SIGNAL("valueChanged(int)"), s2, SLOT("setValue(int)"))

        tb = ToolBarWithPopup(self, style=Qt.ToolButtonTextBesideIcon)
        tb.addAction(QIcon(":/ico/img/page_delete.png"), u"&Удалить",
                     lambda i=self.item1: self.delete_page(i))
        layout.addWidget(tb, 3, 0)

        tb = ToolBarWithPopup(self, style=Qt.ToolButtonTextBesideIcon)
        tb.addAction(QIcon(":/ico/img/page_delete.png"), u"&Удалить",
                     lambda i=self.item2: self.delete_page(i))
        layout.addWidget(tb, 3, 1)

    def delete_page(self, item):
        self.parent.delete_page(item)
        self.hide()

class CheckDialog(QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle(u"Проверка уникальности")
        self.resize(800, 800 * 0.75)
        layout = QGridLayout(self)
        tb = ToolBarWithPopup(self, style=Qt.ToolButtonTextBesideIcon)
        tb.addAction(QIcon(":/ico/img/zoom.png"), u"&Просмотр", self.view_page)
        tb.addAction(QIcon(":/ico/img/delete_all.png"), u"&Удалит все дубли", self.delete_all)
        layout.addWidget(tb)
        self.table = QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setDefaultSectionSize(
            self.table.verticalHeader().fontMetrics().height()*2 + 8)
        model = PagesListModel(self.table)
        self.table.setModel(model)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.table.doubleClicked.connect(self.view_page)
        self.pd = MyProgressDialog(u"Проверка уникальности", u"Обработка", u"Отмена", 0, 0, self)
    def view_page(self):
        rows = [ndx.row() for ndx in self.table.selectedIndexes() if ndx.column() == 0]
        if not rows:
            return
        row = self.table.model().cache[rows[-1]]
        item1 = row[0]
        item2 = row[1]
        dlg = ViewDialog(item1, item2, self)
        dlg.exec_()
    def delete_page(self, item):
        model = self.table.model()
        self.pd.set_range(0, len(model.cache))
        self.pd.set_value(0)
        self.pd.set_text(u"Удаление статей")
        def filter_item(row):
            self.pd.inc_value()
            if row[0] is item or row[1] is item:
                return False
            return True
        model.cache = filter(filter_item, model.cache)
        model.reset()
        tree = self.parent().treeWidget.tree
        command = DeleteArticlesCommand(tree)
        parent = item.parent() or tree.invisibleRootItem()
        index = parent.indexOfChild(item)
        command.append_item(parent, index)
        self.parent().undo_stack.push(command)

    def delete_all(self):
        amount = 0
        egg = []
        tree = self.parent().treeWidget.tree
        command = DeleteArticlesCommand(tree)
        for row in self.table.model().cache:
            #print '.',
            item = row[1]
            parent = item.parent() or tree.invisibleRootItem()
            index = parent.indexOfChild(item)
            if (parent, index) not in egg:
                egg.append((parent, index))
                command.append_item(parent, index)
                parent.takeChild(index)
        self.parent().undo_stack.push(command)
        QMessageBox.question(self, u"Удаление дублей",
            u"Удалено %i повторяющихся материалов. Что скажете?" % len(egg), u"Неплохо")
        self.hide()

def run(articles, parent):
    dlg = CheckDialog(parent)
    dlg.setModal(True)
    dlg.show()
    datalist = [(u"Размер шингла(слов)", 5),
                (u"Совпадений более(%)", 60)]
    rc = fedit(datalist, title=u"Проверка уникальности", parent=dlg)
    if not rc:
        dlg.hide()
        return
    added = []
    dlg.pd.set_text(u"Расчет сумм")
    dlg.pd.set_range(0, 0)
    uniclist = [[Unic(item.article.text, rc[0]), item] for item in articles]
    dlg.pd.set_range(0, len(uniclist))
    dlg.pd.set_value(0)
    dlg.pd.set_text(u"Поиск")
    for item1 in uniclist:
        for item2 in uniclist:
            if item1 is item2:
                continue
            matches = len(item1[0] & item2[0])
            if not matches:
                continue
            maxlen = max([len(item1[0]), len(item2[0])])
            ratio = 100.0 / maxlen * matches
            if ratio > rc[1] and item2 not in added:
                added.append(item1)
                dlg.table.model().appendRow(item1[1], item2[1], ratio)
            qApp.processEvents()
        if dlg.pd.wasCanceled():
            break
        dlg.pd.inc_value()
        time.sleep(0.012)
    dlg.pd.set_value(len(articles))
    dlg.exec_()
