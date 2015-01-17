# -*- coding: UTF-8 -*-

__author__ = "snöa"
    
from PyQt4 import QtGui
from utils.qthelpers import MyProgressDialog
from plugtypes import IUtilitePlugin

class Plugin(IUtilitePlugin):
                
    def _recurse_tree_gen(self, item):
        for i in range(item.childCount()):
            child = item.child(i)
            for subchild in self._recurse_tree_gen(child):
                yield subchild
        if hasattr(item, "article"): #else root
            yield item

    def run(self, parent):
        pd = MyProgressDialog(u"Тестовый пример", u"Обход дерева", u"Отмена", 0, 0, parent)
        pd.show()
        tree = parent.treeWidget.tree
        items_for_del = set()
        
        for child in self._recurse_tree_gen(tree.invisibleRootItem()):
            if child.article.title.find(u"й") !=-1:
                items_for_del.add(child)
            else:
                child.article.title = "%s[passed]" % child.article.title
            QtGui.qApp.processEvents()
            
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
                
        pd.close()
