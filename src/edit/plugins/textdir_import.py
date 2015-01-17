#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
try:
    from plugtypes import IImportPlugin #@UnresolvedImport
except ImportError:
    IImportPlugin = object
from utils.qthelpers import MyProgressDialog, MyPath
from PyQt4 import QtGui
import os
from utils.article import Article
from utils.tidy import autodecode
from utils.formlayout import fedit
import os

log = logging.getLogger(__name__)

class CancelException(Exception):
    pass

class DirTextImport(IImportPlugin):
    
    GOODEXTS = [".txt", ".html", ".htm", ".xhtml"]
    
    ENCODINGS = [u"Автоопределение",
                 ("auto", u"Автоопределение"),
                 ("utf-8", "UTF-8"),
                 ("cp1251", "Windows-1251"),
                 ("ascii", "ascii")]
    
    def run(self, parent):
        
        datalist = [(u"Каталог:", MyPath(parent.current_load_path)),
                    (u"Кодировка текстов", DirTextImport.ENCODINGS)]
        rc = fedit(datalist, title=u"Импорт текстовых файлов", parent=parent)
        if not rc:
            return
        
        dirname = rc[0]
        parent.current_load_path = dirname
        self.encoding = rc[1]
        
        if not dirname:
            return None
        self.pd = pd = MyProgressDialog(u"Импорт", u"Открытие каталог", u"Отмена", 0, 0, parent)
        pd.setMaximumWidth(320)
        pd.show()
        try:
            root = Article()
            self.recurse_dir(unicode(dirname), root)
        except CancelException:
            pass
        pd.close()
        return root

    def recurse_dir(self, fname, parent):
        ext = os.path.splitext(fname)[-1].lower()
        if self.pd.wasCanceled():
            raise CancelException
        if ext in self.GOODEXTS and os.path.isfile(fname):
            text = "".join(open(fname, "rt").readlines())
            if self.encoding == "auto":
                text = autodecode(text)
            else:
                text = text.decode(self.encoding, "replace")
            title = os.path.split(fname)[-1]
            title = ".".join(title.split(".")[:-1])
            self.pd.set_text(u"Добавляем страницу %s" % title)
            QtGui.qApp.processEvents()
            article = Article(title, text)
            parent.add_child(article)
        elif os.path.isdir(fname):
            title = os.path.split(fname)[-1]
            self.pd.set_text(u"Добавляем категорию %s" % title)
            QtGui.qApp.processEvents()
            cat = Article(title, u"")
            parent.add_child(cat)
            for subname in os.listdir(fname):
                subname = unicode(subname)
                self.recurse_dir(fname + os.sep + subname, cat)

if __name__ == '__main__':
    DirTextImport().run(None)
