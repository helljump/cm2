#! /usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
import time
import re
import os
import sys
import Queue
import socket
from urlparse import urljoin
import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtWebKit

from webstemmer.textcrawler import TextCrawler
from webstemmer.zipdb import ACLDB, Dumper
from webstemmer.analyze import LayoutAnalyzer, PageFeeder
from webstemmer.extract import LayoutPatternSet, LayoutPattern, TextExtractor

from utils.tidy import autodecode
from utils.formlayout import fedit
from utils.paths import homepath
from helpers import *

import icons

URL = "http://lenta.ru"
MAXLEVEL = 3
DENIED = r'\.(jpg|jpeg|gif|png|tiff|swf|mov|wmv|wma|ram|rm|rpm|gz|zip|class)\b'
USER_AGENT = "GoboCrawler/1.0"

socket.setdefaulttimeout(10)

class PagesModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self)
        self.labels = [u"Адрес", u"Размер"]
        self.cache = []
    def rowCount(self, parent):
        return len(self.cache)
    def columnCount(self, parent):
        return len(self.labels)
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        row = index.row()
        col = index.column()
        value = ""
        if col==0:
            value = self.cache[row][0]
        else:
            value = len(self.cache[row][1])
        return QVariant(value)
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section + 1)
        return QVariant()
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    def removeRows(self, pos, rows, index=QModelIndex()):
        self.beginRemoveRows(index, pos, pos + rows - 1);
        for i in range(rows):
            self.cache.pop(pos)
        self.endRemoveRows()
        return True

