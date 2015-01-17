#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

INTERFACE = "http://www.livejournal.com/interface/xmlrpc"

USERNAME = "user"
PASSWORD = "passwd"

import xmlrpclib
import logging 
import socket
import traceback 
import time
import random

from utils.formlayout import fedit
from utils.qthelpers import flatter
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QThread

log = logging.getLogger(__name__)

class ExportThread(QThread):
    def __init__(self, tree, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
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
    def testConnection(self, rc, parent):
        try:
            user, pass_, timeout, sleep_from, sleep_to = rc #@UnusedVariable
            socket.setdefaulttimeout(timeout)
            conn = xmlrpclib.ServerProxy(INTERFACE)
            params = { "username":user, "password":pass_ }
            rc = conn.LJ.XMLRPC.login(params)
            title = u"Удачно подключились как пользователь: %s" % unicode(rc['fullname'])
            QtGui.QMessageBox.information(parent, u"Связь установлена", title)
        except:
            QtGui.QMessageBox.warning(parent, u"Ошибка",
                u"Ошибка подключения. Проверьте настройки.")
            log.exception("testConnection:")
    
    def config(self):
        datalist = [
            (u"Пользователь:", USERNAME),
            (u"Пароль:", PASSWORD),
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
        conn = xmlrpclib.ServerProxy(INTERFACE)
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
                
            props = {
                "taglist": ", ".join(item.tags),
                "opt_backdated": True
            }
                
            params = { 
                "username": self.user,
                "password": self.pass_,
                "event": item.text,
                "subject": item.title,
                "year": item.date.year,
                "mon": item.date.month,
                "day": item.date.day,
                "hour": item.date.hour,
                "min": item.date.minute,
                "props": props
            }
            
            rc = conn.LJ.XMLRPC.postevent(params)
            log.debug("created: %s", rc['url'])
            
            sleeptime = random.randint(self.sleep_from, self.sleep_to)
            
            if self.pd:
                self.pd.set_text(u"Спим %i минут" % sleeptime)
            time.sleep(sleeptime * 60)

if __name__ == "__main__":    
    import cPickle
    USERNAME = "unit808"
    PASSWORD = "oIxH0HlS21lS1JlR3EhD"
    tree = cPickle.load(open(r"..\autoload.prt", "rb"))
    writer = Export(tree)
    writer.config()
    writer.write()
