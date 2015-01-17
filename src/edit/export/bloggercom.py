#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

from time import strftime, sleep
import logging

import socket
import traceback 
import random

from utils.formlayout import fedit
from utils.qthelpers import flatter
from PyQt4 import QtGui
from PyQt4.QtCore import QThread

from gdata import service
import gdata
import atom

log = logging.getLogger(__name__)

class MyBloggerClient:
    
    APPKEY = "Content_Monster-2.0"
    LABEL_SCHEME = "http://www.blogger.com/atom/ns#"

    def __init__(self, username, password):      
        self.service = service.GDataService(username, password)
        self.service.source = self.APPKEY
        self.service.service = "blogger"
        self.service.server = "www.blogger.com"
        self.service.ProgrammaticLogin()       
        feed = self.service.Get("/feeds/default/blogs")
        self_link = feed.entry[0].GetSelfLink()
        if self_link:
            self.blog_id = self_link.href.split("/")[-1]
          
    def CreatePost(self, title, content, labels, date):
        entry = gdata.GDataEntry()
        entry.title = atom.Title(title_type="xhtml", text=title)
        entry.content = atom.Content(content_type="html", text=content)
        entry.published = atom.Published(strftime("%Y-%m-%dT%H:%M:%SZ", date))
        for label in labels:
            entry.category.append(atom.Category(scheme=self.LABEL_SCHEME, term=label))
        return self.service.Post(entry, "/feeds/" + self.blog_id + "/posts/default")
      
class ExportThread(QThread):
    def __init__(self, tree, progressdialog=None, parent=None):
        QThread.__init__(self, parent)
        self.tree = tree
        self.pd = progressdialog
        self.parent = parent        
    def run(self):
        try:
            self.write()
        except:
            log.exception("export error")
            self.error = traceback.format_exc()
    def stop(self):
        log.debug("terminate")
        self.terminate()
        log.debug("wait")
        self.wait()

class Export(ExportThread):    
    """
    >>> import cPickle
    >>> tree = cPickle.load(open("../autoload.prt","rb"))
    >>> writer = Export(tree)
    >>> writer.USERNAME = "unit808@gmail.com"
    >>> writer.PASSWORD = "ypJ30Lk5L8wMB0hn82j4"
    >>> writer.config()
    True
    >>> writer.write()
    """
    
    USERNAME = "username@gmail.com"
    PASSWORD = "password"
    
    def testConnection(self, rc, parent):
        try:
            user, pass_, timeout, sleep_from, sleep_to = rc #@UnusedVariable
            socket.setdefaulttimeout(timeout)
            client = MyBloggerClient(user, pass_) #@UnusedVariable
            title = u"Удачно подключились"
            QtGui.QMessageBox.information(parent, u"Связь установлена", title)
        except Exception:
            QtGui.QMessageBox.warning(parent, u"Ошибка",
                u"Ошибка подключения. Проверьте настройки.")
            log.exception("testConnection:")
    
    def config(self):
        datalist = [
            (u"Пользователь(user@gmail.com):", self.USERNAME),
            (u"Пароль:", self.PASSWORD),
            (u"Таймаут:", 60),
            (None, u"Задержка между публикациями"),
            (u"От(минут)", 5),
            (u"До(минут)", 10)
        ]
        rc = fedit(datalist, title=u"Параметры экспорта", parent=self.parent,
            apply=self.testConnection)
        if not rc:
            return False
        self.user, self.pass_, self.timeout, self.sleep_from, self.sleep_to = rc
        return True
        
    def write(self):
        socket.setdefaulttimeout(self.timeout)
        client = MyBloggerClient(self.user, self.pass_)
        
        flatlist = flatter(self.tree)
        
        log.debug("articles count: %i", len(flatlist))
        
        if self.pd:
            self.pd.set_range(0, len(flatlist))
        cnt = 0
        
        for item in flatlist:
            cnt += 1
            
            if self.pd:
                self.pd.set_value(cnt)
                self.pd.set_text(item.title)

            rc = client.CreatePost(item.title, item.text, item.tags, item.date.timetuple()) #@UnusedVariable
            log.debug("published %i", cnt)
    
            sleeptime = random.randint(self.sleep_from, self.sleep_to)            
            if self.pd:
                self.pd.set_text(u"Спим %i минут" % sleeptime)
            sleep(sleeptime * 60)
      
def main():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    main()
