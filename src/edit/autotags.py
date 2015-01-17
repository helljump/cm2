#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
from utils.qthelpers import ToolBarWithPopup, MyProgressDialog
import Stemmer
from utils.formlayout import fedit
from utils.tidy import html_tags_re, autodecode
import re
from logging import debug
import esm
from commands import EditArticleCommand
import icons #@UnusedImport
import spelldialog
import os

class AutotagsDialog(QtGui.QDialog):

    langs = [("russian", u"Русский"), ("english", u"Английский"), ("german", u"Немецкий")]
    
    debugtags = u"""Google, запросы, интернет, контент, поисковик, пользователь, проект, работа, ссылки, страницы, текст, трафик, Яндекс"""
    
    class Lemm(object):
        def __init__(self, word, cnt):
            self.word = word
            self.cnt = cnt

    def __init__(self, artlist, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Автометки")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(640, 480)
        self.artlist = artlist
        self.parent = parent
        
        layout = QtGui.QGridLayout(self)
        
        toolbar = ToolBarWithPopup(self, style=QtCore.Qt.ToolButtonTextBesideIcon)
        toolbar.addAction(QtGui.QIcon(":/ico/img/tag_blue_add.png"), u"Генерировать леммы",
            self.generate_lemms)
        toolbar.addAction(QtGui.QIcon(":/ico/img/note_add.png"), u"Импорт файла", self.import_tags)
        layout.addWidget(toolbar, 0, 0, 1, 1)

        frame = QtGui.QFrame(self)
        l1 = QtGui.QHBoxLayout(frame)
        l1.addWidget(QtGui.QLabel(u"Язык"))
        self.lang_cb = QtGui.QComboBox(frame)
        for l in self.langs:
            self.lang_cb.addItem(l[1], QtCore.QVariant(l[0]))
        l1.addWidget(self.lang_cb)
        l1.addWidget(QtGui.QLabel(u"Меток не более"))
        self.tags_sb = QtGui.QSpinBox(frame)
        self.tags_sb.setValue(5)
        l1.addWidget(self.tags_sb)
        l1.addStretch(1)
        layout.addWidget(frame, 1, 0, 1, 1)

        self.textedit = QtGui.QTextEdit(self)
        layout.addWidget(self.textedit, 2, 0, 1, 1)
        
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        layout.addWidget(buttonBox, 3, 0, 1, 1)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)
        
        #self.textedit.setText(self.debugtags)
        
    def accept(self):
        v = self.lang_cb.itemData(self.lang_cb.currentIndex())
        l = v.toString()
        tagscount = self.tags_sb.value()
        #debug(l)
        
        pd = MyProgressDialog(u"Генерация меток", u"Инициализация", u"Отмена", 0, 0, self)
        pd.setMaximumWidth(320)
        pd.show()

        stemmer = Stemmer.Stemmer(unicode(l))
        
        debug("fix index")
        lemms = {}
        actree = esm.Index()
        txt = unicode(self.textedit.toPlainText())
        for lemm in map(unicode.strip, txt.split(",")):
            base = stemmer.stemWord(lemm.lower())
            base = base.encode("cp1251", "replace")
            lemms[base] = lemm
            actree.enter(base)
            #debug("%s:%s", base, lemm)
            QtGui.qApp.processEvents()
        actree.fix()
        
        pd.set_text(u"Обработка статей")
        pd.set_range(0, len(self.artlist))
        egg = 0
        debug("set tags")
        
        self.parent.undo_stack.beginMacro(u"Автометки")
        
        for item in self.artlist:
            text = item.article.text.lower().encode("cp1251", "replace")
            tags = [ lemms[founded[1]] for founded in actree.query(text) ]
            item_tags = list(set(tags))[:tagscount]
            spam = ", ".join(item_tags)
            self.parent.undo_stack.push(
                EditArticleCommand(self.parent.treeWidget.tree, item, {"tags":spam}))

            pd.set_value(egg)
            egg += 1
            
        self.parent.undo_stack.endMacro()
            
        pd.close()
        
        self.hide()
        
    def _splitwords(self, s):
        ws = html_tags_re.sub("", s)
        ws = ws.lower()
        ws = re.split("(?misu)\W", ws)
        return ws
        
    def generate_lemms(self):
        langs = [(row, row) for row in spelldialog.config]
        langs.insert(0, u"Русский")
        datalist = [ (u"Язык текста:", langs), (u"Минимальный размер слова:", 5),
            (u"Максимальное количество лемм:", 20) ]
        rc = fedit(datalist, title=u"Сгенерировать леммы", parent=self)
        if not rc:
            return False
        (src_lang, min_len, max_count) = rc
        hobj, henc = spelldialog.load_spell(src_lang)
        pd = MyProgressDialog(u"Генерация лемм", u"Обработка", u"Отмена", 0,
            len(self.artlist), self)
        pd.show()
        lemms = {}
        for item in self.artlist:
            ws = self._splitwords(item.article.text)
            for w in ws:
                for q in hobj.stem(w.encode(henc,"replace")):
                    q = q.decode(henc, "replace")
                    if len(q) < min_len:
                        continue
                    if lemms.has_key(q):
                        lemms[q] += 1
                    else:
                        lemms[q] = 1                
            if pd.wasCanceled():
                break
            pd.setValue(pd.value() + 1)
            pd.set_text(item.article.title)
        pd.set_text(u"Сортировка")
        pd.set_range(0, 0)
        spam = []
        for w, v in lemms.items():
            spam.append(AutotagsDialog.Lemm(w, v))
            QtGui.qApp.processEvents()
        spam.sort(cmp=lambda x, y: cmp(x.cnt, y.cnt), reverse=True)
        egg = [item.word for item in spam]
        s2 = set(egg[:max_count])
        self.update_tags(s2)
        pd.close()
        
    def generate_lemms_old(self):
        comment = u""""""
        langs = ["russian", ("russian", u"Русский"), ("english", u"Английский"),
            ("german", u"Немецкий")]
        datalist = [ (u"Язык текста:", langs), (u"Минимальный размер слова:", 5),
            (u"Максимальное количество лемм:", 20) ]
        rc = fedit(datalist, title=u"Сгенерировать леммы", parent=self, comment=comment)
        if not rc:
            return False
        (src_lang, min_len, max_count) = rc
        stemmer = Stemmer.Stemmer(src_lang)
        
        pd = MyProgressDialog(u"Генерация лемм", u"Обработка", u"Отмена", 0,
            len(self.artlist), self)
        pd.setMaximumWidth(320)
        pd.show()
        lemms = {}
        for item in self.artlist:
            ws = self._splitwords(item.article.text)
            for w in stemmer.stemWords(ws):
                if len(w) < min_len:
                    continue
                if lemms.has_key(w):
                    lemms[w] += 1
                else:
                    lemms[w] = 1                
            if pd.wasCanceled():
                break
            pd.setValue(pd.value() + 1)
            pd.set_text(item.article.title)
        
        pd.set_text(u"Сортировка")
        pd.set_range(0, 0)
        spam = []
        for w, v in lemms.items():
            spam.append(AutotagsDialog.Lemm(w, v))
            QtGui.qApp.processEvents()
        spam.sort(cmp=lambda x, y: cmp(x.cnt, y.cnt), reverse=True)
        egg = [item.word for item in spam]
        s2 = set(egg[:max_count])
        self.update_tags(s2)
        pd.close()
        
    def update_tags(self, s2):
        txt = unicode(self.textedit.toPlainText())
        old = map(unicode.strip, txt.split(","))
        s1 = set(old)
        s3 = list(s1 | s2)
        s3 = filter(unicode.strip, s3)
        s3.sort()
        self.textedit.setText(', '.join(s3))
        
    def import_tags(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, u"Открыть...",
            self.parent.current_load_path, "tags file (*.txt)")
        if not fname:
            return
        fname = unicode(fname)
        self.current_load_path = os.path.split(fname)[0]
        txt = open(fname, "rt").read()
        txt = autodecode(txt)
        s2 = map(unicode.strip, txt.split(","))
        if s2:
            self.update_tags(set(s2))
        
    def test(self):
        for item in self.artlist:
            print item.title
