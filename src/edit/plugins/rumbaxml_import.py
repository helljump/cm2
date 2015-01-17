# -*- coding: UTF-8 -*-

import logging
import os
from plugtypes import IImportPlugin
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog
from lxml import etree
from datetime import datetime
from utils.article import Article
from utils.qthelpers import MyProgressDialog

log = logging.getLogger(__name__)

class CancelException(Exception):
    pass

class Plugin(IImportPlugin):
    def run(self, parent):
        fname = QFileDialog.getOpenFileName(parent, u"Импорт", parent.current_load_path, 
            u"RumbaXML(*.xml)")
        if not fname:
            return
        fname = unicode(fname)
        parent.current_load_path = os.path.split(fname)[0]
        pd = MyProgressDialog(u"Импорт", u"Чтение статей", u"Отмена", 0, 0, parent)
        pd.show()
        try:
            root = Article()
            tree = etree.parse(fname)
            catdict = {}
            for page in tree.xpath("page"):
                log.info(page.attrib["id"])            
                category = page.attrib["tags"]
                
                egg = page.attrib["key"]
                if(egg!=""):
                    tags = [tag.split("-")[1] for tag in egg.split(";") if tag!=""]
                else:
                    tags = []
                title = page.xpath("titl/text()")[0]
                
                #desc = page.xpath("desc/text()")[0]
                
                egg = page.xpath("data/text()")[0].replace(" +0000","")
                date = datetime.strptime(egg, "%a, %d %b %Y %H:%M:%S") #datetime
                
                intro = page.xpath("anons/text()")[0]
                
                try:
                    text = page.xpath("text/text()")[0]
                except IndexError:
                    log.warning("no text")
                    text = u""
                
                art = Article(title, text, tags, date)
                art.intro = intro
                
                if not catdict.has_key(category):
                    catdict[category] = Article(category)
                    root.add_child(catdict[category])
                catdict[category].add_child(art)
                
                QtGui.qApp.processEvents()
                if pd.wasCanceled():
                    raise CancelException
                
            pd.close()
            return root
        except CancelException:
            pass
        pd.close()
        return
