#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

'''
TODO:
+добавление
+удаление
редактирование
+список
'''

from PyQt4 import QtCore, QtGui
import logging
import random

class Grunkreuz(object):
    def __init__(self, url, **args):
        self.url = url
        self.use_djenah = args.get("use_djenah",False)
        self.done = args.get("done",False)
        self.icon = QtGui.QIcon("add.png")

class ProjectModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(ProjectModel, self).__init__(parent)
        self.labels = [ self.tr("Url"), self.tr("Use Djenah"), self.tr("Done") ]
        self.projects = [
            Grunkreuz("http://zlo1.ru", use_djenah=True),
            Grunkreuz("http://zlo2eeeeeeeeeee.ru"),
            Grunkreuz("http://zlo3 we kuvqwdc uvqdc.ru", use_djenah=True),
            Grunkreuz("http://zlo4 qwef ibqwf.ru")
        ]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.projects)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.labels)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.projects[index.row()]
        
        if role == QtCore.Qt.DecorationRole and index.column()==2:
            return item.icon
            
        elif role == QtCore.Qt.DisplayRole:
            col = index.column()
            if col==0:
                v = item.url
            elif col==1:
                v = None#item.use_djenah
            elif col==2:
                v = item.done
            return v
        elif role == QtCore.Qt.CheckStateRole and index.column()==1:
            return item.use_djenah
        else:
            return QtCore.QVariant()
            
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        row = index.row()
        col = index.column()
        
        if row < 0 or row >= len(self.projects):
            return False
        if col < 0 or col >= len(self.labels):
            return False

        if col==0:
            self.projects[row].url = value
        elif col==1:
            self.projects[row].use_djenah = value
        elif col==2:
            self.projects[row].done = value
        
        self.dataChanged.emit(index, index)
        
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.labels[section])
        return QtCore.QVariant()
        
    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        logging.debug("removeRows %i -> %i" % (position, rows))
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        for i in range(rows):
            del self.projects[position]
        self.endRemoveRows()
        return True

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.projects.insert(position, Grunkreuz("http://") )
        self.endInsertRows()
        return True
        
class MainWindow(QtGui.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(640,480)
        layout = QtGui.QVBoxLayout(self)
        
        toolbar = QtGui.QToolBar(self)
        toolbar.addAction(self.tr("Add"), self.add_project)
        toolbar.addAction(self.tr("Remove"), self.remove_project)
        toolbar.addAction(self.tr("Test"), self.test)
        layout.addWidget(toolbar)
        
        model = ProjectModel(self)
        self.view = QtGui.QTableView(self)        
        self.view.setModel(model)

        self.view.verticalHeader().hide()
        self.view.verticalHeader().setDefaultSectionSize(20)
        self.view.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        #self.view.resizeColumnsToContents()
        #self.view.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        #self.view.horizontalHeader().setStretchLastSection(False)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        layout.addWidget(self.view)

        self.view.doubleClicked.connect(self.doubleClicked)

    def test(self):
        logging.debug("test")
        logging.debug("projects %i" % self.view.model().rowCount(self.view))
        logging.debug("projects %i" % len(self.view.model().projects))
        for i in self.view.model().projects:
            print i.url

    def add_project(self):
        i = random.randint(100,999)
        pos = self.view.model().rowCount()
        self.view.model().insertRow(pos)
        m = self.view.model()
        self.view.model().setData(m.index(pos,0), "http://zlo-%i.ru" % i)
        self.view.model().setData(m.index(pos,1), True)
        self.view.model().setData(m.index(pos,2), False)

    def remove_project(self):        
        selectionModel = self.view.selectionModel()
        indexes = selectionModel.selectedRows()
        indexes.sort( cmp=lambda x,y: cmp(x.row(),y.row()), reverse=True )
        for index in indexes:
            row = index.row()
            #logging.debug("let's remove %i -> %i" % (row,1))
            self.view.model().removeRow(row)

    def doubleClicked(self, index):
        logging.debug("clicked %i" % index.row())
        
    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    sys.exit(MainWindow().exec_())
