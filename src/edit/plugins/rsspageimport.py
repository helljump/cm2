#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from plugtypes import IImportPlugin
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from utils.qthelpers import MyProgressDialog, MyFile
from utils.article import Article
from utils.formlayout import fedit
from UserString import UserString
import functools
import logging 
import urllib
import re
import Queue
from utils.tidy import autodecode, do_truncate_html

log = logging.getLogger(__name__)

comment = u"""Укажите источник импорта. Это может быть rss/atom или файл."""

class Page(UserString): pass

class RSSPageImport(IImportPlugin):    
    title_re = re.compile(u"<title>(.+?)</title>")
    body_re = re.compile(u"<body[^>]*>(.+?)</body>", re.I | re.U | re.M | re.S)
    
    def run(self, parent):
        mf = MyFile("http://lenta.ru/rss/")
        mf.mask = "feed file (*.xml)"
        mf.mode = "r"
        datalist = [(u"Файл/RSS:", mf),]
        rc = fedit(datalist, title=u"Импорт", parent=parent, comment=comment)
        if not rc:
            return
        fname = rc[0]
        self.root = Article()
        self.pd = MyProgressDialog(u"Импорт", u"Импорт RSS/Atom ленты", u"Отмена", 0, 0, parent)
        self.pd.show()
        self.queue = Queue.Queue()
        self.queue.put(ReadSourceTask(fname))
        t = Worker(self.queue)
        QObject.connect(t, SIGNAL('taskDone(PyQt_PyObject)'), self.process_done)
        t.start()
        self.pd.exec_()
        t.die()
        return self.root

    def process_done(self, rc):
        if isinstance(rc,list):
            self.amount = len(rc)
            self.pd.set_range(1,self.amount)
            self.pd.set_text(u"Грузим страницы")
            for row in rc:
                self.queue.put(ReadPageTask(row))
        elif isinstance(rc,Page):
            self.pd.inc_value()
            m = self.title_re.search(rc.data)
            title = m.group(1) if m else u"Нет заголовка"
            m = self.body_re.search(rc.data)
            text = m.group(1) if m else u"Нет текста"
            self.root.add_child(Article(title, text))
            self.amount -= 1
            if not self.amount:
                self.pd.hide()
        else:
            log.error("unknown type: %s", type(rc))

class ReadPageTask(object):
    def __init__(self, source):
        self.f = functools.partial(self.read_page, source)
    def __call__(self):
        try:
            rc = self.f()
        except Exception, err:
            log.exception("*** task exception ***")
            rc = err
        return rc
    def read_page(self, src):
        text = autodecode(urllib.urlopen(src).read())
        return Page(text)

class ReadSourceTask(object):
    templates = {
        "http://www.sitemaps.org":re.compile("<loc>(.+?)</loc>"),
        "<rss":re.compile("<link>(.+?)</link>")
    }
    def __init__(self, source):
        self.f = functools.partial(self.read_urls, source)
    def __call__(self):
        try:
            rc = self.f()
        except Exception, err:
            log.exception("*** task exception ***")
            rc = err
        return rc
    def read_urls(self, src):
        if not src.startswith("http"):
            src = "file:%s" % src
        text = urllib.urlopen(src).read()
        for k,v in self.templates.items():
            if text.find(k)!=-1:
                log.debug("found %s", k)
                urls = v.findall(text)
                break
        else:
            log.debug("simply split")
            urls = [url.strip() for url in text.split("\n") if len(url.strip())>4]
        log.debug("urls found %i", len(urls))
        return urls

class Worker(QThread):
    def __init__(self, queue, parent=None):
        QThread.__init__(self,    parent)
        self.queue = queue
        self.online = True
    def run(self):
        log.debug("start %s" % QThread.currentThread())
        while self.online:
            try:
                task = self.queue.get_nowait()
                result = task()
                self.emit(SIGNAL('taskDone(PyQt_PyObject)'), result)
            except Queue.Empty:
                QThread.usleep(10)
        log.debug("stop %s" % QThread.currentThread())
    def die(self):
        self.online = False
        self.wait(100)
        self.terminate()
