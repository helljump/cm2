#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"


import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import os
from utils.qthelpers import MyFile
from utils.formlayout import fedit
from utils.paths import pluginpath
import pickle
import unicodecsv as csv
from youtube import YouTube
from datetime import datetime
import codecs
try:
    from plugtypes import IUtilitePlugin
except ImportError:
    IUtilitePlugin = object


log = logging.getLogger(__name__)


class ProgressDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        path = os.path.dirname(__file__)
        uic.loadUi(os.path.join(path, "dialog.ui"), self)

    def stop(self):
        self.progressBar.setRange(1, 100)
        self.progressBar.setValue(100)

    def log(self, item):
        self.listWidget.addItem(item)
        self.listWidget.scrollToBottom()

    def connect(self, th):
        self.finished.connect(th.stop)

        def complete(rc):
            item = QListWidgetItem(rc)
            item.setForeground(Qt.green)
            self.log(item)
            self.stop()
        th.complete.connect(complete)

        def error(rc):
            item = QListWidgetItem(rc)
            item.setForeground(Qt.red)
            self.log(item)
            self.stop()
        th.error.connect(error)

        def process(rc):
            item = QListWidgetItem(rc)
            item.setForeground(Qt.black)
            self.log(item)
        th.process.connect(process)


class Thread(QThread):

    complete = pyqtSignal(QString)
    process = pyqtSignal(QString)
    error = pyqtSignal(QString)

    def __init__(self, parent, queries, amount, fname, apikey, qfile, dform,
            swfile, minlen):
        QThread.__init__(self, parent)
        self.queries = queries
        self.amount = amount
        self.fname = fname
        self.apikey = apikey
        self.qfile = qfile
        self.dform = dform
        self.minlen = minlen
        self.active = True
        if os.path.isfile(swfile):
            self.stopwords = map(unicode.strip, codecs.open(swfile, "r", "UTF-8").readlines())
        else:
            self.stopwords = []

    def run(self):
        try:
            if os.path.isfile(self.qfile):
                egg = map(unicode.strip, codecs.open(self.qfile, "r", "UTF-8").readlines())
                self.queries.extend(egg)
            filters = set()
            fout = open(self.fname, 'wb')
            writer = csv.writer(fout, encoding='utf-8', delimiter=';', quotechar='\"',
                quoting=csv.QUOTE_NONNUMERIC)
            self.process.emit(u"Подключаемся")
            yt = YouTube(self.queries, self.amount, self.apikey, self.stopwords, self.minlen, self.timeq)
            for item in yt.get_items():
                if item["id"] in filters:
                    continue
                filters.add(item["id"])
                item["comments"] = yt.get_comments(item["id"])
                spam = datetime.strptime(item["uploaded"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                row = [
                    item["id"],
                    item["title"],
                    item["description"],
                    spam.strftime(self.dform),
                    item.get("rating", 5),
                    item["thumbnail"]["hqDefault"],
                    item["duration"],
                    item.get("viewCount", 100),
                    item["query"],  # data[8:data.__len__()] ->  data[9:]
                    ]
                for comment in item["comments"]:
                    row.append(comment["content"]["$t"])
                writer.writerow(row)
                self.process.emit(u"Получено " + item["title"])
                if not self.active:
                    break
            self.complete.emit(u"Сохранено в %s" % self.fname)
        except Exception, err:
            self.error.emit(u"Ошибка " + str(err))
        finally:
            fout.close()
        log.debug("thread is stoped")

    def stop(self):
        self.active = False
        log.debug("trying stop the thread")


class Plugin(IUtilitePlugin):

    TITLE = u"YoutTube Генератор Магазинов 2"
    FNAME = os.path.join(pluginpath, "youtubepro.pickle")

    TIMEQ = [
        u"all_time",
        ("all_time", u"За все время"),
        ("this_month", u"За этот месяц"),
        ("this_week", u"За эту неделю"),
        ("today", u"За сегодня"),
    ]

    def _load_settings(self):
        rc = [
                u"Как стать феей",
                "plugins/youtube_pro/queries.txt",
                1000,
                "plugins/youtube_pro/base.csv",
                "",
                "%d/%m/%Y",
                "plugins/youtube_pro/stopwords.txt",
                10,
                Plugin.TIMEQ[0], #all time
            ]
        if os.path.isfile(Plugin.FNAME):
            egg = pickle.load(open(Plugin.FNAME, "r"))
            if len(egg) == len(rc):
                rc = egg
        return rc

    def run(self, parent):
        s = self._load_settings()
        Plugin.TIMEQ[0] = s[8]
        datalist = [
            (u"Запросы(через запятую)", s[0]),
            (u"Файл запросов", MyFile(s[1], "Text(*.txt)", "r")),
            (u"Количество(на каждый запрос)", s[2]),
            (u"Выходной файл", MyFile(s[3], "Comma Separated Values(*.csv)", "w")),
            (u"API key(если пусто, то ключ по умолчанию)", s[4]),
            (u"Формат даты", s[5]),
            (u"Список стопслов", MyFile(s[6], "Text(*.txt)", "r")),
            (u"Минимальная длина комментария", s[7]),
            (u"Время публикаций", Plugin.TIMEQ),

        ]
        rc = fedit(datalist, title=Plugin.TITLE, parent=parent)

        if not rc:
            return
        pickle.dump(rc, open(Plugin.FNAME, "w"))

        queries, qfile, amount, fname, apikey, dform, swfile, minlen, timeq = rc

        pd = ProgressDialog(parent)
        pd.setWindowTitle(Plugin.TITLE)

        norm = map(unicode.strip, queries.split(","))
        th = Thread(parent, norm, amount, fname, apikey, qfile, dform, swfile, minlen)
        th.timeq = timeq # blyaa
        pd.connect(th)

        pd.show()
        th.start()
