#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import sys
import re
import gzip
from PyQt4 import QtCore, QtGui
from utils.qthelpers import ToolBarWithPopup, MyProgressDialog
import itertools
from utils.misc import get_random_spans, replace_by_spans
import math
from commands import EditArticleCommand
import logging
import icons #@UnusedImport
import os

log = logging.getLogger(__name__)

class InsertLinksDialog(QtGui.QDialog):
    def __init__(self, arts, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Вставка ссылок")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(520, 432)
        self.parent = parent
        self.arts = arts

        gridLayout = QtGui.QGridLayout(self)
        
        toolbar = ToolBarWithPopup(self, style=QtCore.Qt.ToolButtonTextBesideIcon)
        toolbar.addAction(QtGui.QIcon(":/ico/img/page_white_get.png"),
            u"Импорт файла", self.import_file)
        gridLayout.addWidget(toolbar, 0, 0)
        
        self.links_te = QtGui.QPlainTextEdit(self)
        gridLayout.addWidget(self.links_te, 1, 0)
        
        horizontalLayout_2 = QtGui.QHBoxLayout()
        self.onpostsmode_rb = QtGui.QRadioButton(u"Ссылок на страницу", self)
        self.onpostsmode_rb.setChecked(True)
        horizontalLayout_2.addWidget(self.onpostsmode_rb)
        
        self.qty_sb = QtGui.QSpinBox(self)
        self.qty_sb.setValue(1)
        horizontalLayout_2.addWidget(self.qty_sb)
        
        self.cycle_cb = QtGui.QCheckBox(u"Зациклено", self)
        self.cycle_cb.setChecked(True)
        horizontalLayout_2.addWidget(self.cycle_cb)
        

        gridLayout.addLayout(horizontalLayout_2, 2, 0)
        
        horizontalLayout_3 = QtGui.QHBoxLayout()
        
        self.totalmode_rb = QtGui.QRadioButton(u"Распределить равномерно", self)
        horizontalLayout_3.addWidget(self.totalmode_rb)
        
        gridLayout.addLayout(horizontalLayout_3, 3, 0)
        
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        gridLayout.addWidget(buttonBox, 4, 0)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.totalmode_rb.clicked.connect(self.cycle_cb.setDisabled)
        self.totalmode_rb.clicked.connect(self.qty_sb.setDisabled)
        self.onpostsmode_rb.clicked.connect(self.cycle_cb.setEnabled)
        self.onpostsmode_rb.clicked.connect(self.qty_sb.setEnabled)
        
    def import_file(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, u"Импорт...", self.parent.current_load_path,
            "Links files (*.txt);;Sitemap XMLs (*.xml *.xml.gz)")
        if not fname:
            return
        fname = unicode(fname)
        self.parent.current_load_path = os.path.split(fname)[0]
        text = ""
        if fname.endswith(".txt"):
            with open(fname, "rt") as finp:
                text = finp.read()
        elif fname.endswith(".gz"):
            finp = gzip.open(fname)
            text = finp.read()
            m = re.findall("<loc>([^>]+)</loc>", text)
            if m:
                spam = [item for item in m]
                text = "\n".join(spam)
        elif fname.endswith(".xml"):
            with open(fname, "rt") as finp:
                text = finp.read()
                m = re.findall("<loc>([^>]+)</loc>", text)
                print m
                if m:
                    spam = [item for item in m]
                    text = "\n".join(spam)
        self.links_te.setPlainText(text)

    def accept(self):
        self.hide()
        self.process()
        
    def process(self):
        pd = MyProgressDialog(u"Вставка ссылок", u"", u"Отмена", 0, len(self.arts), self)
        pd.setMaximumWidth(320)
        pd.show()
        
        links_list = [link.strip() 
            for link in unicode(self.links_te.toPlainText()).split("\n")]
        
        if self.onpostsmode_rb.isChecked():
            linksiter = itertools.cycle(links_list)
            links_on_post = self.qty_sb.value()
        else:
            linksiter = iter(links_list)
            links_on_post = float(len(links_list)) / len(self.arts) + 0.1
        
        artsdone = 0
        links_counter = 0.0
        try:
            
            self.parent.undo_stack.beginMacro(u"Вставка ссылок")
            
            for treeitem in self.arts:
                article = treeitem.article
                #log.debug(article.title)
                text = unicode(article.text)
                if type(links_on_post) == type(0.0):
                    links_counter += links_on_post
                    if links_counter >= 1:
                        egg = math.trunc(links_counter)
                        spans = get_random_spans(text, egg)
                        links_counter -= egg
                    else:
                        spans = []
                else:
                    spans = get_random_spans(text, links_on_post)
                for item in spans:
                    egg = item["word"]
                    item["word"] = "<a href=\"%s\">%s</a>" % (linksiter.next() , item["word"])
                article_text = replace_by_spans(text, spans)
                
                self.parent.undo_stack.push(
                    EditArticleCommand(self.parent.treeWidget.tree, treeitem,
                        {"text":article_text}))

                artsdone += 1
                pd.set_value(artsdone)
                if pd.wasCanceled():
                    break
            else:
                if links_counter > 0:
                    text = unicode(treeitem.article.text)
                    egg = math.trunc(links_counter)
                    spans = get_random_spans(text, egg)
                    for item in spans:
                        item["word"] = "<a href=\"%s\">%s</a>" % (linksiter.next() , item["word"])
                    #print treeitem
                    article_text = replace_by_spans(text, spans)
                    
                    self.parent.undo_stack.push(
                        EditArticleCommand(self.parent.treeWidget.tree, treeitem,
                            {"text":article_text}))

                    
            self.parent.undo_stack.endMacro()
                
        except StopIteration:
            pass#no more links
        pd.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    InsertLinksDialog(None, None).exec_()

