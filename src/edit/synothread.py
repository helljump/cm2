#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from logging import debug, exception
import traceback
from yazzy.yasyn2 import ACDict
from yazzy import yasyn2

from commands import EditArticleCommand

class SynoThread(QThread):
    def __init__(self, articles, params, progressdialog, parent):
        QtCore.QThread.__init__(self, parent)
        self.pd = progressdialog
        self.articles = articles
        self.params = params
        self.parent = parent

    def run(self):
        try:
            egg = []
            self.pd.set_text(u"Создание словаря")
            if self.params['use_stopwords']:
                egg = self.params['stopwords']

            acd = ACDict(egg, self.pd)

            if self.params['use_internal']:
                from yazzy.fullthematik import internal_db
                d = yasyn2.load_py(internal_db)
                i = 0
                for item in d:
                    if not i % 10000:
                        self.pd.set_text(u"Подготовка внутренней базы(%i)" % i)
                    acd.addPhrase(item[0], item[1], item[2])
                    i += 1

            bases = self.params['bases']

            syno_title = self.params['syno_title']
            syno_text = self.params['syno_text']
            syno_intro = self.params['syno_intro']
            process_cats = self.params['process_cats']
            gen_template = self.params['gen_template']

            self.pd.set_range(0, len(bases))
            i = 0
            for base in bases:
                fname, d = yasyn2.load(base)
                j = 0
                for item in d:
                    if not j % 10000:
                        self.pd.set_text(u"Подготовка %s(%i)" % (fname, j))
                    acd.addPhrase(item[0], item[1], item[2])
                    j += 1
                i += 1
                self.pd.set_value(i)

            dones = 0
            i = 0
            self.pd.set_range(0, len(self.articles))
            #self.pd.set_text(u"Обработка страниц")

            self.parent.undo_stack.beginMacro(u"Замена синонимов")

            for article in self.articles:
                changes = {}

                if len(getattr(egg,"intro",""))>0 or len(getattr(egg,"text",""))>0:
                    if syno_title:
                        article_title = acd.search(article.article.title,
                            mindist=self.params['worddistant'], gen_template=gen_template)
                        changes['title'] = article_title
                elif process_cats:
                    article_title = acd.search(article.article.title,
                        mindist=self.params['worddistant'], gen_template=gen_template)
                    changes['title'] = article_title

                if syno_text:
                    article_text = acd.search(article.article.text,
                        mindist=self.params['worddistant'], gen_template=gen_template)
                    changes['text'] = article_text

                dones += acd.founded_sorted_qty

                egg = article.article
                intro = getattr(egg,"intro",None)
                if syno_intro and intro:
                    #print repr(intro)
                    article_intro = acd.search(article.article.intro,
                        mindist=self.params['worddistant'], gen_template=gen_template)
                    changes['intro'] = article_intro

                self.parent.undo_stack.push(
                    EditArticleCommand(self.parent.treeWidget.tree, article, changes))

                dones += acd.founded_sorted_qty
                self.pd.inc_value()
                i += 1
            self.result = dones
            debug("syno done %i", dones)

            self.parent.undo_stack.endMacro()

        except Exception:
            exception("import error")
            self.error = traceback.format_exc()

        debug("syno out")

    def stop(self):
        self.terminate()
        debug("wait")
        self.wait()
