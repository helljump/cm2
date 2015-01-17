#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#mysql --default-character-set utf8 -b dle9 <dle90.sql

__author__ = "snöa"

from plugtypes import IExportPlugin
import logging 
from pytils.translit import slugify
from utils.qthelpers import MyProgressDialog
import os
import codecs
from utils.tidy import sql_quote
from PyQt4.QtGui import QFileDialog

log = logging.getLogger(__name__)

CATEGORY = u"""
INSERT INTO `dle_category` (id, name, alt_name, keywords, posi) VALUES (%(id)i, "%(name)s", "%(slug)s","",%(id)i);
"""

ARTICLE = u"""
INSERT INTO `dle_post` (id, autor, date, short_story, full_story, xfields, title, keywords, category, alt_name, tags, approve) VALUES (%(id)i, "%(author)s", "%(date)s", "%(intro)s", "%(text)s", "", "%(title)s", "",%(catid)i, "%(slug)s", "%(tags)s", 1);
"""

TAG = u"""
INSERT INTO `dle_tags` (news_id, tag) VALUES (%(postid)i, "%(tag)s");
"""

def articles_count(item):
    egg = 1
    for subitem in item.get_children():
        egg += articles_count(subitem)
    return egg

class CancelException(Exception):
    pass

class ExportPlugin(IExportPlugin):
    
    AUTHOR = 'admin'
    CATID = 100
    ARTICLEID = 1000
    
    def run(self, tree, parent):
        fname = QFileDialog.getSaveFileName(parent, u"Экспорт DLE 9.0", 
            parent.current_save_path, u"SQL file (*.sql)")
        if fname == "":
            return
        fname = unicode(fname)
        parent.current_save_path = os.path.split(fname)[0]
        self.pd = MyProgressDialog(u"Экспорт DLE 9.0", u"Запись статей", u"Отмена", 0,
            articles_count(tree), parent)
        self.pd.show()
        try:
            self.export(tree, fname)
        except CancelException:
            pass
        self.pd.close()

    def get_articles(self, parent):
        articles = []
        tags = []
        for item in parent.get_children():
            if self.pd.wasCanceled():
                raise CancelException
            self.pd.inc_value()
            if hasattr(item,"intro"):
                intro = item.intro
                text = item.text
            else:
                intro = item.text
                text = ""               
            egg = ARTICLE % {
                "id":self.ARTICLEID,
                "author":self.AUTHOR,
                "date":str(item.date),
                "intro":sql_quote(intro),
                "text":sql_quote(text),
                "title":sql_quote(item.title),
                "catid":self.CATID,
                "slug":slugify(item.title),
                "tags":sql_quote(", ".join(item.tags))
            }
            articles.append(egg)
            for tag in item.tags:
                egg = TAG % {
                    "postid":self.ARTICLEID,
                    "tag":sql_quote(tag)
                }
                tags.append(egg)
            egg, spam = self.get_articles(item)
            articles += egg
            tags += spam
            self.ARTICLEID += 1
        return articles, tags
    
    def export(self, tree, fname):
        categories = []
        articles = []
        tags = []
        for item in tree.get_children():
            egg = CATEGORY % {
                "id":self.CATID,
                "name":sql_quote(item.title),
                "slug":slugify(item.title)
            }
            categories.append(egg)
            new_articles, new_tags = self.get_articles(item)
            articles += new_articles
            tags += new_tags
            self.CATID += 1

        with codecs.open(fname, "wt", "utf-8", "replace") as fout:
            fout.write("".join(categories))
            fout.write("".join(articles))
            fout.write("".join(tags))
