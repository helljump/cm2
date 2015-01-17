#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

#from lxml import etree
#from pytils.translit import slugify
#from datetime import datetime 
from logging import debug, exception
#from utils.article import Article
import traceback
from utils.formlayout import fedit
import time

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from utils.qthelpers import MyFile

ZHEADER = u'''##Главная страница
@@file=index
@@module=zmodule_allpages
@@donotlist=1

'''

ZCATEGORY = u'''##%(deep)s%(rus_name)s
@@time=%(pubdate)s
@@donotlist=1
@@module=zmodule_listpages
'''

ZARTICLE = u'''##%(deep)s%(rus_name)s
@@time=%(pubdate)s
@@type=page
@@nomenuitem=1
@@nosubmenu=1
'''

ZTAGS = u'''##Все метки
@@file=tags
@@filter=asis
@@module=zmodule_tags
@@donotlist=1

'''

ZSITEMAP = u'''##Карта сайта
@@file=sitemap
@@filter=asis
@@module=zmodule_sitemap
@@donotlist=1
@@params.subpage=стр.

'''

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
        mf.mask = "Zebrum Lite Pages (*.txt)"

        comment=u"""Выгрузка для Zebrum Lite 2.0.3. Для импорта используйте parser.php <br>
        из пакета Zebrum Lite"""

        datalist = [
            (u"Файл выгрузки:", mf),
            (u"Страница меток:", True),
            (u"Страница карты сайта:", True)
            ]
                
        rc = fedit(datalist, title=u"Параметры экспорта", parent=self.parent, comment=comment)
        if not rc:
            return False
            
        (self.fname, self.add_tagspage, self.add_sitemappage) = rc
        return True
        
    def _recurse(self, cat, fout):
        
        for subitem in cat.get_children():
            if self.pd: self.pd.set_text(u"Добавление %s" % subitem.title)
            
            params = {
                "deep":"#"*self.deep,
                "rus_name":subitem.title,
                "pubdate": int(time.mktime(subitem.date.timetuple()))
            }
            
            if subitem.get_children():
                egg = (ZCATEGORY % params).encode("utf-8")
            else:
                egg = (ZARTICLE % params).encode("utf-8")
            
            fout.write(egg)
            
            if subitem.tags:
                egg = ("@@tags=%s\n" % ", ".join(subitem.tags)).encode("utf-8")
                fout.write(egg)
            desc = getattr(subitem,'intro','')
            #do_truncate_html(subitem.text, self.desc_len)
            if subitem.get_children() and desc:
                egg = ("@@description=%s\n" % desc).encode("utf-8")
                fout.write(egg)

            fout.write(subitem.text.encode("utf-8"))
            fout.write("\n\n")

            self.deep +=1
            self._recurse(subitem, fout)
            self.deep -=1
        
    def write(self):
        if self.pd: self.pd.set_text(u"Запись файла")
        debug("write %s", self.fname)        
        self.deep = 0
        
        with open(self.fname,"wt") as fout:
            
            if self.pd: self.pd.set_text(u"Вставка заголовка")
            fout.write(ZHEADER.encode("utf-8"))

            self._recurse(self.tree, fout)

            if self.add_tagspage:
                fout.write(ZTAGS.encode("utf-8"))                
            if self.add_sitemappage:
                fout.write(ZSITEMAP.encode("utf-8"))

if __name__ == "__main__":
    import cPickle
    tree = cPickle.load(open("sireni.prt","rb"))
    export = Export(tree, "c:\\xampplite\\htdocs\\zebrum\\tools\\pages.txt")
    export.config()
    export.run()
