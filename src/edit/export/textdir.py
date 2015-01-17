#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from logging import debug, exception
from utils.article import Article
import traceback
import os
from utils.tidy import autodecode

from PyQt4 import QtCore
from PyQt4.QtCore import QThread

class Import(QThread):    
    def __init__(self, fname, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.fname = unicode(fname)
        self.pd = progressdialog
        self.result = None

    def _recurse_dir( self, fname, parent):
        goodexts = [".txt", ".html", ".htm", ".xhtml"]
        ext = os.path.splitext(fname)[-1].lower()
        if ext in goodexts and os.path.isfile( fname ):
            debug("add file %s", fname)
            text = "".join(open(fname,"rt").readlines())
            text = autodecode(text)
            title = os.path.split(fname)[-1]
            title = ".".join(title.split(".")[:-1])
            if self.pd: self.pd.set_text(u"Добавляем страницу %s" % title)
            article = Article(title, text)
            parent.add_child(article)
        elif os.path.isdir( fname ):
            debug("add dir %s", fname)
            title = os.path.split(fname)[-1]
            if self.pd: self.pd.set_text(u"Добавляем категорию %s" % title)
            cat = Article(title, u"")
            parent.add_child(cat)
            for subname in os.listdir( fname ):
                subname = unicode( subname )
                self._recurse_dir( fname + os.sep + subname, cat )

    def run(self):
        try:
            root = Article()
            self._recurse_dir(self.fname,root)
            self.result = root
        except:
            exception("import error")
            self.error = traceback.format_exc()
        
    def stop(self):
        debug("terminate")
        self.terminate()
        debug("wait")
        self.wait()

if __name__ == "__main__":
    reader = Import(u"d:\\work\\promidol\\test\\кат")
    reader.run()
    import cPickle
    cPickle.dump(reader.result, open("textdir.prt","wb"), cPickle.HIGHEST_PROTOCOL )
