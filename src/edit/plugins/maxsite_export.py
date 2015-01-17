#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

try:
    from plugtypes import IExportPlugin
except ImportError:
    IExportPlugin = object
    
import logging 
from pytils.translit import slugify
from utils.qthelpers import MyProgressDialog, MyFile
import os
import sys
import codecs
from utils.formlayout import fedit
from utils.tidy import sql_quote

log = logging.getLogger(__name__)

HEADER = u"""# demo

INSERT INTO _PREFIX_options (options_key, options_value) VALUES ('active_plugins', '_serialize_a:4:{i:0;s:8:"category";i:1;s:10:"pagination";i:2;s:10:"randomtext";i:3;s:10:"text_block";}');

###

INSERT INTO _PREFIX_options (options_key, options_value, options_type) VALUES ('sidebars-1', '_serialize_a:2:{i:0;s:19:"text_block_widget 1";i:1;s:15:"category_widget";}', 'sidebars');

###

INSERT INTO _PREFIX_options (options_key, options_value, options_type) VALUES ('sidebars-2', '_serialize_a:1:{i:0;s:19:"text_block_widget 2";}', 'sidebars');

###

INSERT INTO _PREFIX_options (options_key, options_value, options_type) VALUES ('sidebars-3', '_serialize_a:1:{i:0;s:17:"randomtext_widget";}', 'sidebars');

###

INSERT INTO _PREFIX_options (options_key, options_value, options_type) VALUES ('text_block_widget_1', '_serialize_a:3:{s:6:"header";s:0:"";s:4:"text";s:39:"Это текстовый виджет.";s:4:"type";s:4:"html";}', 'plugins');

###

INSERT INTO _PREFIX_options (options_key, options_value, options_type) VALUES ('text_block_widget_2', '_serialize_a:3:{s:6:"header";s:0:"";s:4:"text";s:47:"Еще один текстовый виджет";s:4:"type";s:4:"html";}', 'plugins');

###

INSERT INTO _PREFIX_options (options_key, options_value, options_type) VALUES ('category_widget_0', '_serialize_a:9:{s:6:"header";s:14:"Рубрики";s:6:"format";s:49:"[LINK][TITLE]<sup>[COUNT]</sup>[/LINK]<br>[DESCR]";s:14:"format_current";s:49:"<span>[TITLE]<sup>[COUNT]</sup></span><br>[DESCR]";s:7:"include";s:0:"";s:7:"exclude";s:0:"";s:10:"hide_empty";s:1:"0";s:5:"order";s:13:"category_name";s:9:"order_asc";s:3:"ASC";s:13:"include_child";s:1:"0";}', 'plugins');

"""

CATEGORY = u"""###

INSERT INTO _PREFIX_category (category_name, category_desc, category_slug) VALUES 
"""

#('Астрономия', 'Астрономические заметки', 'astro'), 
#('Физика', 'Физические заметки', 'phisic'), 
#('Биология', 'Заметки о животных', 'bio');

ARTICLE = u"""

###

INSERT INTO _PREFIX_page (page_id_autor, page_title, page_content, page_slug, page_date_publish) VALUES """

#(1, 'Галактика', 'Гала́ктика - гравитационно-связанная система из звёзд.', 'galactic', DATE_ADD(NOW(), INTERVAL -4 HOUR_MINUTE) );

CAT2OBJ = u"""
###

INSERT INTO _PREFIX_cat2obj (page_id, category_id) VALUES 
"""

#(3, 3);

comment = u"""Скопируйте полученный файл в каталог CMS "/application/views/install/"
под именем "demo.sql" и проинсталлируйте CMS с установкой демо-данных"""

class CancelException(Exception):
    pass

class MaxSiteExport(IExportPlugin):
    
    def run(self, tree, parent):
        mf = MyFile("demo.sql")
        mf.mask = "Mysql query file (*.sql)"
        mf.mode = "w"
        datalist = [(u"Файл:", mf),]
        rc = fedit(datalist, title=u"Экспорт", parent=parent, comment=comment)
        if not rc:
            return
        export_file = rc[0]
        if not export_file:
            return
        self.export_file = unicode(export_file).encode(sys.getfilesystemencoding())
        self.tree = tree
        self.pd = MyProgressDialog(u"Экспорт", u"Запись статей", u"Отмена", 0,
            self.articles_count(tree), parent)
        self.pd.show()
        try:
            self.export()
        except CancelException:
            pass
        self.pd.close()

    def articles_count(self, root):
        def _recurse(item):
            egg = 1
            for subitem in item.get_children():
                egg += _recurse(subitem)
            return egg
        return _recurse(root)

    def get_articles(self, parent):
        articles = []
        for item in parent.get_children():
            if self.pd.wasCanceled():
                raise CancelException
            self.pd.inc_value()
            #(1, 'Галактика', 'Гала́ктика - гравитационно-связанная система из звёзд.', 'galactic', DATE_ADD(NOW(), INTERVAL -4 HOUR_MINUTE) );
            egg = "(1, '%s', '%s', '%s', '%s')" % (sql_quote(item.title), sql_quote(item.text),
                slugify(item.title), str(item.date))
            #log.debug("%s" % egg)
            articles.append(ARTICLE+egg)
            articles += self.get_articles(item)
        return articles

    def export(self):
        cat_id = 3
        article_id = 3
        categories = []
        articles = []
        cat2obj = []
        for item in self.tree.get_children():
            #('Астрономия', 'Астрономические заметки', 'astro'), 
            egg = "('%s', '%s', '%s')" % (sql_quote(item.title), 
                sql_quote(getattr(item, "intro", "")), slugify(item.title))
            log.debug("%s", egg)
            categories.append(egg)
            new_articles = self.get_articles(item)
            articles += new_articles
            log.debug("articles %i", len(new_articles))            
            cat2obj += ["(%i, %i)" % (id+article_id, cat_id) for id in range(0,len(new_articles))]
            cat_id += 1
            article_id += len(new_articles)
        with codecs.open(self.export_file, "wt", "utf-8", "replace") as fout:
            fout.write(HEADER)
            fout.write(CATEGORY)
            fout.write(", ".join(categories))
            fout.write(";")
            fout.write(";".join(articles))
            fout.write(";\n")
            fout.write(CAT2OBJ)
            fout.write(",\n".join(cat2obj))
            fout.write(";\n")
