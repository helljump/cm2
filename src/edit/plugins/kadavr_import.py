# -*- coding: UTF-8 -*-

import logging
import os
from plugtypes import IImportPlugin
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog
from phpserialize import load
from utils.article import Article
from utils.qthelpers import MyProgressDialog
from datetime import datetime

log = logging.getLogger(__name__)

class CancelException(Exception):
    pass

class Plugin(IImportPlugin):
    def run(self, parent):
        fname = QFileDialog.getOpenFileName(parent, u"Импорт", parent.current_load_path, 
            u"kadavr engine file(*.kad)")
        if not fname:
            return
        fname = unicode(fname)
        parent.current_load_path = os.path.split(fname)[0]
        pd = MyProgressDialog(u"Импорт", u"Чтение статей", u"Отмена", 0, 0, parent)
        pd.show()
        try:
            root = Article()
            egg = load(open(fname,"rb"))
            eggslug = egg["tags"]
            gziped = egg.get("packed", False)
            for cslug, fields in egg["categories"].items():
                cat = Article(unicode(fields["title"], "utf-8"))
                root.add_child(cat)
                for aslug, afields in egg["articles"].items():
                    if afields["category"] == cslug:
                        tags = []
                        for i, tagslug in afields["tags"].items():
                            tags.append(unicode(eggslug[tagslug]["title"], "utf-8"))
                        #print afields["date"]
                        try:
                            pubdate = datetime.strptime(afields["date"], "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError: #no millis
                            pubdate = datetime.strptime(afields["date"], "%Y-%m-%dT%H:%M:%S")
                        if gziped:
                            afields["text"] = afields["text"].decode("zlib")
                            afields["intro"] = afields["intro"].decode("zlib")
                        art = Article(unicode(afields["title"], "utf-8"), unicode(afields["text"], "utf-8"), tags, pubdate)
                        art.intro = unicode(afields["intro"], "utf-8")
                        cat.add_child(art)
                    QtGui.qApp.processEvents()
                    if pd.wasCanceled():
                        raise CancelException
            pd.close()
            return root
        except CancelException:
            pass
        pd.close()
        return
