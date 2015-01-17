#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging 
from plugtypes import IExportPlugin #@UnresolvedImport
from utils.qthelpers import MyProgressDialog
from PyQt4.QtGui import QFileDialog
from phpserialize import dump
from pytils.translit import slugify
import os

log = logging.getLogger(__name__)

class CancelException(Exception):
    pass

class Plugin(IExportPlugin):        
    def run(self, tree, parent):        
        fileName = QFileDialog.getSaveFileName(parent, u"Экспорт", parent.current_save_path, 
            u"php pickle (*.pkl)")
        if fileName == "":
            return
        self.fileName = unicode(fileName)
        parent.current_save_path = os.path.split(self.fileName)[0]

        self.tree = tree
        self.pd = MyProgressDialog(u"Экспорт", u"Запись статей", u"Отмена", 0,
                                   self.articles_count(tree), parent)
        self.pd.setFixedWidth(320)
        self.pd.show()
        try:
            self.export()
        except CancelException:
            pass
        self.pd.close()
    def articles_count(self, root):
        def _recurse(item):
            egg = 1
            for subitem in item.get_children():
                egg += _recurse(subitem)
            return egg
        return _recurse(root)
    def export(self):
        def recurse_tree(tree):
            children = {}
            for item in tree.get_children():
                if self.pd.wasCanceled():
                    raise CancelException
                article = {
                    "title":item.title,
                    "category":slugify(tree.title)[:30],
                    "text":item.text,
                    "pubdate":item.date.isoformat(),
                    "tags":item.tags,
                    "intro":getattr(item, "intro", "")
                }
                article["children"] = recurse_tree(item)
                children[slugify(item.title)[:30]] = article
                self.pd.inc_value()
            return children
        obj = recurse_tree(self.tree)
        with open(self.fileName, "wb") as fout:
            dump(obj, fout)
