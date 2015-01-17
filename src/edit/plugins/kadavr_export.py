#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
import os
from xml.sax.saxutils import escape

from plugtypes import IExportPlugin
from PyQt4.QtCore import QDate
from phpserialize import dump
from pytils.translit import slugify
from utils.qthelpers import MyProgressDialog, MyFile
from utils.formlayout import fedit

log = logging.getLogger(__name__)

def articles_count(item):
    egg = 1
    for subitem in item.get_children():
        egg += articles_count(subitem)
    return egg

def generate_uniq_name(names, new_name):
    egg = orig_egg = slugify(new_name)
    cnt = 1
    while egg in names:
        egg = "%s-%i" % (orig_egg, cnt)
        cnt += 1
    return egg

def flatten(item):
    children = []
    for subitem in item.get_children():
        children.append(subitem)
        children += flatten(subitem)
    return children

class CancelException(Exception):
    pass
    
class Plugin(IExportPlugin):        

    USEGZIP = True
    
    def run(self, tree, parent):
        egg = parent.current_save_path + os.sep + "articles.kad"
        mf = MyFile(egg)
        mf.mask = "Kadaver data file (*.kad)"
        mf.mode = "w"
        datalist = [(u"Файл:", mf), 
            (u"Сжатие", self.USEGZIP),
            (None, u"Отключите сжатие для версий Кадавр до 1.4"),
            (u"Slug", "%Y-%m-%d/%H-%M-%S/%%(slug)s"),
        ]
        rc = fedit(datalist, title=u"Экспорт", parent=parent)
        if not rc:
            return
        fname = rc[0]
        self.USEGZIP = rc[1]
        self.slugform = rc[2]
        parent.current_save_path = os.path.split(fname)[0]
        self.pd = MyProgressDialog(u"Экспорт", u"Запись статей", u"Отмена", 0,
            articles_count(tree), parent)
        self.pd.show()
        try:
            self.export(tree, fname)
        except CancelException:
            pass
        self.pd.close()
        
    def export(self, tree, fname):
        categories = {}
        articles = {}
        tags = {}
        obj = {
            "categories":categories,
            "articles":articles,
            "tags":tags,
            "packed":self.USEGZIP
        }
        for cat in tree.get_children():
            slug = generate_uniq_name(categories, cat.title)            
            log.debug("+ category: %s", slug)
            categories[slug] = {
                "title":escape(cat.title)
            }
            self.pd.inc_value()
            for article in flatten(cat):
                
                if hasattr(article,"intro"):
                    intro = article.intro
                    text = article.text
                else:
                    intro = ""
                    text = article.text

                egg = article.date
                if isinstance(egg, QDate):
                    log.debug("convert old project QDate to datetime")
                    egg = egg.toPyDate()

                #artslug = generate_uniq_name(articles, article.title)
                artslug = article.date.strftime(self.slugform) % {"slug":slugify(article.title)}
                
                log.debug("+- article: %s date %s", artslug, egg)

                articles[artslug] = {
                    "title":escape(article.title),
                    "slug":artslug,
                    "category":slug,
                    "intro":intro,
                    "text":text,
                    "date":egg.isoformat(),
                    "tags":[slugify(tag) for tag in article.tags]
                }
                
                if self.USEGZIP:
                    articles[artslug]["intro"] = articles[artslug]["intro"].encode("utf-8").encode("zlib")
                    articles[artslug]["text"] = articles[artslug]["text"].encode("utf-8").encode("zlib")
                
                for tag in article.tags:
                    tagslug = slugify(tag)
                    if tagslug in tags:
                        amount = tags[tagslug]["amount"] + 1
                    else:
                        amount = 1
                    tags[tagslug] = {
                        "title":escape(tag),
                        "amount":amount
                    }
                self.pd.inc_value()
        with open(fname, "wb") as fout:
            dump(obj, fout)