class SpiderDialog(QDialog):

    pklfile = os.path.join(homepath, "treeedit", "spider.pkl")

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle(u"Универсальный парсер")
        self.resize(800,600)
        l = QGridLayout(self)
        tb = ToolBar(self)
        tb.addAction(QIcon(":/ico/spider_web.png"), u"Запуск паука", self.process)
        tb.addAction(QIcon(":/ico/delete.png"), u"Удалить страницы", self.remove_pages)
        tb.addSeparator()
        self.analize_tb = tb.addAction(QIcon(":/ico/android.png"), u"Анализ", self.analyze)
        tb.addSeparator()
        self.export_tb = tb.addAction(QIcon(":/ico/filter.png"), u"Экспорт", self.extract)
        tb.addSeparator()
        tb.addAction(QIcon(":/ico/moneybox.png"), u"Экспорт без обработки", self.extract_asis)
        l.addWidget(tb, 0, 0)

        splitter = QSplitter(self)
        splitter.setFrameShape(QFrame.StyledPanel)
        splitter.setFrameShadow(QFrame.Raised)
        l.addWidget(splitter, 1, 0)

        self.table = QTableView(splitter)
        model = PagesModel(self.table)
        self.table.setModel(model)
        self.table.verticalHeader().setDefaultSectionSize(
            self.table.verticalHeader().fontMetrics().height() + 4)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self.view_article)

        self.webview = QtWebKit.QWebView(splitter)
        self.webview.setUrl(QUrl("about:blank"))

        splitter.setSizes([10,100])

        self.pd = ProgressLogDialog(u"Обработка", self)
        self.pd.setModal(True)

        self.patterns = []
        self.export_tb.setEnabled(False)

        try:
            if os.path.isfile(self.pklfile):
                egg = pickle.load(open(self.pklfile,"rb"))
                self.table.model().cache = egg
                self.table.model().reset()
        except:
            log.exception("*** SPIDER PICKLE ERROR ***")

    def view_article(self, index):
        row = index.row()
        model = self.table.model()
        self.webview.setHtml(model.cache[row][1])

    def process(self):
        self.patterns = []
        datalist = [(u"Начальный адрес:", URL),
                    (u"Глубина:", MAXLEVEL),
                    (None,u"<small>Максимальная глубина рекурсии при прохождению по ссылкам со страниц</small>"),
                    (u"Игнорировать:", DENIED),
                    (None,u"<small>Регулярное выражение для указания исключений</small>"),
                    (u"USER_AGENT",USER_AGENT)]
        rc = fedit(datalist, title=u"Паук", parent=self,
            icon=QIcon(":/ico/spider_web.png"))
        if not rc:
            return

        queue = Queue.Queue()
        th = Worker(queue, self)
        QObject.connect(th, SIGNAL('taskDone(PyQt_PyObject)'), self.callback)
        th.start()

        self.pd.clear()
        self.pd.setWindowTitle(u"Паук")
        self.pd.set_range(0,10)
        self.pd.set_label(u"Парсим сайт")
        self.pd.progress.setTextVisible(False)
        queue.put(CrawlerTask(rc))
        self.pd.exec_()

        th.die()

    def remove_pages(self):
        rows = [ndx.row() for ndx in self.table.selectedIndexes() if ndx.column() == 0]
        rows.sort(reverse=True)
        for row in rows:
            self.table.model().removeRows(row, 1)

    def callback(self, rc):
        if isinstance(rc,tuple):
            self.pd.log("%s: %i" % (rc[0], len(rc[1])))
            v = self.pd.get_value()
            if v>9:
                self.pd.set_value(0)
            self.pd.set_value(v+1)
            model = self.table.model()
            egg = len(model.cache)
            model.beginInsertRows(QModelIndex(), egg, egg)
            spam = (rc[0], autodecode(rc[1]))
            model.cache.append(spam)
            model.endInsertRows()
        elif rc is None:
            self.pd.hide()
        else:
            log.error("thread error: %s", rc)

    def closeEvent(self, e):
        pickle.dump(self.table.model().cache,open(self.pklfile,"wb"))
        e.accept()

    def analyze(self):
        self.patterns = []
        cluster_threshold = 97
        title_threshold = 60
        limiter = 5
        datalist = [(u"Порог кластеризации(%):", cluster_threshold),
                    (u"Порог заголовка(%):", title_threshold),
                    (None,u"Измените эти значения если анализатор неверно\nопределеляет значимые фрагменты страницы"),
                    (u"Анализировать не более(статей):", limiter),
                    (u"Количество дополнительных фрагментов(не более):", 0)
                    ]
        rc = fedit(datalist, title=u"Анализ страниц", parent=self,
            icon=QIcon(":/ico/android.png"))
        if not rc:
            return
        cluster_threshold = rc[0]/100.0
        title_threshold = rc[1]/100.0
        limit = rc[2]
        max_sample = rc[3]

        queue = Queue.Queue()
        limited = self.table.model().cache[:limit]
        for row in limited:
            log.debug("queued: %s", row[0])
            queue.put((row[0], row[1]))

        queue.put("STOP")

        th = AnalyzeThread(cluster_threshold, title_threshold, queue, max_sample, self)
        QObject.connect(th, SIGNAL('pageFeed(PyQt_PyObject)'), self.callback_pagefeed)
        QObject.connect(th, SIGNAL('appendPattern(PyQt_PyObject)'), self.callback_appendpattern)
        QObject.connect(th, SIGNAL('taskDone()'), self.callback_taskdone)
        th.start()
        self.pd.clear()
        self.pd.setWindowTitle(u"Анализ")
        log.debug("articles for analyze: %i", len(limited))
        self.pd.set_range(0,len(limited))
        self.pd.set_label(u"Анализ статей")
        self.pd.progress.setTextVisible(False)
        self.pd.exec_()
        th.die()
        if self.patterns:
            self.export_tb.setEnabled(True)

    def callback_taskdone(self):
        self.pd.log(u"<font color='blue'>Анализ закончен</font>")
        #self.pd.hide()

    def callback_pagefeed(self, name):
        self.pd.inc_value()
        self.pd.log(u"Добавлена статья: %s" % name)

    def callback_appendpattern(self, rc):
        self.pd.log(u"<font color='green'>+ Сгенерирован шаблон на базе адреса: %s</font>" % rc[1])
        self.patterns.append(rc)

    def extract_asis(self):
        self.pd.clear()
        self.pd.setWindowTitle(u"Экспорт")
        self.pd.set_range(0,len(self.table.model().cache))
        self.pd.set_label(u"Экспорт страниц без обработки")
        self.pd.progress.setTextVisible(False)
        for row in self.table.model().cache:
            self.pd.inc_value()
            # TypeError: decoding Unicode is not supported
            egg = row[0]
            if not isinstance(egg, unicode):
                egg = unicode(row[0],"utf-8")
            self.pd.log(u"<font color='green'>Добавили статью: %s</font>" % egg)
            self.emit(SIGNAL('addArticle(PyQt_PyObject)'), row)
        self.hide()

    def extract(self):
        pat_threshold = 80
        diffscore_threshold = 50
        datalist = [(u"Порог соответствия шаблону(%):", pat_threshold),
                    (u"Порог отличия(%):", diffscore_threshold),
                    (u"Минимальный размер статьи(символов):", 500)
                    ]
        rc = fedit(datalist, title=u"Экспорт", parent=self, icon=QIcon(":/ico/filter.png"))
        if not rc:
            return
        pat_threshold = rc[0]/100.0
        diffscore_threshold = rc[1]/100.0
        minsize = rc[2]

        queue = Queue.Queue()
        for row in self.table.model().cache:
            queue.put(row)

        pat_queue = Queue.Queue()
        for row in self.patterns:
            pat_queue.put(row)

        th = ExtractThread(pat_threshold, diffscore_threshold, queue, pat_queue, minsize, self)
        QObject.connect(th, SIGNAL('addArticle(PyQt_PyObject)'), self.extract_addarticle)
        QObject.connect(th, SIGNAL('logIt(PyQt_PyObject)'), self.extract_log)

        th.start()
        self.pd.clear()
        self.pd.setWindowTitle(u"Экспорт")
        self.pd.set_range(0,len(self.table.model().cache))
        self.pd.set_label(u"Обработка страниц шаблоном")
        self.pd.progress.setTextVisible(False)
        self.pd.exec_()
        th.die()

    def extract_addarticle(self, rc):
        self.pd.log(u"<font color='green'>Добавили статью: %s</font>" % unicode(rc[0],"utf-8"))
        self.emit(SIGNAL('addArticle(PyQt_PyObject)'), rc)
        self.pd.inc_value()

    def extract_log(self, mess):
        self.pd.log(mess)
        #self.pd.hide()

