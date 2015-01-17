#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
import edit.icons #@UnusedImport
from utils.tidy import autodecode
from utils.qthelpers import MyProgressDialog, ToolBarWithPopup

class StopDialog(QtGui.QDialog):
    def __init__(self, stopwords, parent=None):
        QtGui.QWidget.__init__( self, parent )
        self.resize(320, 480)
        self.setWindowTitle(u"Редактор стоп-слов")

        gridLayout = QtGui.QGridLayout(self)
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        gridLayout.addWidget(self.listWidget, 1, 0, 1, 1)

        tb = ToolBarWithPopup(self)
        tb.addAction(QtGui.QIcon(":/ico/img/note_add.png"), u"Добавить", self.addItem)
        tb.addAction(QtGui.QIcon(":/ico/img/note_go.png"), u"Импорт", self.impList)
        tb.addAction(QtGui.QIcon(":/ico/img/note_delete.png"), u"Удалить", self.delItem)
        gridLayout.addWidget(tb, 0, 0, 1, 1)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        gridLayout.addWidget(buttonBox, 2, 0, 1, 1)

        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)

        self.set_list(stopwords)

    def accept(self):
        self.result = []
        for i in range( self.listWidget.count() ):
            item = unicode(self.listWidget.item(i).text())
            self.result.append(item)
        self.setResult(1)
        self.hide()

    def addItem( self, text = u"шаблон", edited = True ):
        item = QtGui.QListWidgetItem( text, self.listWidget )
        item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable |
                       QtCore.Qt.ItemIsEnabled )
        if edited:
            self.listWidget.editItem( item )

    def delItem( self ):
        for item in self.listWidget.selectedItems():
            ndx = self.listWidget.indexFromItem(item)
            self.listWidget.takeItem( ndx.row() )

    def set_list(self, l):
        for i in l:
            self.addItem( i, False)            

    def impList(self):
        fname = QtGui.QFileDialog.getOpenFileName( self, u"Импорт стоп-слов",
            ".", u"Текстовый файл(*.txt)")
        if fname == "":
            return
        fname = unicode(fname)
        pd = MyProgressDialog(u"Импорт", u"Декодирование", u"Отмена", 0, 0, self)
        pd.show()
        egg = autodecode( open(unicode(fname),"rt").read() )
        arr = filter(lambda egg: len( egg.strip() ) > 0, egg.split("\n"))
        pd.set_text(u"Добавление")
        self.set_list(arr)
        pd.close()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    StopDialog = StopDialog([u'Убить',u'Съесть',u'Выкопать'])
    StopDialog.show()
    rc = StopDialog.exec_()
    if rc:
        print StopDialog.result
