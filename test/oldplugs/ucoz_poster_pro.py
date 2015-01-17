#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
try:
    from plugtypes import IExportPlugin  # @UnresolvedImport
except ImportError:
    IExportPlugin = object
from PyQt4 import QtGui, QtCore
import os
import pickle
import time
import traceback
from utils.qthelpers import MyProgressDialog
from engine.browser import Browser, FormMethod
from utils.paths import pluginpath
from utils.formlayout import fedit

log = logging.getLogger(__name__)

fname = os.path.basename(__file__) + ".pkl"
configfile = os.path.join(pluginpath, fname.encode("mbcs"))

try:
    settings = pickle.load(open(configfile, "rt"))
except IOError:
    settings = {"user": "ad@min.ru",
                "pass": "admin",
                "url": "http://admin.ucoz.ru/",
                "cat_id": 1}


def articles_count(root):
    def _recurse(item):
        egg = 1
        for subitem in item.get_children():
            egg += _recurse(subitem)
        return egg
    return _recurse(root)


class PosterException(Exception):
    pass


class UcozPoster(object):
    def __init__(self, timeout):
        self.br = Browser(proxy={}, timeout=timeout)

    def login(self, url, user, pass_):
        self.url = url
        self.br.open(url)
        self.br.set_param("user", user)
        self.br.set_param("password", pass_)
        self.br.set_param("sbc", u"Вход")
        self.br.method = FormMethod.POST
        self.br.open(url + "index/sub/")
        rc = unicode(self.br.find_tag("cmd", "p", "innerHTML"))
        if rc.find(u"Неправильный логин или пароль") != -1:
            raise PosterException("Wrong LogIn")
        elif rc.find(u"IP адрес временно заблокирован") != -1:
            raise PosterException("IP blocked")

    def post(self, cat_id, title, text, tagsstring):
        self.br.open(self.url + "news/0-0-0-0-1")
        self.br.select_form(1)
        self.br.set_param("cat", str(cat_id))
        self.br.set_param("title", title)
        self.br.set_param("message", text)
        self.br.set_param("tags", tagsstring)
        self.br.set_param("sbm", u"Добавить")
        self.br.open(self.url + "news/")
        #self.br.dump()
        rc = unicode(self.br.find_tag("cmd", "p", "content"))
        if rc.find(u"Материал успешно добавлен") == -1:
            raise PosterException("Not added")


comment = u"""Публикация новостей возможна только при наличии на вашем сайте<br/>
страницы /news/0-0-0-0-1."""


class Export(IExportPlugin):
    def run(self, tree, parent):
        datalist = [(u"Пользователь(email):", settings['user']),
                    (u"Пароль:", settings['pass']),
                    (u"Адрес сайта(http://test.ucoz.ru/):", settings['url']),
                    (u"ID Категории:", settings['cat_id']),
                    (u"Задержка между публикациями(с)", settings.get('sleep', 60))
                    ]
        rc = fedit(datalist, title=u"Экспорт UCOZ", parent=parent, comment=comment)
        if not rc:
            return
        settings["user"], settings["pass"], settings["url"], settings["cat_id"], settings["sleep"] = rc
        pickle.dump(settings, open(configfile, "wt"))

        pd = MyProgressDialog(u"Экспорт UCOZ", u"Подключение к серверу", u"Отмена",
                              0, 0, parent)
        pd.setFixedWidth(320)
        pd.show()
        th = ExportThread(tree, parent, rc, pd, parent.connect_timeout)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                th.terminate()
                break
            time.sleep(0.0123)
            QtGui.qApp.processEvents()
        pd.close()
        if th.error:
            parent.errmsg.setWindowTitle(u"Ошибка экспорта")
            parent.errmsg.showMessage(th.error)
        return th.result


class CancelException(Exception):
    pass


class ExportThread(QtCore.QThread):
    def __init__(self, tree, parent, params, progressdialog, timeout=30):
        super(ExportThread, self).__init__(parent)
        self.error = self.result = None
        self.params = params
        self.pd = progressdialog
        self.tree = tree
        self.timeout = timeout

    def run(self):
        try:
            (user, pass_, url, cat_id, self.pause) = self.params
            print self.pause
            self.poster = UcozPoster(self.timeout)
            self.poster.login(url, user, pass_)
            self.pd.set_text(u"Публикация статей")
            self.pd.set_range(0, articles_count(self.tree))
            self.export(cat_id)
        except:
            self.error = traceback.format_exc()

    def export(self, cat_id):
        def recurse_tree(tree):
            for item in tree.get_children():
                if self.pd.wasCanceled():
                    raise CancelException
                self.poster.post(cat_id, item.title, item.text, ", ".join(item.tags))
                time.sleep(self.pause)
                recurse_tree(item)
                self.pd.set_text(item.title)
                self.pd.inc_value()
        recurse_tree(self.tree)

if __name__ == '__main__':
    pass
