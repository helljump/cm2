#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snöa

from pytils.translit import slugify
from logging import debug, exception
import traceback
from utils.formlayout import fedit

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from utils.qthelpers import MyFile
from utils.tidy import sql_quote

TRUNCATE_TABLE_SQL = """
TRUNCATE TABLE `%(db_prefix)scategory`;
TRUNCATE TABLE `%(db_prefix)spost`;
TRUNCATE TABLE `%(db_prefix)stags`;
"""

CATEGORY_SQL_80 = """
INSERT INTO `%(db_prefix)scategory` VALUES
    (NULL, 0, 1, '%(rus_catname)s', '%(catname)s', '', '', '', '', '', '', 0, '', '');
SET @catid = last_insert_id();
"""

CATEGORY_SQL_85 = """
INSERT INTO `%(db_prefix)scategory` VALUES
    (NULL, 0, 1, '%(rus_catname)s', '%(catname)s', '', '', '', '', '', '', 0, '', '', '');
SET @catid = last_insert_id();
"""

ARTICLE_SQL = """
INSERT INTO `%(db_prefix)spost` VALUES
    (NULL, '%(author_name)s', '%(pubdate)s', '%(introtext)s',
    '%(fulltext)s', '', '%(rus_artname)s', '', '', @catid,
    '%(artname)s', 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, '', '', 1, '', '', '', 0,
    '%(tags)s', '');
SET @artid = last_insert_id();
"""

TAG_SQL = """INSERT INTO `%(db_prefix)stags` VALUES (NULL, @artid, '%(tag)s');
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
        mf.mask = "DLE 8 SQL file (*.sql)"

        v = [0, (0, u'8.0'), (2, u'8.5')]

        datalist = [
            (u"Файл выгрузки:", mf),
            (u"Префикс таблиц:", "dle_"),
            (u"Вставка команд очистки:", True),
            (u"Имя автора:", u"Админ"),
            (u"Версия DLE:", v)]
                
        rc = fedit(datalist, title=u"Параметры экспорта", parent=self.parent)
        if not rc:
            return False
            
        (self.fname, self.table_prefix, self.clear_tables, self.author_name,
            self.dle_ver) = rc
        return True
        
    def _write_articles(self, cat, fout):
        for art in cat.get_children():
            if self.pd: self.pd.set_text(u"Добавление статьи %s" % art.title)
            self.artcount += 1
            intro_text = getattr(art,'intro','')
            params = {"db_prefix":self.table_prefix,
                "author_name":sql_quote(self.author_name),
                "pubdate":art.date,
                "introtext":sql_quote(intro_text),
                "fulltext":sql_quote(art.text),            
                "rus_artname":sql_quote(art.title),
                "artname":slugify(art.title),
                "tags":sql_quote(",".join(art.tags))}
            egg = (ARTICLE_SQL % params).encode("utf-8")
            fout.write(egg)
            self._write_articles(art, fout)
            
            for tag in art.tags:
                params = {"db_prefix":self.table_prefix, "tag":sql_quote(tag)}
                egg = (TAG_SQL % params).encode("utf-8")
                fout.write(egg)
        
    def write(self):
        if self.pd: self.pd.set_text(u"Запись файла")
        debug("write %s", self.fname)
        
        params = {"db_prefix":self.table_prefix}
        self.artcount = 0
        
        with open(self.fname,"wt") as fout:
            
            if self.pd: self.pd.set_text(u"Вставка кода очистки")
            if self.clear_tables:
                fout.write((TRUNCATE_TABLE_SQL % params).encode("utf-8"))

            for cat in self.tree.get_children():
                if self.pd: self.pd.set_text(u"Добавление категории %s" % cat.title)
                params["catname"] = slugify(cat.title)
                params["rus_catname"] = sql_quote(cat.title)
                if self.dle_ver == 0:
                    fout.write( (CATEGORY_SQL_80 % params).encode("utf-8") )
                else:
                    fout.write( (CATEGORY_SQL_85 % params).encode("utf-8") )
                self._write_articles(cat, fout)

if __name__ == "__main__":
    import cPickle
    tree = cPickle.load(open("sireni.prt","rb"))
    export = Export(tree, "dle8.sql")
    export.config()
    export.run()