class DieThread(QThread):
    def die(self):
        log.debug("try to kill %s" % QThread.currentThread())
        self.online = False
        self.wait(100)
        self.terminate()
        log.debug("killed %s" % QThread.currentThread())

class AnalyzeThread(DieThread):
    def __init__(self, cluster_threshold, title_threshold, queue, max_sample, parent):
        DieThread.__init__(self, parent)
        self.cluster_threshold = cluster_threshold
        self.title_threshold = title_threshold
        self.max_sample = max_sample
        self.queue = queue
    def run(self):
        debug = 0
        score_threshold = 100
        default_charset = 'utf-8'
        acldb = None
        linkinfo = 'linkinfo'
        try:
            analyzer = LayoutAnalyzer(debug=debug)
            feeder = PageFeeder(analyzer, default_charset=default_charset, debug=debug)
            for row in iter(self.queue.get, "STOP"):
                feeder.feed_page(row[0], row[1])
                self.emit(SIGNAL('pageFeed(PyQt_PyObject)'), row[0])
            feeder.close()
            for c in analyzer.analyze(self.cluster_threshold, self.title_threshold,
                self.max_sample):
                if c.pattern and score_threshold <= c.score:
                    egg = (c.score, c.name, c.title_sectno, c.pattern)
                    self.emit(SIGNAL('appendPattern(PyQt_PyObject)'), egg)
            rc = None
        except Exception, err:
            log.exception("*** task exception ***")
            rc = err
        self.emit(SIGNAL('taskDone()'))

