#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = 'helljump'

import logging

log = logging.getLogger(__name__)

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ab_parser import ABParser, RusParser
import os
import yaml
import codecs
try:
    from utils.formlayout import fedit
    from utils.article import Article
    from plugtypes import IImportPlugin
    import config_dialog
except ImportError:
    IImportPlugin = object
    log.exception('article parser')


class Plugin(IImportPlugin):

    def __init__(self, *args):
        super(Plugin, self).__init__(*args)
        self.configfile = os.path.join(os.path.dirname(__file__), 'config.yml')

    def _save(self, data):
        fout = codecs.open(self.configfile, "wt", "utf-8")
        yaml.dump(data, fout, encoding='UTF-8', default_flow_style=False)
        fout.close()

    def _load(self):
        if os.path.isfile(self.configfile):
            return yaml.load(codecs.open(self.configfile, "r", "UTF-8"))

    def run(self, parent):
        #QMessageBox.warning(parent, u'Внимание', u'Вследствии смены выдачи плагин временно не работает.'\
        #    u' Ведутся работы по восстановлению функциональности.')
        #return

        datalist = [
            [u'Сервис', [
                'Rusarticles',
                (RusParser, 'Rusarticles'),
                (ABParser, 'Articlesbase')]],
            [u'Запрос', u'роботы'],
            [u'Количество', 100],
            [u'Пауза между запросами(с)', 1],
            [u'Пауза между банами(с)', 60],
            [u'Использовать прокси', True],
            [None, u'<em>Что-бы избежать бана, используйте максимально свежие прокси.</em>']
        ]

        egg = self._load()
        if egg and len(egg) == 6:
            for row in datalist[0][1][1:]:
                if row[0] is egg[0]:
                    datalist[0][1][0] = row[1]
                    break
            for i in range(1, len(egg)):
                datalist[i][1] = egg[i]

        rc = fedit(datalist, title=u'Импорт', parent=parent)

        if not rc:
            return

        self._save(rc)
        service, query, amount, sleep, bansleep, useproxy = rc

        proxylist = config_dialog.get_proxy_list() if useproxy else None
        parser = service(parent, proxylist, bansleep)
        c = 0
        for art in parser.get_articles(query):
            parent.add_article.emit(Article(*art))
            c += 1
            if c >= amount:
                break
            if parser.browser.webview is None:
                break
            parser.browser.wait(sleep)
        parser.browser.hide()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    plugin = Plugin()
    plugin.run(None)
