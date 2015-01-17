#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from plugtypes import IProcessPlugin #@UnresolvedImport
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from utils.qthelpers import MyProgressDialog
from utils.formlayout import fedit
import re
import gobo_o as gobo
import os
import traceback
import time
import logging

log = logging.getLogger(__name__)

basespath = os.path.join(*__file__.split(os.path.sep)[-3:-1])

class Thread(QThread):
    def __init__(self, parent):
        super(Thread, self).__init__(parent)
        self.error = None
        self.online = True
    def run(self):
        try:
            self.process()
        except:
            self.error = traceback.format_exc()
    def stop(self):
        self.online = False
        self.terminate()
        self.wait(100)

class MyThread(Thread):
    def process(self):
        base_dict = gobo.read(self.base)
        if self.pack:
            base_dict = gobo.pack_douples(base_dict)
        else:
            base_dict = gobo.remove_douples(base_dict)
        self.pd.set_range(1, len(self.items))
        self.pd.set_text(u"Обработка")
        self.result = 0
        egg = 1
        for item in self.items:
            if not self.online:
                break
            self.pd.set_value(egg)
            log.debug("process %s", item.title)
            text = item.article.text
            fitems = gobo.find_tokens(base_dict, text)
            fitems = gobo.xref_remove(fitems)
            if self.dupes:
                fitems = gobo.remove_founded_dupes(fitems)
            fitems = gobo.distant_filter(fitems, self.dist)
            self.result += len(fitems)
            text = gobo.goboize_text(fitems, text)
            text = text.replace("[goboclass]", self.class_)
            item.article.text = text
            self.pd.set_text(item.article.title)
            egg+=1

class Plugin(IProcessPlugin):
    def run(self, items, parent):
        bases = [fname for fname in os.listdir(basespath)
                 if fname.endswith(".gob") or fname.endswith(".ods")]
        if not bases:
            raise Exception("no gobo bases")
            return
        egg = [(fname, fname) for fname in bases]
        egg.insert(0, bases[0])
        datalist = [(u"База:", egg),
                    (u"Class:", "gobo"),
                    (u"Минимальная дистанция:", 100),
                    (u"Упаковка терминов:", True),
                    (u"Удаление дублей:", True)]
        rc = fedit(datalist, title=u"Гобонизация", parent=parent)
        if not rc:
            return
        th = MyThread(parent)
        th.base = os.path.join(basespath, rc[0]) 
        th.class_ = rc[1]
        th.dist = rc[2]
        th.pack = rc[3]
        th.dupes = rc[4]
        th.items = items
        pd = th.pd = MyProgressDialog(u"Гобонизация", u"Загрузка словаря", 
                                      u"Отмена", 0, 0, parent)
        pd.show()
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.stop()
            qApp.processEvents()
            time.sleep(0.012)
        pd.close()
        if th.error:
            raise Exception(th.error)
        QMessageBox.information(parent, u"Гобонизация", 
                                u"Добавлено терминов: %i" % th.result)
