#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
from plugtypes import IExportPlugin
from utils.qthelpers import MyProgressDialog
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QDate
from phpserialize import dump
from pytils.translit import slugify
import os
import time
import codecs
from xml.sax.saxutils import escape

log = logging.getLogger(__name__)

header = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <articles xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
"""

footer = """</articles>
"""

page = """    <page id="%(slug)s" tags="%(categoryslug)s" key="%(tags)s" comm="no">
        <titl>%(title)s</titl>
        <desc>%(intro)s</desc>
        <author>%(author)s</author>
        <data>%(date)s</data>
        <anons>%(intro)s</anons>
        <text>%(text)s</text>
        <metatitl>%(title)s</metatitl>
    </page>
"""

def articles_count(item):
    egg = 1
    for subitem in item.get_children():
        egg += articles_count(subitem)
    return egg

def generate_uniq_name(names, new_name):
    egg = orig_egg = slugify(new_name)
    cnt = 1
    while egg in names:
        egg = "%s_%i" % (orig_egg, cnt)
        cnt += 1
    return egg.replace("-","_")

def flatten(item):
    children = []
    for subitem in item.get_children():
        children.append(subitem)
        children += flatten(subitem)
    return children

class CancelException(Exception):
    pass

class Plugin(IExportPlugin):        
    
    def run(self, tree, parent):        
        dirname = QFileDialog.getExistingDirectory(parent, u"Каталог данных Rumba XML(data)",
            parent.current_save_path);                                                 
        if dirname == "":
            return
        dirname = unicode(dirname)
        parent.current_save_path = dirname
        self.pd = MyProgressDialog(u"Экспорт", u"Запись статей", u"Отмена", 0, 
            articles_count(tree), parent)
        self.pd.show()
        try:
            self.export(tree, dirname)
        except CancelException:
            pass
        self.pd.close()
        
    def export(self, tree, dirname):
        
        categories = {}
        articles = {}
        
        for cat in tree.get_children():
            slug = generate_uniq_name(categories, cat.title)
            if isinstance(cat.date, QDate):
                cat.date = cat.date.toPyDate()
            utime = "%i" % int(time.mktime(cat.date.timetuple()))
            if not hasattr(cat,"intro"):
                cat.intro = cat.text
            categories[slug] = [ slug, cat.title, utime, cat.intro, cat.title ]
            for article in flatten(cat):
                if not hasattr(article,"intro"):
                    article.intro = ""
                artslug = generate_uniq_name(articles, article.title)
                articles[artslug] = {
                    "slug": artslug,
                    "categoryslug": slug,
                    "tags": ";".join( [ "%s-%s" % (slugify(tag).replace("-","_"), escape(tag)) 
                        for tag in article.tags if len(tag)>0 ] ),
                    "title": escape(article.title),
                    "intro": escape(article.intro),
                    "text": escape(article.text),
                    "author": "Admin",
                    "date": article.date.strftime("%a, %d %b %Y %H:%M:%S")
                }
                
        with codecs.open( os.path.join(dirname,"data.xml"), "wt", "utf-8", "replace") as fout:
            fout.write(header)
            for row in articles.itervalues():
                fout.write(page % row)
            fout.write(footer)
            
        with codecs.open( os.path.join(dirname,"category.txt"), "wt", "utf-8", "replace") as fout:
            for row in categories.itervalues():
                fout.write("|".join(row))
                fout.write("\n")
