# -*- coding: UTF-8 -*-

import logging
import os
from plugtypes import IImportPlugin
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog
from utils.article import Article
from utils.qthelpers import MyProgressDialog
from datetime import datetime
import re
import codecs

log = logging.getLogger(__name__)
default_cat = u"Новости"

def parse(finp):
    articles = []
    for item in re.finditer(r"(?imsu)<item>(.+?)</item>", finp):
        article = {
            "title":u"Без названия",
            "pubdate":datetime.now(),
            "text":"",
            "intro":"",
            "category":default_cat,
            "post_id":"0",
            "post_parent":"0",
            "tags":[]
        }
        if (not re.search("(?imsu)<wp:post_type>post</wp:post_type>", item.group(1)) and
            not re.search("(?imsu)<wp:post_type>page</wp:post_type>", item.group(1))):
            continue
        m = re.search("(?imsu)<title>(.+?)</title>", item.group(1))
        if m:
            article["title"] = m.group(1)
        m = re.search("(?imsu)<wp:post_date>(.+?)</wp:post_date>", item.group(1))
        if m:
            try:
                article["pubdate"] = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        m = re.search("(?imsu)<content:encoded><!\[CDATA\[(.+?)\]\]></content:encoded>", item.group(1))
        if m:
            article["text"] = m.group(1)
        m = re.search("(?imsu)<excerpt:encoded><!\[CDATA\[(.+?)\]\]></excerpt:encoded>", item.group(1))
        if m:
            article["intro"] = m.group(1)
        m = re.search("(?imsu)<category.+?><!\[CDATA\[(.+?)\]\]></category>", item.group(1))
        if m:
            article["category"] = m.group(1)
        m = re.search("(?imsu)<wp:post_id>(\d+)</wp:post_id>", item.group(1))
        if m:
            article["post_id"] = m.group(1)
        m = re.search("(?imsu)<wp:post_parent>(\d+)</wp:post_parent>", item.group(1))
        if m:
            article["post_parent"] = m.group(1)
        m = re.findall("(?imsu)<category domain=\"tag\"><!\[CDATA\[(.+?)\]\]></category>", item.group(1))
        if m:
            article["tags"] = m
        articles.append(article)
    return articles

class CancelException(Exception):
    pass

class Plugin(IImportPlugin):
    def run(self, parent):
        fname = QFileDialog.getOpenFileName(parent, u"Импорт", parent.current_load_path,
            u"Wordpress XML file(*.xml)")
        if not fname:
            return
        fname = unicode(fname)
        parent.current_load_path = os.path.split(fname)[0]
        pd = MyProgressDialog(u"Импорт", u"Чтение статей", u"Отмена", 0, 0, parent)
        pd.show()
        try:
            categories = {}
            root = Article()
            articles = parse(codecs.open(fname,"r","utf-8").read())
            pd.set_range(0, len(articles))
            for item in articles:
                if not categories.has_key(item["category"]):
                    cat = Article(item["category"])
                    categories[item["category"]] = cat
                    root.add_child(cat)
                else:
                    cat = categories[item["category"]]
                art = Article(item["title"], item["text"], item["tags"], item["pubdate"])
                art.intro = item["intro"]
                cat.add_child(art)
                QtGui.qApp.processEvents()
                if pd.wasCanceled():
                    raise CancelException
                pd.inc_value()
            pd.close()
            return root
        except CancelException:
            pass
        pd.close()
        return
