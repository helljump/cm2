#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from pytils.translit import slugify
from logging import debug, exception
import traceback
from utils.formlayout import fedit

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from utils.qthelpers import MyFile
from utils.tidy import sql_quote

TRUNCATE_TABLE_SQL = u"""TRUNCATE TABLE `%(db_prefix)ssections`;
TRUNCATE TABLE `%(db_prefix)scategories`;
TRUNCATE TABLE `%(db_prefix)scontent`;

"""

SECTION_SQL = u"""INSERT INTO `%(db_prefix)ssections` 
    VALUES (NULL,'%(rus_name)s','','%(name)s','','content', 'left','',1,0,
    '0000-00-00 00:00:00',1,0,1,'');
SET @secid = last_insert_id();

"""

CATEGORY_SQL = u"""INSERT INTO `%(db_prefix)scategories`
    VALUES (NULL,0,'%(rus_catname)s','','%(catname)s','',@secid,'left','%(description)s',1,0,
    '0000-00-00 00:00:00',NULL,1,0,0,'');
SET @catid = last_insert_id();

"""

ARTICLE_SQL = u"""INSERT INTO `%(db_prefix)scontent` VALUES
    (NULL,'%(rus_artname)s','%(artname)s','','%(introtext)s','%(fulltext)s',1,@secid,0,@catid,
    '%(pubdate)s',%(author_id)i,'%(author_name)s','%(pubdate)s',%(author_id)i,0,
    '0000-00-00 00:00:00','%(pubdate)s','0000-00-00 00:00:00','','','',1,0, %(artcount)i,
    '%(tags)s', '', 0, 0, '');

"""

class ExportThread(QThread):
    def __init__(self, tree, fname, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.tree = tree
        self.fname = unicode(fname)
        self.pd = progressdialog
        self.parent = parent
        
    def run(self):
        try:
            self.write()
        except:
            exception("export error")
            self.error = traceback.format_exc()
                
    def stop(self):
        debug("terminate")
        self.terminate()
        debug("wait")
        self.wait()

class Export(ExportThread):
    
    def config(self):
 
        mf = MyFile(self.fname)
        mf.mask = "Joomla 1.5 SQL file (*.sql)"

        datalist = [
            (u"Файл выгрузки:", mf),
            (u"Префикс таблиц:", "jos_"),
            (u"Вставка команд очистки:", True),
            (u"Имя автора:", u"Админ"),
            (u"Id автора(62-admin):", 62)
        ]
                
        rc = fedit(datalist, title=u"Параметры экспорта", parent=self.parent)
        if not rc:
            return False
            
        (self.fname, self.table_prefix, self.clear_tables, self.author_name,
            self.author_id) = rc
        
        return True
        
    def _write_articles(self, cat, fout):
        for art in cat.get_children():
            if self.pd: self.pd.set_text(u"Добавление статьи %s" % art.title)
            self.artcount += 1
            intro_text = getattr(art, 'intro', '')
            params = {"db_prefix":self.table_prefix,
                "rus_artname":sql_quote(art.title),
                "artname":slugify(art.title),
                "introtext":sql_quote(intro_text),
                "fulltext":sql_quote(art.text),
                "pubdate":art.date,
                "author_id":self.author_id,
                "author_name":sql_quote(self.author_name),
                "artcount":self.artcount,
                "tags":sql_quote(",".join(art.tags))}
            egg = (ARTICLE_SQL % params).encode("utf-8")
            fout.write(egg)
            self._write_articles(art, fout)
        
    def write(self):
        if self.pd: self.pd.set_text(u"Запись файла")
        debug("write %s", self.fname)
        
        params = {"db_prefix":self.table_prefix}
        self.artcount = 0
        
        with open(self.fname, "wt") as fout:
            
            if self.pd: self.pd.set_text(u"Вставка кода очистки")
            if self.clear_tables:
                fout.write((TRUNCATE_TABLE_SQL % params).encode("utf-8"))
                
            if self.pd: self.pd.set_text(u"Добавление секции")
            params["name"] = "articles"
            params["rus_name"] = u"Статьи"
            fout.write((SECTION_SQL % params).encode("utf-8"))

            for cat in self.tree.get_children():
                if self.pd: self.pd.set_text(u"Добавление категории %s" % cat.title)
                params["catname"] = slugify(cat.title)
                params["rus_catname"] = sql_quote(cat.title)
                params["description"] = sql_quote(cat.text)
                fout.write((CATEGORY_SQL % params).encode("utf-8"))
                self._write_articles(cat, fout)

if __name__ == "__main__":
    import cPickle
    tree = cPickle.load(open("sireni.prt", "rb"))
    export = Export(tree, "sireni-j15.sql")
    export.config()
    export.run()
