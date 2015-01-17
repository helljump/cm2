#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QThread
from pytils.translit import slugify
import xmlrpclib
import logging 
from utils.formlayout import fedit
import socket
import traceback 

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
            url, user, pass_, blog_id, timeout = rc
            socket.setdefaulttimeout(timeout)
            conn = xmlrpclib.ServerProxy( url )
            d1 = conn.wp.getOptions( blog_id, user, pass_, ["blog_title"] )
            title = u"Удачно подключились к блогу:\n" + unicode( d1['blog_title']['value'] )
            QtGui.QMessageBox.information( parent, u"Связь установлена", title )
        except:
            QtGui.QMessageBox.warning( parent, u"Ошибка", 
                u"Ошибка подключения. Проверьте настройки.")
            log.exception("testConnection:")
    
    def config(self):
        datalist = [
            (u"Адрес сайта на WP:","http://wordpress.localhost/xmlrpc.php"),
            (None, u"<font color=green>пример: http://mysite.ru/xmlrpc.php </font>"),
            (u"Пользователь:", "admin"),
            (u"Пароль:", "admin"),
            (u"Id блога(1 по умолчанию):", 1),
            (u"Таймаут:", 60)
        ]
        rc = fedit(datalist, title=u"Параметры экспорта", parent=self.parent, 
            apply=self.testConnection)
        if not rc:
            return False
        self.url, self.user, self.pass_, self.blog_id, self.timeout = rc
        return True

    def addCategory(self, item, parent):
        params = {"name": item.title,
          "slug":slugify( item.title ),
          "parent_id":parent,
          "description":item.text}
        log.debug(u"newCategory %s", item.title)
        if self.pd: self.pd.set_text(u"Добавление категории %s" % item.title)
        cat_id = self.conn.wp.newCategory( self.blog_id, self.user, self.pass_, params )
        return cat_id

    def addPost(self, item, parent):
        params = {"title":item.title,
          "mt_allow_comments":1,
          "mt_allow_pings":1,
          "categories":[parent],
          "mt_keywords":", ".join( item.tags ),
          "dateCreated":item.date,
          "description":item.text,
          "wp_slug":slugify( item.title )}
        log.debug(u"newPost %s", item.title)
        if self.pd: self.pd.set_text(u"Добавление статьи %s" % item.title)
        self.conn.metaWeblog.newPost( self.blog_id, self.user, self.pass_, params, True )

    def articles_count(self, root):
        def _recurse(item):
            egg = 1
            for subitem in item.get_children():
                egg += _recurse(subitem)
            return egg
        return _recurse(root)

    def write(self):
        socket.setdefaulttimeout(self.timeout)
        self.conn = xmlrpclib.ServerProxy( self.url )
        def recurse_tree(tree, parent=0):
            for item in tree.get_children():
                if not parent or item.get_children():
                    cat_id = self.addCategory(item, parent)
                    recurse_tree(item, cat_id)
                else:
                    self.addPost(item, tree.title)
                if self.pd:
                    self.pd.set_value(self.pd.value()+1)
        if self.pd:
            self.pd.set_range(0,self.articles_count(self.tree))
        recurse_tree(self.tree)

if __name__ == "__main__":
    import cPickle
    tree = cPickle.load(open(r"d:\work\promidol\src\edit\autoload.prt","rb"))
    writer = Export(tree)
    writer.config()
    writer.write()
