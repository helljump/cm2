# -*- coding: UTF-8 -*-

__author__ = "snöa"
    
from PyQt4 import QtGui, QtCore
from utils.qthelpers import MyProgressDialog
from plugtypes import IUtilitePlugin

class Plugin(IUtilitePlugin):
                
    def run(self, parent):
    
        rc = QtGui.QMessageBox.question(parent, u"Удаление статей", u"Вы уверены?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )
        if rc == QtGui.QMessageBox.No:
            return
    
        pd = MyProgressDialog(u"Удаление статей", u"Обход дерева", u"Отмена", 0, 0, parent)
        pd.show()
        tree = parent.treeWidget.tree
        items_for_del = set()
        
        for i in range(tree.topLevelItemCount()):
            child = tree.topLevelItem(i)
            for j in range(child.childCount()):
                child.takeChild(0)
            QtGui.qApp.processEvents()
        
        """
        for item in items_for_del:
            parent = item.parent()
            if not parent:
                index = tree.indexOfTopLevelItem(item)
                item.takeChildren()
                tree.takeTopLevelItem(index)
            else:
                index = parent.indexOfChild(item)
                item.takeChildren()
                parent.takeChild(index)
            QtGui.qApp.processEvents()
        """
        
        pd.close()
