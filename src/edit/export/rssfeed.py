#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

import logging
from feedparser import parse
import traceback
from datetime import datetime
from utils.article import Article

from PyQt4 import QtCore
from PyQt4.QtCore import QThread


log = logging.getLogger(__name__)


class Import(QThread):
    def __init__(self, fname, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.fname = unicode(fname)
        self.pd = progressdialog
        self.result = None

    def run(self):
        try:
            root = Article()
            self.pd.set_text(u"Чтение")
            entries = parse(self.fname)['entries']
            #self.pd.set_range(0,len(entries))
            cnt = 0
            self.pd.set_text(u"Добавление")
            for item in entries:
                #self.pd.inc_value()
                cnt+=1
                title = item.get('title','')
                if 'content' in item and len(item['content']) > 0 and 'value' in item['content'][0]:
                    text = item['content'][0]['value']
                else:
                    text = item.get('summary','')
                article = Article(title, text, pubdate=datetime.now())
                root.add_child(article)
            self.result = root
        except:
            log.exception("import error")
            self.error = traceback.format_exc()

    def stop(self):
        log.debug("terminate")
        self.terminate()
        log.debug("wait")
        self.wait()

if __name__ == "__main__":
    logging.basicConfig()
    reader = Import(r"rss_fhg.cgi@id=shheff&site=1&type=1&thumbs=1&items=15")
    #reader = Import(r"d:\work\promidol\test\forum.xml")
    reader.run()
    #import
    #json.dump(reader.result, open("feedreader.prt","wb"), indent=2)
