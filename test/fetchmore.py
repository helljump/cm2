#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui

class DjenahListModel(QtCore.QAbstractListModel):
    numberPopulated = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(DjenahListModel, self).__init__(parent)

        self.fileList = ["one","two","three"]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.fileList)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self.fileList) or index.row() < 0:
            return None

        if role == QtCore.Qt.DisplayRole:
            return self.fileList[index.row()]

        if role == QtCore.Qt.BackgroundRole:
            batch = (index.row() // 1) % 2
            if batch == 0:
                return QtGui.qApp.palette().base()

            return QtGui.qApp.palette().alternateBase()

        return None
                
    def addRow(self):
        self.beginInsertRows(QtCore.QModelIndex(), len(self.fileList), len(self.fileList)+1)
        self.fileList.append("12345")
        self.endInsertRows() 
        
    def clear(self):
        self.beginResetModel()
        self.fileList = []
        self.endResetModel()

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Test")

        self.model = DjenahListModel(self)        
        view = QtGui.QListView()
        view.setModel(self.model)

        layout = QtGui.QGridLayout()
        layout.addWidget(view, 0, 0)
        self.setLayout(layout)

    def closeEvent(self, event):
        print "ce"
        #self.model.addRow()
        self.model.clear()
        event.ignore()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
