#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging 
log = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread
import re
from utils.article import Article
from utils.tidy import overspaces, autodecode
import traceback

class Export(QThread):
    
    HTML_HEADER = """<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=%(encoding)s">
    <title>Promidol TreeEdit</title>
</head>
<body>
"""

    HTML_TAIL = """</body>
</html>
"""

    def __init__(self, tree, fname, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.tree = tree
        self.fname = unicode(fname)
        self.progressdialog = progressdialog
        self.error = None
        
    def run(self):
        encoding = "utf-8"
        try:
            if self.progressdialog:
                self.progressdialog.set_text(u"Запись заголовка")
                QtGui.qApp.processEvents()
            fout = open(self.fname, "wt")
            fout.write(self.HTML_HEADER % {"encoding":encoding})
            
            def recurse(parent, deep=1):
                for item in parent.get_children():
                    title = item.title.encode(encoding, "ignore")
                    text = item.text.encode(encoding, "ignore")
                    fout.write("<H%(deep)i>%(title)s</H%(deep)i>\n%(text)s\n" % 
                                { "title":title, "deep":deep, "text":text })
                    recurse(item, deep + 1)
                    if self.progressdialog:
                        self.progressdialog.set_text(u"Запись страницы")
                    QtGui.qApp.processEvents()
                    
            recurse(self.tree)
            
            if self.progressdialog:
                self.progressdialog.set_text(u"Запись хвоста")
                QtGui.qApp.processEvents()
            
            fout.write(self.HTML_TAIL)
            fout.close()
        except:
            log.exception("export error")
            self.error = traceback.format_exc()
        
    def stop(self):
        log.debug("terminate")
        self.terminate()
        log.debug("wait")
        self.wait()

class Import(QThread):
    
    bodyclean = re.compile("(<\/?(body|html)[^>]*>)", re.I | re.M)
    
    def __init__(self, fname, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.fname = fname
        self.progressdialog = progressdialog
        self.result = None
        
    def run(self):
        try:
            last_deep = [None] * 9
            last_deep[0] = root = Article()
            log.debug("parse")
            if self.progressdialog:
                self.progressdialog.set_text(u"Анализ файла")
                #QtGui.qApp.processEvents()
            
            
            for fname in self.fname:
                egg = unicode(fname)
                pretty = autodecode(open(egg).read())
                #print "1"
                log.debug("make tree")
                splitted = re.split("(?imsu)<h[1-8][^>]*>", pretty)
                if self.progressdialog:
                    self.progressdialog.set_text(u"Построение дерева")
                    self.progressdialog.set_range(0, len(splitted))
                    #QtGui.qApp.processEvents()
                cntr = 0
                #print "2"
                
                for article in splitted:
                    spam = re.split("(?imsu)</h([1-8])>", article)
                    if len(spam) > 1 and len(spam[0].strip()) > 0:
                        deep = int(spam[1])
                        #print "-"*deep, u"%s" % spam[0].strip()
                        title = re.sub('<(?!(?:a\s|/a|!))[^>]*>', '', spam[0]).strip()
                        try:
                            text = spam[2]
                            text = self.bodyclean.sub("", text)
                            text = overspaces.sub(" ", text)
                            text = text.strip()
                        except KeyError:
                            text = ""
                        log.debug("Create article %s", title)
                        #print title
                        art = Article(title, text)
                        recdeep = deep - 1
                        while not last_deep[recdeep]:
                            recdeep -= 1
                        else:
                            last_deep[recdeep].add_child(art)
                            last_deep[recdeep + 1] = art
                    if self.progressdialog:
                        self.progressdialog.inc_value()
                        pass
                        #QtGui.qApp.processEvents()
                    cntr += 1

                #print "3"

            log.debug("done")
            self.result = root
        except:
            log.exception("import error")
            self.error = traceback.format_exc()
           
        log.debug("*** done ***")

    def stop(self):
        log.debug("terminate")
        self.terminate()
        log.debug("wait")
        self.wait()