class CrawlerTask(object, Dumper):
    def __init__(self, params):
        self.params = params
    def __call__(self):
        try:
            starturl = self.params[0]
            maxlevel = self.params[1]
            baseid = time.strftime('%Y%m%d%H%M')
            acldb = ACLDB()
            acldb.add_deny(self.params[2])
            acldb.add_allow('^'+re.escape(urljoin(starturl, '.')))
            tc = TextCrawler(self, starturl, baseid, acldb=acldb, maxlevel=maxlevel,
                default_charset="utf-8", delay=0.5, timeout=30)
            tc.USER_AGENT = self.params[3]
            tc.run()
            rc = None
        except Exception, err:
            log.exception("*** task exception ***")
            rc = err
        return rc
    def feed_page(self, name, data):
        name = "/".join(name.split("/")[1:])
        QThread.currentThread().emit(SIGNAL('taskDone(PyQt_PyObject)'), (name, data))

class ExtractThread(DieThread, LayoutPatternSet):

    def __init__(self, pat_threshold, diffscore_threshold, queue, pat_queue, minsize, parent):
        DieThread.__init__(self, parent)
        LayoutPatternSet.__init__(self, debug=0)
        self.pat_threshold = pat_threshold
        self.diffscore_threshold = diffscore_threshold
        self.queue = queue
        self.pat_queue = pat_queue
        self.minsize = minsize

    def run(self):
        debug = 0
        mainscore_threshold = 50
        default_charset = codec_out = 'utf-8'
        strict = False
        try:
            patternset = self#MyLayoutPatternSet(debug=debug)

            while not self.pat_queue.empty():
                (score, name, title_sectno, pattern) = self.pat_queue.get_nowait()
                main_sectno = -1
                patternset.pats.append(
                    LayoutPattern(name, score, title_sectno, main_sectno, pattern))
                self.emit(SIGNAL('logIt(PyQt_PyObject)'), u"Добавили шаблон: %s" % name)

            consumer = TextExtractor(patternset, self.pat_threshold, self.diffscore_threshold,
                mainscore_threshold, default_charset=default_charset,
                codec_out=codec_out, strict=strict, debug=debug)

            while not self.queue.empty():
                article = self.queue.get_nowait()
                consumer.feed_page(article[0], article[1])
                self.emit(SIGNAL('logIt(PyQt_PyObject)'), u"Обработали страницу: %s" % article[0])

            rc = None
        except Exception, err:
            log.exception("*** task exception ***")
            rc = err
        self.emit(SIGNAL('logIt(PyQt_PyObject)'), u"<font color='blue'>Экспорт закончен</font>")

    def dump_text(self, name, tree, pat_threshold, diffscore_threshold, main_threshold,
                    codec_out='utf-8', strict=True):
        enc = lambda x: x.encode(codec_out, 'replace')
        (pat1, layout) = self.identify_layout(tree, pat_threshold, strict=strict)
        if layout:
            log.debug('!MATCHED: %s', name)
            title = "untitled"
            text = "no text"
            for sectno in xrange(len(layout)):
                sect = layout[sectno]
                if sectno == pat1.title_sectno:
                    for b in sect.blocks:
                        title = enc(b.orig_text)
                elif diffscore_threshold <= sect.diffscore:
                    if pat1.title_sectno < sectno and main_threshold <= sect.mainscore:
                        egg = []
                        for b in sect.blocks:
                            egg.append(enc(b.orig_text))
                        text = "\n\n".join(egg)
            if len(text)>self.minsize:
                egg = (title, text)
                self.emit(SIGNAL('addArticle(PyQt_PyObject)'), egg)

def test(art):
    print art[0]

if __name__ == "__main__":
    #pklfile = "grab.pkl"
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    dlg = SpiderDialog(None)
    QObject.connect(dlg, SIGNAL('addArticle(PyQt_PyObject)'), test)
    dlg.exec_()
