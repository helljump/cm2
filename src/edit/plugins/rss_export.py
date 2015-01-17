#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from datetime import datetime

DATEFORMAT = "%a, %d %b %Y %H:%M:%S +0300"
URL = "untitled.ru"

HEAD = u"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <atom:link href="http://%(URL)s/feed.xml" rel="self" type="application/xml"/> 
        <title>Сайт %(URL)s</title>
        <link>http://%(URL)s/</link>
        <description>Статьи</description>
        <language>ru</language>
        <copyright>Copyright (c) 2000-%(YEAR)i %(URL)s</copyright>
        <category>Humor, Entertainment, Sport, Games, News</category>
        <generator>RSS %(URL)s v1.0</generator>
        <lastBuildDate>%(UTC)s</lastBuildDate>
        <ttl>30</ttl>""" % {
    "URL":URL,
    "YEAR":datetime.now().year,
    "UTC":datetime.now().strftime(DATEFORMAT)
}

ITEM = u"""
        <item>
            <title>%(TITLE)s</title>
            <link>http://%(URL)s/articles/%(SLUG)s.html</link>
            <author>manager@%(URL)s (Manager)</author>
            <category domain="http://%(URL)s/articles/">Статьи</category>
            <description><![CDATA[%(CONTENT)s]]></description>
            <source url="http://%(URL)s">%(URL)s - Статьи</source>
            <pubDate>%(DATEPUB)s</pubDate>
            <guid isPermaLink="false">%(RAND)i</guid>
        </item>
"""

TAIL = """    </channel>
</rss>
"""

import logging 
from plugtypes import IExportPlugin
from pytils.translit import slugify
from utils.qthelpers import MyProgressDialog
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import QThread, QObject, SIGNAL
import os
import codecs
import Queue
from utils.formlayout import fedit
from random import randint
from xml.sax.saxutils import escape

log = logging.getLogger(__name__)

class Thread(QThread):
    def __init__(self, fname, queue, parent):
        QThread.__init__(self, parent)
        self.fname = fname
        self.queue = queue
    
    def run(self):
        self.online = True
        fout = codecs.open(self.fname, "wt", "utf-8", "replace")
        fout.write(HEAD)
        while not self.queue.empty():
            row = self.queue.get_nowait()
            self.emit(SIGNAL('export(PyQt_PyObject)'), row.title)
            params = {
                "TITLE":row.title,
                "SLUG":slugify(row.title),
                "URL":URL,
                "CONTENT":row.text, #was escape(row.text),
                "DATEPUB":row.date.strftime(DATEFORMAT),
                "RAND":randint(50000,99999)
            }
            fout.write(ITEM % params)
            if not self.online:
                break
        fout.write(TAIL)
        fout.close()
        self.emit(SIGNAL('done(PyQt_PyObject)'), "")

    def die(self):
        log.debug("try to kill %s" % QThread.currentThread())
        self.online = False
        self.wait(100)
        self.terminate()
        log.debug("killed %s" % QThread.currentThread())
        
class Plugin(IExportPlugin):
    
    def run(self, tree, parent):
        fname = QFileDialog.getSaveFileName(parent, u"Экспорт RSS", 
            parent.current_save_path, u"RSS Feed (*.xml)")
        if fname == "":
            return
        fname = unicode(fname)
        parent.current_save_path = os.path.split(fname)[0]
        
        articles = self.flatten(tree)
        
        self.pd = MyProgressDialog(u"Экспорт RSS", u"Запись статей", u"Отмена", 0,
            len(articles), parent)
                
        queue = Queue.Queue()
        for row in articles:
            queue.put(row)
        
        th = Thread(fname, queue, parent)
        QObject.connect(th, SIGNAL('export(PyQt_PyObject)'), self.export_process)
        QObject.connect(th, SIGNAL('done(PyQt_PyObject)'), self.export_done)
        self.cnt = 0
        th.start()
        self.pd.exec_()
        th.die()

    def export_process(self, rc):
        self.pd.setLabelText(rc)
        self.pd.setValue(self.cnt)
        self.cnt += 1
        
    def export_done(self, rc):
        self.pd.hide()
        if isinstance(rc, Exception):
            raise rc
        
    def flatten(self, root):
        def _recurse(tree):
            egg = []
            for item in tree.get_children():
                egg.append(item)
                egg += _recurse(item)
            return egg
        return _recurse(root)
