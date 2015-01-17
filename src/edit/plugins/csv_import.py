#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from plugtypes import IImportPlugin
from utils.qthelpers import MyProgressDialog, MyFile, MyString
from PyQt4 import QtGui
import os
from utils.article import Article
from utils.formlayout import fedit
from utils.tidy import autodecode
from StringIO import StringIO
import csv
from functools import partial
from utils.paths import pluginpath
import pickle

log = logging.getLogger(__name__)

dec = lambda x: x.decode("utf-8","replace")

def process(template, values):
    for i in range(0, len(values)):
        template = template.replace("{$%i}" % (i+1), dec(values[i]))
    return template

class CancelException(Exception):
    pass

class Plugin(IImportPlugin):

    fname = os.path.basename(__file__) + ".pkl"
    configfile = os.path.join(pluginpath, fname.encode("mbcs"))

    defaults = [
        "",#0
        u"Автоопределение",#1
        ",",#2
        "\"",#3
        False,#4
        True,#5
        "{$1}",#6
        "{$1}",#7
        u"Параметр:{$2}\nПараметр:{$3}\nПараметр:{$4}"#8
    ]

    ENCODINGS = [
        defaults[1],
        ("auto", u"Автоопределение"),
        ("utf-8", "UTF-8"),
        ("cp1251", "Windows-1251"),
        ("ascii", "ascii")
    ]

    def run(self, parent):

        try:
            Plugin.defaults = pickle.load(open(Plugin.configfile, "rt"))
            log.debug("use plugin params")
        except IOError:
            log.debug("use defaults params")

        if not Plugin.defaults[0]:
            Plugin.defaults[0] = parent.current_load_path+"/"

        #print "[%s]" % Plugin.defaults[0]

        datalist = [
            (u"Файл:", MyFile(Plugin.defaults[0], "Comma Separated Values(*.csv)", "r")),#0
            (u"Кодировка файла", Plugin.ENCODINGS),#1
            (u"Разделитель полей", Plugin.defaults[2]),#2
            (u"Разделитель текста", Plugin.defaults[3]),#3
            (u"Игнорировать первую строку(заголовок)", Plugin.defaults[4]),#4
            (u"Один столбец как заголовок категории", Plugin.defaults[5]),#5
            (u"Шаблон заголовка", Plugin.defaults[6]),#6
            (u"Шаблон меток", Plugin.defaults[7]),#7
            (u"Шаблон материала", MyString(Plugin.defaults[8], 480, 250)),#8
        ]

        for k in Plugin.ENCODINGS[1:]:
            if k[0] == Plugin.ENCODINGS[0]:
                Plugin.ENCODINGS[0] = k[1]
                break
                
        rc = fedit(datalist, title=u"Импорт CSV файла", parent=parent)
        if not rc:
            return
        if not rc[0]:
            return None
            
        pickle.dump(rc, open(Plugin.configfile, "wt"))
            
        parent.current_load_path = os.path.split(unicode(rc[0]))[0]
        pd = MyProgressDialog(u"Импорт CSV", u"Открытие файла", u"Отмена", 0, 0, parent)
        pd.show()
        try:
            pd.set_text(u"Читаем файл")
            data = open(rc[0], "r").read()
            if rc[1]=="auto":
                encoded = autodecode(data, 1024)
            else:
                encoded = data.decode(rc[1], "replace")
            pd.set_text(u"Генерируем статьи")
            tmproot = root = Article()            
            eggfunc = partial(csv.reader, StringIO(encoded.encode("utf-8","replace")))
            if rc[2]:
                eggfunc = partial(eggfunc, delimiter=rc[2].encode("utf-8"))
            if rc[3]:
                eggfunc = partial(eggfunc, quotechar=rc[3].encode("utf-8"))
            for row in eggfunc():
                if rc[4]:
                    rc[4] = False
                    continue
                row = filter(lambda x: len(x)>0, row)
                if rc[5] and len(row)==1:
                    tmproot = Article(dec(row[0]))
                    root.add_child(tmproot)
                    pd.set_text(u"Добавили категорию: %s" % dec(row[0]))
                    log.debug("add category %s", tmproot)
                else:
                    pd.set_text(u"Добавили материал: %s" % dec(row[0]))
                    title = process(rc[6], row)
                    tags = [process(rc[7], row)]
                    text = process(rc[8], row)
                    art = Article(title, text, tags)
                    tmproot.add_child(art)
                QtGui.qApp.processEvents()
                if pd.wasCanceled():
                    raise CancelException
        except CancelException:
            pass
        pd.close()
        return root

if __name__ == '__main__':
    pass
