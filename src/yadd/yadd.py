#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QLocale, Qt, QThread
from aboutdialog import AboutDialog
from djenahdialog import DjenahDialog
from engine import anticaptcha 
from linkdialog import LinkDialog
from proxy.checker.proxyform import MainDialog as ProxyMainDialog 
import Queue
from rc import rc #@UnusedImport
from rss.rss import RSSDialog
from scripts.addurl import Code, AddUrlResult
from scripts.addurl.yandex import addurl
from settingsdialog import SettingsDialog
from utils.qthelpers import ToolBarWithPopup, MyProgressDialog
from utils.translator import Translator
from logging import debug, exception, error
import random
import shelve
import sys
from engine.browser import Browser, BrowserError
from urlparse import urlparse
from statisticsdialog import Statistic_Dialog
import time

class TooManyObloms(Exception): pass

class ReadSitemapThread(QThread):

    def __init__(self, url, parent):
        QtCore.QThread.__init__(self, parent)
        self.url = url
        self.exc = None
        self.links = []

    def run(self):
        br = Browser()
        try:
            soup = br.open(self.url)
            for loc in soup.findAll("loc"):
                self.links.append("".join(loc.contents))
        except BrowserError, err:
            self.exc = err

class AddUrlThread(QThread):
    def __init__(self, task_queue, done_queue, pipe, pipeimg, userkey, timeout, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.task_queue = task_queue
        self.done_queue = done_queue
        self.pipe = pipe
        self.pipeimg = pipeimg
        self.userkey = userkey
        self.timeout = timeout
        self.online = True
        self.connect(self, QtCore.SIGNAL("stop_addurl()"), self.stop)
        
    def run(self):
        for task in iter(self.task_queue.get, 'STOP'):
            try:
                if not self.online:
                    break
                rc = addurl(task.link, task.proxy, self.pipe, self.pipeimg, self.userkey, self.timeout)
                rc.task = task
                self.done_queue.put(rc)
            except BrowserError:
                rc = AddUrlResult(Code.NOTADDED)
                rc.task = task
                self.done_queue.put(rc)
                error("BrowserError [%s]", task.link)
            except Exception, err:
                rc = AddUrlResult(Code.NOTADDED)
                rc.task = task
                self.done_queue.put(rc)
                exception("*** Unhandled error [%s] ***", err)
            time.sleep(random.random())
        debug("thread done")
        
    def stop(self): 
        debug("signal stop emitted")
        self.online = False
                
class Grunkreuz(object):
    def __init__(self, url, **args):
        self.url = url
        self.use_djenah = args.get("use_djenah", False)
        self.done = args.get("done", 0)
        self.keywords = None
        self.desc = None

class YaddTask(object):
    def __init__(self, project, link, proxy, djlink=None):
        self.project = project
        self.link = link
        self.proxy = proxy
        self.djlink = djlink

class BlapBanner(QtGui.QLabel):
    def __init__(self, parent):
        super(BlapBanner, self).__init__(parent)        
        movie = QtGui.QMovie(":/banner/banner.gif",QtCore.QByteArray(), self)
        movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.setMovie(movie)
        movie.start()
        self.setStyleSheet("background-color: rgb(255,255,255);")
        self.setFrameStyle(QtGui.QFrame.StyledPanel)
    def mouseReleaseEvent(self, event):
        debug("open blap")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://blap.ru"))

class ProjectModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(ProjectModel, self).__init__(parent)
        self.labels = [ self.tr("Url"), self.tr("Use Djenah"), self.tr("Done") ]
        cfg = shelve.open("projects.cfg")
        self.projects = cfg.get("projects", [])
        cfg.close()
        self.done_icon = QtGui.QIcon(":/yadd/done.png")

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.projects)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.labels)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self.projects[index.row()]
        col = index.column()

        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                v = item.url
                return v
            elif col == 2:
                return item.done
                
        elif role == QtCore.Qt.CheckStateRole:
            if col == 1:
                return item.use_djenah

        '''
        if role == QtCore.Qt.DecorationRole:
            if col==1 and item.use_djenah:
                return self.done_icon            
            if col==2 and item.done:
                return self.done_icon            
        '''

        return QtCore.QVariant()
            
    """
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        row = index.row()
        col = index.column()
        
        if row < 0 or row >= len(self.projects):
            return False
        if col < 0 or col >= len(self.labels):
            return False

        if col==0:
            self.projects[row].url = value
        elif col==1:
            self.projects[row].use_djenah = value
        elif col==2:
            self.projects[row].done = value
        elif col==3:
            self.projects[row].keywords = value
        elif col==4:
            self.projects[row].desc = value
        
        self.dataChanged.emit(index, index)
    """
        
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.labels[section])
        return QtCore.QVariant()
        
    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        #logging.debug("removeRows %i -> %i" % (position, rows))
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        for i in range(rows): #@UnusedVariable
            del self.projects[position]
        self.endRemoveRows()
        return True

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows): #@UnusedVariable
            self.projects.insert(position, Grunkreuz("http://"))
        self.endInsertRows()
        return True
        
    def save_projects(self):
        cfg = shelve.open("projects.cfg")
        cfg['projects'] = self.projects
        cfg.close()

    def set_djenahed(self, row, state):
        self.projects[row].use_djenah = state
        self.refreshPos(row)
        
    def refreshPos(self, pos):
        self.dataChanged.emit(self.index(pos, 0), self.index(pos, len(self.labels)))
                
