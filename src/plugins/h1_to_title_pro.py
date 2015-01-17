# -*- coding: UTF-8 -*-

from plugtypes import IProcessPlugin
from PyQt4 import QtGui
from utils.qthelpers import MyProgressDialog
import re
from utils.tidy import html_tags_re, overspaces

class Plugin(IProcessPlugin):

    h1closed = re.compile(u"(?imsu)<h1.+?>(.+?)</h1>")
    
    def run(self, items, parent):
        pd = MyProgressDialog(u"Обработка", u"H1 в заголовок", u"Отмена", 0, len(items), parent)
        pd.show()
        for item in items:            
            m = self.h1closed.search(item.article.text)
            if m:
                item.article.title = self.sanitize(m.group(1))
                item.article.text = self.h1closed.sub("", item.article.text)
            pd.inc_value()
            QtGui.qApp.processEvents()
        pd.close()

    def sanitize(self, s):
        return overspaces.sub(" ", html_tags_re.sub(" ", s)).strip()
