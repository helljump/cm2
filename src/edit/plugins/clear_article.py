#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from plugtypes import IArticlePlugin #@UnresolvedImport
from datetime import datetime
#from PyQt4 import QtGui

class MegaClear(IArticlePlugin):
    def run(self, fields, parent):
        """title, text, intro, date, tags"""
        return {"title":u"Новый заголовок - (%s)" % fields["title"],
                "intro":u"test intro",
                "date":datetime(2010, 10, 10, 0, 0, 0)}
