#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"


import requests
import os
import random
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:
    from plugtypes import IProcessPlugin
    from utils.formlayout import fedit
except:
    IProcessPlugin = object

import logging

log = logging.getLogger(__name__)


KEY = 'trnsl.1.1.20130728T135808Z.c6f90aaf09ac89f7.a3dd7f198e12a5ca5cf1e3afdd67653b5d0843a9'
DOC = 'http://api.yandex.ru/translate/doc/dg/concepts/About.xml'


def createProgress(title, label, from_=0, to_=0, parent=None):
    dlg = QProgressDialog(label, u"Отмена", from_, to_, parent)
    dlg.setWindowTitle(title)
    dlg.setModal(True)
    dlg.setMinimumDuration(1)
    dlg.setFixedWidth(400)
    return dlg


class AsyncThread(QThread):

    task_done = pyqtSignal(QString)

    def __init__(self, parent, items, translator):
        QThread.__init__(self, parent)
        self.items = items
        self.t = translator

    def run(self):
        for item in self.items:
            try:
                title = self.t.translate(item.article.title)
                text = self.t.translate(item.article.text)
                if hasattr(item.article, "intro"):
                    intro = self.t.translate(item.article.intro)
                    item.article.intro = intro
                item.article.text = text
                item.article.title = title
                self.task_done.emit(u"Переведено " + item.article.title)
            except Exception, err:
                log.exception('translate error')
                self.task_done.emit(u"Ошибка " + str(err))


class Translator(object):

    BLOCKSIZE = 2000
    TRANSURL = "https://translate.yandex.net/api/v1.5/tr.json/translate"

    def __init__(self, lang="ru-en", proxy=False):
        if proxy and os.path.isfile("proxy.txt"):
            self.proxy = map(str.strip, open("proxy.txt", "r").readlines())
        else:
            self.proxy = None
        self.lang = lang

    def _get_random_proxy(self):
        if self.proxy:
            return {"http": random.choice(self.proxy)}
        else:
            return {}

    def _split(self, text):
        blocks = []
        acc = ""
        for row in re.split("([\.\?\!])", text):
            if len(acc) + len(row) < Translator.BLOCKSIZE:
                acc += row
            else:
                blocks.append(acc)
                acc = row
        blocks.append(acc)
        return blocks

    def translate(self, text, format="plain"):
        assert type(text) == unicode
        rows = self._split(text)
        newtext = []
        for row in rows:
            params = {
                'key': KEY,
                "text": row,
                "format": format,
                "lang": self.lang
            }
            rc = requests.post(Translator.TRANSURL, data=params, proxies=self._get_random_proxy())
            if rc.status_code != 200:
                raise Exception("Translate error " + str(rc))
            newtext.append(rc.json()["text"][0])
        return "".join(newtext)


class Process(IProcessPlugin):

    LANGS = [
        u"en-ru",
        ("en-ru", u"С английского на русский "),
        ("ru-en", u"С русского на английский"),
        ("ru-uk", u"С русского на украинский"),
        ("uk-ru", u"С украинского на русский"),
        ("pl-ru", u"С польского на русский"),
        ("ru-pl", u"С русского на польский"),
        ("tr-ru", u"С турецкого на русский"),
        ("ru-tr", u"С русского на турецкий"),
        ("de-ru", u"С немецкого на русский"),
        ("ru-de", u"С русского на немецкий")
    ]

    def run(self, items, parent):

        datalist = [
            (u"Языки перевода", Process.LANGS),
            (u"Использовать прокси(proxy.txt):", False),
        ]
        rc = fedit(datalist, title=u"Экспорт текстовых файлов", parent=parent)
        if not rc:
            return

        tr = Translator(lang=rc[0], proxy=rc[1])
        th = AsyncThread(parent, items, tr)
        pd = createProgress(u"Обработка", u"Подключаемся", 1, len(items),
            parent=parent)
        pd.canceled.connect(lambda: th.terminate())

        def done(rc):
            if not pd.wasCanceled():
                pd.setValue(pd.value() + 1)
                pd.setLabelText(rc)

        th.task_done.connect(done)
        pd.show()
        th.start()


def main():
    t = Translator()
    rc = t.translate(u"Вышел зайчик погулять.")
    print rc.encode("utf-8")


if __name__ == '__main__':
    main()
