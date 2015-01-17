#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from plugtypes import IProcessPlugin
from PyQt4 import QtGui
from utils.qthelpers import MyProgressDialog
import re
from utils.tidy import html_tags_re, overspaces

h1closed = re.compile("</h1>", re.I)

def sanitize(s):
    return overspaces.sub(" ", html_tags_re.sub(" ", s)).strip()

class Plugin(IProcessPlugin):
    def run(self, items, parent):
        pd = MyProgressDialog(u"Обработка", u"H1 в заголовок", u"Отмена", 0, 
            len(items), parent)
        pd.show()
        for item in items:            
            m = h1closed.split(item.article.text, 1)
            if len(m)>1:
                item.article.title = sanitize(m[0])
                item.article.text = m[1].strip()
            pd.inc_value()
            QtGui.qApp.processEvents()
        pd.close()
