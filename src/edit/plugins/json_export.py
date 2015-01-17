#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from plugtypes import IExportPlugin
import logging 
from pytils.translit import slugify
from utils.qthelpers import MyProgressDialog
import os
import codecs
from PyQt4.QtGui import QFileDialog
import json

log = logging.getLogger(__name__)

def articles_count(item):
    egg = 1
    for subitem in item.get_children():
        egg += articles_count(subitem)
    return egg

class CancelException(Exception):
    pass

class ExportPlugin(IExportPlugin):

    def run(self, tree, parent):
        fname = QFileDialog.getSaveFileName(parent, u"Экспорт JSON", 
            parent.current_save_path, u"JSON file (*.json)")
        if fname == "":
            return
        fname = unicode(fname)
        parent.current_save_path = os.path.split(fname)[0]
        self.pd = MyProgressDialog(u"Экспорт JSON", u"Запись статей", u"Отмена", 0,
            articles_count(tree), parent)
        self.pd.show()
        try:
            self.export(tree, fname)
        except CancelException:
            pass
        self.pd.close()

    def get_articles(self, parent):
        articles = []
        for item in parent.get_children():
            if self.pd.wasCanceled():
                raise CancelException
            self.pd.inc_value()
            egg = {
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
            spam = self.get_articles(item)
            articles += egg
        return articles
    
    def export(self, tree, fname):
        data = []
        category_pk = 0
        article_pk = 0
        for item in tree.get_children():
            category_pk += 1
            egg = {
                "pk": category_pk,
                "model": "company.category",
                "fields": {
                    "title": item.title
                }
            }
            data.append(egg)
            for subitem in item.get_children():
                article_pk += 1
                if self.pd.wasCanceled():
                    raise CancelException
                self.pd.inc_value()
                egg = {
                    "pk": article_pk,
                    "model": "company.company",
                    "fields": {                        
                        "category": category_pk,
                        "description": "",
                        "image": "",
                        "site": "",
                        "phone": "",
                        "address": "",
                        "email": "",
                        "title": subitem.title,
                        "ip": "127.0.0.1",
                        "created": str(subitem.date), #"2011-06-10 00:33:54",
                        "spam": False,
                        "published": True
                    }
                }
                
                params = subitem.text.replace("\r","").split("\n\n")
                if len(params)>1:
                    egg["fields"]["description"] = "\n\n".join(params[1:])
                for row in params[0].split("\n"):
                    row = row.strip()
                    if row.lower().find("http://")==0:
                        egg["fields"]["site"] = row
                    elif row.lower().endswith(".jpg") or row.lower().endswith(".png"):
                        log.debug("image found %s", row)
                        egg["fields"]["image"] = "company/2000/01/%s" % row
                    elif row.find("+7")==0:
                        egg["fields"]["phone"] = row
                    elif row.find("@")>0:
                        egg["fields"]["email"] = row
                    else:
                        if len(row)>200:
                            log.debug("address warning %s", subitem.title)
                        egg["fields"]["address"] = row
                
                data.append(egg)

        json.dump(data, open(fname, "wt"), indent=2, encoding="utf-8")