class MainWindow(QtGui.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(self.tr("promidol :: yadd"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(800, 600)
        layout = QtGui.QVBoxLayout(self)
        
        toolbar = ToolBarWithPopup(self)
        toolbar.addAction(QtGui.QIcon(":/yadd/run.png"), self.tr("Run"), self.poisoned)
        #toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.poolsize_sb = QtGui.QSpinBox(self)
        self.poolsize_sb.setRange(1, 99)
        self.poolsize_sb.setSuffix(self.tr(" thread(s)"))
        toolbar.addWidget(self.poolsize_sb)
        toolbar.addSeparator()
        toolbar.addAction(QtGui.QIcon(":/yadd/add.png"), self.tr("Add"), self._add_project)
        toolbar.addAction(QtGui.QIcon(":/yadd/remove.png"), self.tr("Remove"), self._remove_project)

        #add popup button
        menu = QtGui.QMenu(self)
        menu.addAction(QtGui.QIcon(":/yadd/fileimport.png"), self.tr("from file"), self._import_links)
        menu.addAction(QtGui.QIcon(":/yadd/sitemap.png"), self.tr("from sitemap"), self._import_sitemap)
        tb1 = QtGui.QToolButton(self)
        tb1.setIcon(QtGui.QIcon(":/yadd/import.png"))
        tb1.setText(self.tr("Import"))
        tb1.setMenu(menu)
        tb1.setPopupMode(QtGui.QToolButton.InstantPopup)
        tb1.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        toolbar.toolButtonStyleChanged.connect(tb1.setToolButtonStyle) 
        toolbar.addWidget(tb1)
        
        toolbar.addSeparator()
        toolbar.addAction(QtGui.QIcon(":/yadd/djenah.png"), self.tr("Djenah's"), self._djenahs)
        toolbar.addAction(QtGui.QIcon(":/yadd/proxy.png"), self.tr("Proxy"), self._proxycheck)
        toolbar.addSeparator()
        toolbar.addAction(QtGui.QIcon(":/yadd/configure.png"), self.tr("Settings"), self._settings)
        toolbar.addSeparator()
        toolbar.addAction(QtGui.QIcon(":/yadd/about.png"), self.tr("About"), self._about)
        toolbar.addAction(QtGui.QIcon(":/yadd/rss.png"), self.tr("RSS"), self._viewrss)
        #toolbar.addAction(QtGui.QIcon(":/yadd/rss.png"), self.tr("RSS"), self._test)
        
        #toolbar.setContextMenuPolicy(Qt.CustomContextMenu)
        #toolbar.customContextMenuRequested.connect(lambda p, t=toolbar: self._show_toolbar_menu(p, t))
        self.toolbar = toolbar # таки пришлось :)

        layout.addWidget(toolbar)
        
        model = ProjectModel(self)
        self.view = QtGui.QTableView(self)        
        self.view.setModel(model)

        self.view.verticalHeader().hide()
        self.view.verticalHeader().setDefaultSectionSize(20)
        self.view.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        #self.view.resizeColumnsToContents()
        #self.view.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        #self.view.horizontalHeader().setStretchLastSection(False)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        layout.addWidget(self.view)

        movie_label = BlapBanner(self)

        layout.addWidget(movie_label)

        self.view.doubleClicked.connect(self._doubleClicked)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self._show_popup)

        self._load_config()
                
    def _import_sitemap(self):
        #импорт сайтмап с тырнета
        url, rc = QtGui.QInputDialog.getText(self, self.tr("Import sitemap"),
                                             self.tr("Enter url (http://lipf.ru/sitemap.xml):"),
                                             text="http://")
                                            #text="http://lipf.ru/sitemap.xml")
                                            #text="http://az.lib.ru/editors/g/gogolx_n_w/text_0020.shtml")
        if not rc:
            return

        parsed = urlparse(str(url))
        if not parsed.netloc:
            return
            
        url = str(url)
        
        pd = MyProgressDialog(self.tr("Read url"), self.tr("Read %s" % url), self.tr("Cancel"), 0, 0, self)
        pd.show()
        
        #q = Queue.Queue()
        #task = Thread(target=self._read_sitemap, args=(url, q))
        task = ReadSitemapThread(url, pd)
        task.start()
        
        while task.isRunning():
            if pd.wasCanceled():
                debug("sitemap task terminate...")
                task.terminate()
                debug("sitemap task terminated")
                break
            QtGui.qApp.processEvents()
            time.sleep(0.01)
        else:
            links = task.links
            if not links:
                debug("add sitemap links")
                pd.close()
                QtGui.QMessageBox.critical(self, self.tr("Read sitemap"), self.tr("Sitemap read error"))
                return

            pd.setRange(0, len(links) - 1)
            while links:
                link = links.pop(0)
                m = self.view.model()        
                pos = m.rowCount()
                m.insertRow(pos)
                item = m.projects[pos]
                item.url = unicode(link) 
                item.use_djenah = False
                item.done = 0
                item.keywords = u""
                item.desc = u""
                m.refreshPos(pos)
                pd.setValue(pd.value() + 1)

                if pd.wasCanceled():
                    break
                QtGui.qApp.processEvents()
        
        debug("sitemap task done")
        pd.close()
                
    def _show_toolbar_menu(self, p, t):
        menu = QtGui.QMenu(self)
        menu.addAction(self.tr("Only icons"),
                       lambda : t.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly))
        menu.addAction(self.tr("Text beside icon"),
                       lambda : t.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon))
        menu.addAction(self.tr("Text under icon"),
                       lambda : t.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon))
        menu.exec_(QtGui.QCursor.pos())
        
    def _show_popup(self, point):
        menu = QtGui.QMenu(self)
        menu.addAction(self.tr("Djenahing"),
                       lambda v=True: self._set_link_djenahed(v)).setIcon(QtGui.QIcon(":/yadd/djenah.png"))
        menu.addAction(self.tr("Undjenahing"),
                       lambda v=False: self._set_link_djenahed(v)).setIcon(QtGui.QIcon(":/yadd/undjenah.png"))
        menu.exec_(QtGui.QCursor.pos())
        
    def _set_link_djenahed(self, state):
        selectionModel = self.view.selectionModel()
        indexes = selectionModel.selectedRows()
        for index in indexes:
            self.view.model().set_djenahed(index.row(), state)
        
        #index = self.view.indexAt(point)
        #logging.debug("index popup %i" % index.row())
        #if not index.isValid(): 
        #    return
        
    def _import_links(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Import links"), ".",
            "links (*.txt)")
        if fileName:
            debug("import from %s" % fileName)
            for link in open(fileName).readlines():
                m = self.view.model()        
                pos = m.rowCount()
                m.insertRow(pos)
                item = m.projects[pos]
                item.url = unicode(link) 
                item.use_djenah = False
                item.done = 0
                item.keywords = u""
                item.desc = u""
                m.refreshPos(pos)
        
    def _settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()
        
    def _djenahs(self):
        dlg = DjenahDialog(self)
        dlg.exec_()
                
    def _load_config(self):
        cfg = shelve.open("yadd.cfg")
        poolsize = cfg.get("yadd.poolsize", 10)
        tbstyle = cfg.get("yadd.toolbarstyle", QtCore.Qt.ToolButtonTextBesideIcon)
        cfg.close()
        self.poolsize_sb.setValue(poolsize)
        self.toolbar.setToolButtonStyle(tbstyle)
        self.toolbar.emit(QtCore.SIGNAL("toolButtonStyleChanged  (Qt::ToolButtonStyle)"), tbstyle)

    def _castrating_link(self, link):
        link = link.replace("http://www.", "")
        link = link.replace("http://", "")
        return link
        
    def _disinfecting(self, task_queue, threads, pd):
        debug("terminate threads")
        for pr in threads:
            if pr.isRunning():
                pr.wait(100)
                pr.terminate()
                pr.wait()
        debug("clear queue")
        try:
            while 1:
                task_queue.get_nowait()
        except Queue.Empty:
            pass
        debug("close queue")
        debug("pd close")
        pd.close()

    def poisoned(self):

        cfg = shelve.open("yadd.cfg")
        agkey = cfg.get("yadd.antigate_key", "")
        timeout = cfg.get("yadd.connection_timeout", 30)
        stoperrors = cfg.get("yadd.stop_after_errors", 99)
        djlinks = cfg.get("yadd.djenah_links", [])
        cfg.close()
        
        cfg = shelve.open("proxy.cfg")
        proxylist = cfg.get("proxy.checker.proxylist", [])
        cfg.close()
        
        poolsize = self.poolsize_sb.value()
        
        userkey = agkey.strip()
        
        if userkey == "":
            if QtGui.QMessageBox.question(self, self.tr("No antigate key"),
                              self.tr("You don't enter antigate key.\nWork in single thread.\nContinue?"),
                              buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return
            poolsize = 1
        
        debug("put all tasks in task_queue")
        
        task_queue = Queue.Queue()
        done_queue = Queue.Queue()
        
        pipeimg = Queue.Queue()
        
        links_amount = 0
        prjs = self.view.model().projects

        # создали очередь заданий
        for i in range(len(prjs)):
            prj = prjs[i]
            random_proxy = {"http":random.choice(proxylist)[0]} if proxylist else {}
            wp = YaddTask(i, prj.url, random_proxy)
            task_queue.put(wp)
            links_amount += 1        
            if prj.use_djenah:
                for djlink in djlinks:
                    djurl = djlink.replace("[SITEURL]", self._castrating_link(prj.url))
                    random_proxy = {"http":random.choice(proxylist)[0]} if proxylist else {}
                    wp = YaddTask(i, djurl, random_proxy, djlink)
                    task_queue.put(wp)
                    links_amount += 1        
        debug("total tasks [%i]" % links_amount)

        queues = []
        threads = []

        debug("create threads [%i]" % poolsize)
        
        # создали пул процессов
        for i in range(poolsize): #@UnusedVariable
            pipe = Queue.Queue()
            queues.append(pipe)
            pr = AddUrlThread(task_queue, done_queue, pipe, pipeimg, userkey, timeout, self)
            threads.append(pr)
            pr.start()
            
        debug("all threads run")

        pd = QtGui.QProgressDialog(self)
        pd.setModal(True)
        pd.setWindowTitle(self.tr("Add urls"))
        pd.setRange(0, links_amount)
        pd.setValue(0)
        pd.setLabelText(self.tr("Run"))
        pd.setFixedWidth(480)
        pd.forceShow()

        done_tasks = 0
        
        # понеслось
        errors = 0
        results = {}
        
        try:
        
            while done_tasks < links_amount:
                
                for pipe in queues: # проверим очереди
                    try:                        
                        data = pipeimg.get_nowait()
                        debug("getting image")
                        if data[0] == anticaptcha.Command.IMAGE:
                            debug("------------> get image command")
                            dlg = anticaptcha.AntiCaptcha_Dialog(data[1], self)
                            if dlg.exec_():
                                debug("send text")
                                pipe.put((anticaptcha.Command.TEXT, dlg.get_text()))
                            else:
                                debug("send stop")
                                pipe.put((anticaptcha.Command.STOP,))
                                pd.cancel()
                    except Queue.Empty:
                        pass
                                
                try:
                    rc = done_queue.get_nowait()
                    done_tasks += 1
                    pd.setValue(done_tasks)
                    
                    if not results.has_key(rc.code):
                        results[rc.code] = []
                    
                    if rc.code == Code.WRONGCAPTCHA:
                        results[rc.code].append(rc.cap_id)
                    else:
                        results[rc.code].append(rc.task.djlink or rc.task.link)
                    
                    if rc.code == Code.DONE:
                        prj = prjs[rc.task.project]
                        prj.done += 1
                        self.view.model().refreshPos(rc.task.project)
                        pd.setLabelText(self.tr("added:") + rc.task.link)
                                                                        
                    elif rc.code == Code.ALREADYININDEX:
                        pd.setLabelText(self.tr("already in index:") + rc.task.link)
                        
                    elif rc.code == Code.WRONGCAPTCHA:
                        pd.setLabelText(self.tr("wrong captcha:") + rc.task.link)                        
                        
                    elif rc.code == Code.NOTADDED:
                        errors += 1
                        pd.setLabelText(self.tr("not added:") + rc.task.link)
                        
                    elif rc.code == Code.BANNED:
                        errors += 1
                        pd.setLabelText(self.tr("banned:") + rc.task.link)
                        
                    obloms = 1.0 * errors / links_amount * 100  
                    if obloms > stoperrors:
                        raise TooManyObloms()
                        
                except Queue.Empty:
                    pass
                if pd.wasCanceled():
                    for th in threads:
                        th.emit(QtCore.SIGNAL("stop_proxytests()"))
                    break
                QtGui.qApp.processEvents()
                time.sleep(0.01)
            
        except TooManyObloms:
            pr = self._disinfecting(task_queue, threads, pd)
            QtGui.QMessageBox.critical(self, self.tr("Stop thread"),
                                       self.tr("Too many errors.\nSee settings 'Stop after' parameter."))
        else:
            pr = self._disinfecting(task_queue, threads, pd)
        
        debug("yandex was poisoned")

        #debug("%s", results)
        #import pickle
        #pickle.dump(results, open("results.log","wb"), pickle.HIGHEST_PROTOCOL)

        dlg = Statistic_Dialog(self, results, self.view.model())
        dlg.exec_()

    def _viewrss(self):
        dlg = RSSDialog(self)
        dlg.exec_()

    def _proxycheck(self):
        dlg = ProxyMainDialog(self)
        dlg.resize(640, 480)
        dlg.exec_()

    def _about(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    def _add_project(self):
        
        ld = LinkDialog("http://", usedjenah=True, parent=self)
        if not ld.exec_():
            return

        m = self.view.model()

        pos = m.rowCount()
        m.insertRow(pos)
        item = m.projects[pos]
        item.url = unicode(ld.url_le.text()) 
        item.use_djenah = ld.usedjenah_cb.isChecked()
        item.done = 0
        item.keywords = unicode(ld.keywords_le.text())
        item.desc = unicode(ld.desc_le.text())
        m.refreshPos(pos)

    def _remove_project(self):        
        selectionModel = self.view.selectionModel()
        indexes = selectionModel.selectedRows()
        indexes.sort(cmp=lambda x, y: cmp(x.row(), y.row()), reverse=True)
        for index in indexes:
            row = index.row()
            #logging.debug("let's remove %i -> %i" % (row,1))
            self.view.model().removeRow(row)

    def _doubleClicked(self, index):
        row = index.row()
        #logging.debug("clicked %i" % row)
        item = self.view.model().projects[row]
        
        ld = LinkDialog(item.url, usedjenah=item.use_djenah, keys=item.keywords,
            desc=item.desc, parent=self)
        if not ld.exec_():
            return

        item.url = unicode(ld.url_le.text()) 
        item.use_djenah = ld.usedjenah_cb.isChecked()
        #item.done = False
        item.keywords = unicode(ld.keywords_le.text())
        item.desc = unicode(ld.desc_le.text())
        self.view.model().refreshPos(row)
        
        #logging.debug("url %s" % item.url)
        
    def closeEvent(self, event):
        poolsize = self.poolsize_sb.value()
        cfg = shelve.open("yadd.cfg")
        cfg["yadd.poolsize"] = poolsize
        cfg["yadd.toolbarstyle"] = self.toolbar.toolButtonStyle()
        cfg.close()
        self.view.model().save_projects()
        event.accept()

def main():
    MainWindow().exec_()

if __name__ == '__main__':    
    reload(sys)
    if hasattr(sys, "setdefaultencoding"): sys.setdefaultencoding("utf-8")
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(':/yadd/yadd.png'))
    tr = Translator(None, 'yadd_%s.qm' % QLocale.system().name())
    app.installTranslator(tr)
    try:
        rc = main()
    except:
        exception("Unhandled exception")
    sys.exit(rc)
