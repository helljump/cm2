#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from plugtypes import IProcessPlugin #@UnresolvedImport

from PyQt4 import QtGui
from utils.qthelpers import MyProgressDialog

class Reverse(IProcessPlugin):    
    def run(self, items, parent):
        pd = MyProgressDialog(u"Обработка", u"Выверт статей", u"Отмена", 0,
                                len(items), parent)
        pd.setFixedWidth(320)
        pd.show()
        for item in items:
            item.article.text = self.rev(item.article.text)
            item.article.title = self.rev(item.article.title)
            item.article.tags = self.rev(item.article.tags)
            item.article.meta = {"mykey":"myvalue"}
            # item.article.date
            if hasattr(item.article, "intro"):
                item.article.intro = self.rev(item.article.intro)
            pd.set_value(pd.value() + 1)
            QtGui.qApp.processEvents()
        pd.close()

    def rev(self, s):
        s = list(s)
        s.reverse()
        return "".join(s)
