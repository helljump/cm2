#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from plugtypes import IProcessPlugin #@UnresolvedImport
from PyQt4 import QtGui
from utils.qthelpers import MyProgressDialog
import spelldialog #@UnresolvedImport
from utils.formlayout import fedit
import re

class TitleGenerator(IProcessPlugin):
    def activate(self):
        langs = [u"Русский"]
        for k in spelldialog.config:
            langs.append((k, k))
        self.datalist = [
            (u"Разделитель:", "([\.\?\!]+)"),
            (u"Язык текста:", langs),
            (u"Удалять прилагательные:", True),
            (u"Исправлять регистр:", False),
            (u"Слов, не более:", 10),
        ]

    def run(self, items, parent):
        rc = fedit(self.datalist, title=u"Генерация заголовоков", parent=parent)
        if not rc:
            return
        (delimiter, langkey, remove_prils, capitalize_text, overwords) = rc
        pd = MyProgressDialog(u"Генерация заголовков", u"Загрузка словаря", u"Отмена", 0,
                                len(items), parent)
        pd.setFixedWidth(320)
        pd.show()
        QtGui.qApp.processEvents()
        hobj, henc = spelldialog.load_spell(langkey)
        delimiter_c = re.compile(delimiter, re.U)
        html_tags_re = re.compile("<[^>]*>", re.I | re.U | re.S | re.M)
        for item in items:
            article_title = item.article.text
            article_title = html_tags_re.sub("", article_title)
            if not article_title:
                continue
            if remove_prils:
                egg = delimiter_c.split(article_title)[0]
                egg = re.split("(?u)([\s,\:\.\?;]+)", egg)
                spam = []
                for src in egg:
                    word = hobj.analyze(src.encode(henc, "replace"))
                    if not word:
                        spam.append(src)
                        continue
                    word = word[0]
                    word = unicode(word, henc)
                    if "fl:A" not in word: #not pril
                        spam.append(src)
                article_title = "".join(spam)                
            article_title = re.sub("(?usmi)[\s]+", " ", article_title)                
            article_title = article_title.strip()
            article_title = " ".join(article_title.split(" ")[:overwords])
            if capitalize_text:
                article_title = article_title.capitalize()
            item.article.title = article_title
            pd.set_value(pd.value() + 1)
            pd.set_text(article_title)
            QtGui.qApp.processEvents()
        pd.close()
