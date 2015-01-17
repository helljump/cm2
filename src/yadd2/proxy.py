#! /usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import os
import logging.config

cfg = "logging.conf"
if os.path.isfile(cfg):
    logging.config.fileConfig(cfg)

log = logging.getLogger(__name__)

import sys
sys.path.append(r"d:\work\cm2\src")

import pickle
import re
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
from itertools import cycle
from scripts import searchengine
from Queue import Queue
import operator
import icons #@UnusedImport
from engine.browser import Browser, BrowserError
import urllib2
import time
import socket
import chardet

USERHOME = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
HOMEPATH = os.path.join(unicode(USERHOME), "yadd2").encode("mbcs")
if not os.path.isdir(HOMEPATH):
    os.mkdir(HOMEPATH)

TIMEOUT = 10
searchengine.TIMEOUT = 60

class ToolBar(QToolBar):
    def __init__(self, parent, style=Qt.ToolButtonTextBesideIcon, *args):
        QWidget.__init__(self, parent, *args)
        self.setToolButtonStyle(style)
        self.setIconSize(QSize(32, 32))

class ProgressDialog(QProgressDialog):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setWindowModality(Qt.WindowModal)
        self.setFixedWidth(320)
        self.connect(self, SIGNAL("setValue(int)"), self, SLOT("setValue(int)"))
        self.connect(self, SIGNAL("setText(QString)"), self, SLOT("setLabelText(QString)"))
        self.connect(self, SIGNAL("incValue()"), self.inc_value)
    def inc_value(self):
        self.setValue(self.value() + 1)

class SEParserThread(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent
    def run(self):
        log.debug("start thread")
        try:
            self.parse()
            self.parent.emit(SIGNAL("closeProgress()"))
        except StopIteration:
            pass
        except Exception, err:
            self.parent.emit(SIGNAL("showError(QString)"), str(err))
        log.debug("end thread")
    def parse(self):
        i = 1
        se = []
        q = unicode(self.parent.query_le.text())
        if self.parent.googleru_cb.isChecked():
            se.append(searchengine.GoogleRu().search(q))
        if self.parent.google_cb.isChecked():
            se.append(searchengine.GoogleCom().search(q))
        if self.parent.yandex_cb.isChecked():
            se.append(searchengine.YandexRu().search(q))
        amount = self.parent.amount_sb.value()
        se = cycle(se)
        while True:
            nextse = se.next()
            link = nextse.next()
            self.parent.pd.emit(SIGNAL("setValue(int)"), i)
            self.parent.pd.emit(SIGNAL("setText(QString)"), link)
            self.parent.emit(SIGNAL("appendUrl(QString)"), link)
            i += 1
            if i > amount:
                break

class SimpleListModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self)
        self.parent = parent
        self.labels = [u"Найденые страницы"]
        self.data = []
    def rowCount(self, parent):
        return len(self.data)
    def columnCount(self, parent):
        return len(self.labels)
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()
        value = ''
        if role == Qt.DisplayRole:
            row = index.row()
            value = self.data[row]
        if role == Qt.EditRole:
            row = index.row()
            value = self.data[row]
        return QVariant(value)
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section + 1)
        return QVariant()
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
    def setData(self, index, data, role):
        try:
            row = index.row()
            self.data[row] = unicode(data.toString())
            return True
        except:
            return False
    def sort(self, col, order):
        reverse = order != Qt.AscendingOrder
        self.data.sort(reverse=reverse)
        ifrom = self.createIndex(0, 0)
        ito = self.createIndex(self.rowCount(None), self.columnCount(None))
        self.dataChanged.emit(ifrom, ito)
    def insertRows(self, pos, rows, index=QModelIndex()):
        self.beginInsertRows(index, pos, pos + rows - 1)
        for row in range(rows): #@UnusedVariable
            self.data.insert(pos, "")
        self.endInsertRows()
        return True
    def removeRows(self, pos, rows, index=QModelIndex()):
        self.beginRemoveRows(index, pos, pos + rows - 1);
        for i in range(rows): #@UnusedVariable
            self.data.pop(pos)
        self.endRemoveRows()
        return True

class SEParserDialog(QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle(u"Парсер выдачи")
        self.resize(700, 700 * 0.75)
        layout = QGridLayout(self)
        tb = ToolBar(self)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/cog_go.png"),
            u"&Выполнить", self.run)
        layout.addWidget(tb, 0, 0, 1, 2)
        self.query_le = QLineEdit(self)
        self.query_le.setText("free proxy list")
        layout.addWidget(QLabel(u"Запрос"), 1, 0, 1, 1)
        layout.addWidget(self.query_le, 1, 1, 1, 1)
        self.amount_sb = QSpinBox(self)
        self.amount_sb.setMaximumWidth(80)
        self.amount_sb.setRange(0, 1000)
        self.amount_sb.setValue(100)
        layout.addWidget(QLabel(u"Количество ccылок"), 2, 0, 1, 1)
        layout.addWidget(self.amount_sb, 2, 1, 1, 1)
        egg = QHBoxLayout()
        self.google_cb = QCheckBox("Google.com", self)
        self.google_cb.setChecked(True)
        egg.addWidget(self.google_cb)
        self.googleru_cb = QCheckBox("Google.ru", self)
        self.googleru_cb.setChecked(True)
        egg.addWidget(self.googleru_cb)
        self.yandex_cb = QCheckBox("Yandex.ru", self)
        self.yandex_cb.setChecked(True)
        egg.addWidget(self.yandex_cb)
        egg.addStretch(1)
        layout.addWidget(QLabel(u"Поисковые системы"), 3, 0, 1, 1)
        layout.addLayout(egg, 3, 1, 1, 1)
        self.table = QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(
            self.table.verticalHeader().fontMetrics().height() + 4)
        model = SimpleListModel(self.table)
        self.table.setModel(model)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.connect(self, SIGNAL("appendUrl(QString)"), self.appendRow)
        layout.addWidget(self.table, 4, 0, 1, 2)        
        bbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close, Qt.Horizontal, self)
        layout.addWidget(bbox, 5, 0, 1, 2)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)        
        self.errmsg = QErrorMessage(self)
        self.errmsg.setModal(True)
        self.connect(self, SIGNAL("showError(QString)"), self.show_error)
        self.pd = ProgressDialog(self)
        self.connect(self, SIGNAL("closeProgress()"), self.pd, SLOT("hide()"))
    def appendRow(self, url):
        model = self.table.model()
        row = model.rowCount(None)
        model.insertRows(row, 1)
        index = model.createIndex(row, 0)
        model.setData(index, QVariant(url), Qt.DisplayRole)
    def show_error(self, err):
        self.pd.hide()
        self.errmsg.setWindowTitle(u"Ошибка")
        self.errmsg.showMessage(err)
    def run(self):
        self.pd.setWindowTitle(u"Получение результатов запроса")
        self.pd.setRange(0, self.amount_sb.value())
        self.pd.setValue(0)
        th = SEParserThread(self)
        th.start()
        self.pd.exec_()
        if self.pd.wasCanceled():
            th.wait(100)
            th.terminate()
    def get_links(self):
        return self.table.model().data

class PagesParserThread(QThread):
    ADDRESS = re.compile("((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\w\-]{2,20}\.\w{2,4})\:(\d{2,6}))")
    def __init__(self, queue, parent):
        QThread.__init__(self, parent)
        self.parent = parent
        self.queue = queue
    def run(self):
        log.debug("start thread")
        for page in iter(self.queue.get, "STOP"):
            try:
                br = Browser(timeout=TIMEOUT)
                br.open(page)
                for item in self.ADDRESS.finditer(br.source):
                    address = str(item.groups(0)[0])
                    self.parent.emit(SIGNAL("appendAddress(QString)"), address)
                    self.parent.pd.emit(SIGNAL("setText(QString)"), address)
            except BrowserError, err:
                log.error("%s", err)
                self.parent.pd.emit(SIGNAL("setText(QString)"), str(err))
            self.parent.pd.emit(SIGNAL("incValue()"))
        #self.parent.emit(SIGNAL("closeProgress()"))
        log.debug("end thread")
            
class PagesParserDialog(QDialog):
    PAGES = os.path.join(HOMEPATH, "pages.pkl")
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle(u"Парсер страниц")
        self.resize(800, 800 * 0.75)
        layout = QGridLayout(self)
        tb = ToolBar(self)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/cog_go.png"),
            u"&Запуск", self.run)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/google.png"),
            u"&Парсер выдачи", self.parse_se)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/filter.png"),
            u"&Удалить повторы", self.clear)
        layout.addWidget(tb, 0, 0, 1, 2)
        l1 = QHBoxLayout()
        l1.addWidget(QLabel(u"Потоков"))
        self.threads_se = QSpinBox(self)
        self.threads_se.setValue(3)
        l1.addWidget(self.threads_se)
        l1.addStretch(1)
        layout.addLayout(l1, 1, 0, 1, 2)
        self.pages_table = QTableView(self)
        self.pages_table.setSortingEnabled(True)
        self.pages_table.verticalHeader().setDefaultSectionSize(
            self.pages_table.verticalHeader().fontMetrics().height() + 4)
        model = SimpleListModel(self.pages_table)
        model.labels = [u"Страницы"]
        self.pages_table.setModel(model)
        self.pages_table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.pages_table, 2, 0)
        tb = ToolBar(self, style=Qt.ToolButtonIconOnly)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/add.png"),
            u"&Добавить", lambda t=self.pages_table: self.insert_row(t))
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/delete.png"),
            u"&Удалить", lambda t=self.pages_table: self.remove_row(t))
        layout.addWidget(tb, 3, 0, 1, 1)
        self.address_table = QTableView(self)
        self.address_table.setSortingEnabled(True)
        self.address_table.verticalHeader().setDefaultSectionSize(
            self.address_table.verticalHeader().fontMetrics().height() + 4)
        model = SimpleListModel(self.address_table)
        model.labels = [u"Адреса"]
        self.address_table.setModel(model)
        self.address_table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.address_table, 2, 1)
        tb = ToolBar(self, style=Qt.ToolButtonIconOnly)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/add.png"),
            u"&Добавить", lambda t=self.address_table: self.insert_row(t))
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/delete.png"),
            u"&Удалить", lambda t=self.address_table: self.remove_row(t))
        layout.addWidget(tb, 3, 1, 1, 1)
        bbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close, Qt.Horizontal, self)
        layout.addWidget(bbox, 4, 0, 1, 2)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        self.errmsg = QErrorMessage(self)
        self.errmsg.setModal(True)
        self.connect(self, SIGNAL("showError(QString)"), self.show_error)
        self.connect(self, SIGNAL("appendAddress(QString)"), self.append_address)
        self.configure()
    def append_address(self, ip):
        model = self.address_table.model()
        row = model.rowCount(None)
        model.insertRows(row, 1)
        index = model.createIndex(row, 0)
        model.setData(index, QVariant(ip), Qt.DisplayRole)
    def configure(self):
        if os.path.isfile(self.PAGES):
            links = pickle.load(open(self.PAGES))
            self.pages_table.model().data = links
    def insert_row(self, table):
        selected = table.selectedIndexes()
        if selected:
            last = selected[-1]
            row = last.row() + 1
        else:
            row = 0
        table.model().insertRows(row, 1)
    def remove_row(self, table):
        rows = [ndx.row() for ndx in table.selectedIndexes() if ndx.column() == 0]
        rows.sort(reverse=True)
        for row in rows:
            table.model().removeRows(row, 1)
    def run(self):
        self.pd = ProgressDialog(self)
        self.pd.setWindowTitle(u"Получение адресов")
        self.pd.setLabelText(u"Формирование списка")
        addresses = self.pages_table.model().data
        queue = Queue()
        for link in addresses:
            if not link.strip():
                continue
            queue.put(link)
        for i in range(len(addresses)): #@UnusedVariable
            queue.put("STOP")
        self.pd.setRange(0, len(addresses))
        self.pd.setValue(0)
        self.pd.setLabelText(u"Обработка")
        ths = []
        for i in range(self.threads_se.value()): #@UnusedVariable
            th = PagesParserThread(queue, self)
            th.start()
            ths.append(th)
        self.pd.exec_()
        if self.pd.wasCanceled():
            for th in ths:
                if th.isRunning():
                    th.wait(100)
                    th.terminate()
    def clear(self):
        def s(w):
            data = list(set(w.model().data))
            w.model().data = data
            w.model().modelReset.emit()
        s(self.pages_table)
        s(self.address_table)
    def parse_se(self):
        form = SEParserDialog(self)
        if not form.exec_():
            return        
        model = self.pages_table.model()
        row = model.rowCount(None)
        links = form.get_links()
        model.insertRows(row, len(links))
        for i in range(len(links)):
            index = model.createIndex(row + i, 0)
            model.setData(index, QVariant(links[i]), Qt.DisplayRole)
    def accept(self):
        pages = self.pages_table.model().data
        pickle.dump(pages, open(self.PAGES, "wb"))
        self.setResult(1)
        self.hide()
    def get_addresses(self):
        return self.address_table.model().data
    def show_error(self, err):
        self.pd.hide()
        self.errmsg.setWindowTitle(u"Ошибка")
        self.errmsg.showMessage(err)

class TargetDialog(QDialog):
    CHECKLIST = os.path.join(HOMEPATH, "targets.pkl")
    DEFAULT = (
        ("http://www.google.com", u"<title>Google</title>"),
        ("http://www.yandex.ru", u"<title>Яндекс</title>"),
        ("http://market.yandex.ru", u"<title>Яндекс.Маркет")
    )
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle(u"Редактор целей")
        self.resize(500, 500 * 0.73)
        layout = QGridLayout(self)
        tb = ToolBar(self)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/add.png"), u"&Добавить",
            self.add_row)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/delete.png"), u"&Удалить",
            self.del_row)
        layout.addWidget(tb, 0, 0)
        self.table = QTableWidget(0, 2)
        self.table.verticalHeader().setDefaultSectionSize(
            self.table.verticalHeader().fontMetrics().height() + 4)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem(u"Адрес",
            QTableWidgetItem.UserType + 1))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem(u"Метка",
            QTableWidgetItem.UserType + 1))
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1, 0)
        bbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close, Qt.Horizontal, self)
        layout.addWidget(bbox, 2, 0)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        self.configure()
    def configure(self):
        if os.path.isfile(self.CHECKLIST):
            links = pickle.load(open(self.CHECKLIST))
        else:
            links = self.DEFAULT
        for egg in links:
            self.table.insertRow(0)
            item0 = QTableWidgetItem(egg[0], QTableWidgetItem.UserType + 1)
            item1 = QTableWidgetItem(egg[1], QTableWidgetItem.UserType + 1)
            self.table.setItem(0, 0, item0)
            self.table.setItem(0, 1, item1)
        self.table.setSortingEnabled(True)
    def add_row(self):
        self.table.setSortingEnabled(False)
        row = self.table.currentRow() + 1
        self.table.insertRow(row)
        item0 = QTableWidgetItem("", QTableWidgetItem.UserType + 1)
        item1 = QTableWidgetItem("", QTableWidgetItem.UserType + 1)
        self.table.setItem(row, 0, item0)
        self.table.setItem(row, 1, item1)
        self.table.setSortingEnabled(True)
    def del_row(self):
        rows = [i.row() for i in self.table.selectedIndexes() if i.column() == 0]
        for i in sorted(rows, reverse=True):
            self.table.removeRow(i)
    def accept(self):
        self.links = links = []
        for row in range(self.table.rowCount()):
            site = unicode(self.table.item(row, 0).text())
            tag = unicode(self.table.item(row, 1).text())
            links.append((site, tag))
        pickle.dump(tuple(links), open(self.CHECKLIST, "wb"))
        self.setResult(1)
        self.hide()

class ProxyState(object): 
    OK, NOANSWER, NOTESTED = range(3)

class ProxyServer(object):
    def __init__(self, address="", delay=0, state=ProxyState.NOTESTED):
        self.address = address
        self.delay = delay
        self.state = state
    def get_delay(self):
        if self.state != ProxyState.OK:
            return 0xffff
        else:
            return self.delay

class ProxyListModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self)
        self.parent = parent
        self.labels = [u"Адреса", u"Время отклика"]
        self.data = []
    def rowCount(self, parent):
        return len(self.data)
    def columnCount(self, parent):
        return len(self.labels)
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()
        value = ''
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            if col == 0:
                value = self.data[row].address
            elif col == 1:
                state = self.data[row].state
                if state == ProxyState.NOTESTED:
                    value = u"Не тестировался"
                elif state == ProxyState.NOANSWER:
                    value = u"Не отвечает"
                elif state == ProxyState.OK:
                    value = self.data[row].delay
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 0:
                value = self.data[row].address
        return QVariant(value)        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section + 1)
        return QVariant()
    def flags(self, index):
        default = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 0:
            default |= Qt.ItemIsEditable 
        return default
    def setData(self, index, data, role):
        try:
            row = index.row()
            col = index.column()
            if col == 0:
                self.data[row].address = unicode(data.toString())
                self.data[row].state = ProxyState.NOTESTED
            elif col == 1:
                self.data[row].state = ProxyState.OK
                self.data[row].delay = data.toFloat()
            return True
        except:
            return False
    def sort(self, col, order):
        if col == 0:
            colkey = operator.attrgetter("address") 
        elif col == 1:
            colkey = operator.methodcaller("get_delay") 
        reverse = order != Qt.AscendingOrder
        self.data.sort(key=colkey, reverse=reverse)
        ifrom = self.createIndex(0, 0)
        ito = self.createIndex(self.rowCount(None), self.columnCount(None))
        self.dataChanged.emit(ifrom, ito)
    def insertRows(self, pos, rows, index=QModelIndex()):
        self.beginInsertRows(index, pos, pos + rows - 1)
        for row in range(rows): #@UnusedVariable
            self.data.insert(pos, ProxyServer("0.0.0.0"))
        self.endInsertRows()
        return True
    def removeRows(self, pos, rows, index=QModelIndex()):
        self.beginRemoveRows(index, pos, pos + rows - 1);
        for i in range(rows): #@UnusedVariable
            self.data.pop(pos)
        self.endRemoveRows()
        return True

class CheckerThread(QThread):
    def __init__(self, queue, target, parent, model):
        QThread.__init__(self, parent)
        self.model = model
        self.queue = queue
        self.target = target
        self.parent = parent
        self.stop = False
    def run(self):
        log.debug("run thread")
        for row in iter(self.queue.get, "STOP"):
            server = self.model.data[row]
            self.check(server)
            index = self.model.createIndex(row, 1)
            self.model.dataChanged.emit(index, index)
            self.parent.emit(SIGNAL("incProgress()"))
            if self.stop:
                break
        log.debug("done thread")
    def check(self, server):
        self.parent.emit(SIGNAL("textProgress(QString)"),
                         u"Подключение к %s" % server.address)
        proxy_handler = urllib2.ProxyHandler({"http": server.address})
        http_handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(proxy_handler, http_handler)
        opener.addheaders = [("User-agent", "Mozilla/5.0")]
        t = time.time()
        socket.setdefaulttimeout(TIMEOUT)
        while time.time() - t < TIMEOUT:
            try:
                req = urllib2.Request(self.target[0])
                response = opener.open(req, timeout=TIMEOUT)
                data = response.read()
                encoding = chardet.detect(data)
                encdata = data.decode(encoding["encoding"])
                encdata.index(self.target[1])
                server.state = ProxyState.OK
                server.delay = time.time() - t
                log.debug("proxycheck success")
                self.parent.emit(SIGNAL("textProgress(QString)"),
                                 u"Удачно %s" % server.address)
                break
            except Exception, err:
                self.parent.emit(SIGNAL("textProgress(QString)"),
                                 u"Не отвечает %s" % server.address)
                log.warning("proxycheck exception: %s", err)
                server.state = ProxyState.NOANSWER
                time.sleep(0.1)
    def die(self):
        self.stop = True
        self.wait(100)
        self.terminate()

class CheckerDialog(QDialog):
    PROXY = os.path.join(HOMEPATH, "proxy.pkl")
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle(u"Проверка proxy-серверов")
        self.resize(600, 600 * 0.75)
        layout = QGridLayout(self)
        tb = ToolBar(self)
        menu = QMenu(self)
        menu.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/16x16/accept.png"),
                       u"Проверить выбранные", self.selected_check)
        tb1 = QToolButton(self)
        tb1.setToolButtonStyle(Qt.ToolButtonFollowStyle)
        tb1.setIcon(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/cog_go.png"))
        tb1.setText(u"&Запуск")
        tb1.setMenu(menu)
        tb1.setPopupMode(QToolButton.MenuButtonPopup)
        tb1.clicked.connect(self.check)
        tb.addWidget(tb1)                
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/page_world.png"),
            u"&Парсер страниц", self.parse_pages)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/cart_put.png"),
            u"&Импорт", self.import_file)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/cart_remove.png"),
            u"&Экспорт", self.export_file)
        layout.addWidget(tb)
        l1 = QHBoxLayout()
        l1.addWidget(QLabel(u"Потоков"))
        self.threads_sb = QSpinBox(self)
        self.threads_sb.setValue(3)
        l1.addWidget(self.threads_sb)
        l1.addWidget(QLabel(u"Цель"))
        self.target_cb = QComboBox(self)
        l1.addWidget(self.target_cb)
        edit_target_tb = QToolButton(self)
        edit_target_tb.setIcon(QIcon(":/icons/fatcow-hosting-icons-1700/16x16/add.png"))
        edit_target_tb.setText(u"Редактировать")
        edit_target_tb.setToolTip(u"Редактировать")
        edit_target_tb.clicked.connect(self.edit_targets)
        l1.addWidget(edit_target_tb)
        l1.addWidget(QLabel(u"Таймаут"))
        self.timeout_sb = QSpinBox(self)
        self.timeout_sb.setRange(0, 120)
        self.timeout_sb.setValue(30)
        l1.addWidget(self.timeout_sb)
        l1.addStretch(1)
        layout.addLayout(l1, 1, 0)
        self.table = QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(
            self.table.verticalHeader().fontMetrics().height() + 4)
        model = ProxyListModel(self.table)
        self.table.setModel(model)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table)
        tb = ToolBar(self, style=Qt.ToolButtonIconOnly)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/add.png"), u"&Добавить",
            self.insert_row)
        tb.addAction(QIcon(":/icons/fatcow-hosting-icons-1700/32x32/delete.png"), u"&Удалить",
            self.remove_row)
        layout.addWidget(tb)
        bbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close, Qt.Horizontal, self)
        layout.addWidget(bbox)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        self.errmsg = QErrorMessage(self)
        self.errmsg.setModal(True)
        self.configure()
        self.pd = ProgressDialog(self)
        self.connect(self, SIGNAL("incProgress()"), self.pd.inc_value)
        self.connect(self, SIGNAL("textProgress(QString)"), self.pd.setLabelText)
    def configure(self):
        if os.path.isfile(self.PROXY):
            links = pickle.load(open(self.PROXY))
            for row in links:
                proxy = ProxyServer(row[0], row[1], row[2])
                self.table.model().data.append(proxy)
            self.table.reset()
        if os.path.isfile(TargetDialog.CHECKLIST):
            links = pickle.load(open(TargetDialog.CHECKLIST))
        else:
            links = TargetDialog.DEFAULT
        for row in links:
            self.target_cb.addItem(row[0], QVariant(row[1]))
    def export_file(self):
        try:
            fileName = QFileDialog.getSaveFileName(self, u"Экспорт", ".",
                                                   u"список proxy (*.txt)")
            if fileName == "":
                return
            fileName = unicode(fileName)
            with open(fileName, "wt") as fout:
                for row in self.table.model().data:
                    fout.write("%s\n" % row.address) 
        except IOError, err:
            self.errmsg.setWindowTitle(u"Ошибка")
            self.errmsg.showMessage(err)
    def import_file(self):
        try:
            fileName = QFileDialog.getOpenFileName(self, u"Импорт", ".",
                                                   u"список proxy (*.txt)")
            if fileName:
                fileName = unicode(fileName)
                data = self.table.model().data
                for row in open(fileName).readlines():
                    data.append(ProxyServer(row.strip()))
                self.table.model().reset()
        except IOError, err:
            self.errmsg.setWindowTitle(u"Ошибка")
            self.errmsg.showMessage(err)
    def insert_row(self):
        selected = self.table.selectedIndexes()
        if selected:
            last = selected[-1]
            row = last.row() + 1
        else:
            row = 0
        self.table.model().insertRows(row, 1)
    def remove_row(self):
        rows = [ndx.row() for ndx in self.table.selectedIndexes() if ndx.column() == 0]
        rows.sort(reverse=True)
        for row in rows:
            self.table.model().removeRows(row, 1)
    def edit_targets(self):
        form = TargetDialog(self)
        if not form.exec_():
            return
        self.target_cb.clear()
        for row in form.links:
            self.target_cb.addItem(row[0], QVariant(row[1]))
    def parse_pages(self):
        form = PagesParserDialog(self)
        if not form.exec_():
            return
        data = self.table.model().data
        for addr in form.get_addresses():
            data.append(ProxyServer(addr))
        self.table.model().reset()
    def accept(self):
        urls = []
        for row in self.table.model().data:
            urls.append((row.address, row.delay, row.state))
        pickle.dump(urls, open(self.PROXY, "wb"))
        self.setResult(1)
        self.hide()
    def selected_check(self):
        rows = [ndx.row() for ndx in self.table.selectedIndexes() if ndx.column() == 0]
        self.check(rows)
    def check(self, rows=[]):
        global TIMEOUT
        model = self.table.model()
        TIMEOUT = self.timeout_sb.value()
        target = (unicode(self.target_cb.currentText()),
                  unicode(self.target_cb.itemData(self.target_cb.currentIndex()).toString()))
        if not rows:
            rows = range(model.rowCount(None))
        self.pd.setWindowTitle(u"Проверка прокси")
        self.pd.setLabelText(u"Формирование списка")
        self.pd.setRange(0, len(rows))
        self.pd.setValue(0)
        queue = Queue()
        for i in rows:
            queue.put(i)
        for i in range(self.threads_sb.value()): #@UnusedVariable
            queue.put("STOP")
        self.pd.setLabelText(u"Обработка")
        ths = []
        for i in range(self.threads_sb.value()): #@UnusedVariable
            th = CheckerThread(queue, target, self, model)
            th.start()
            ths.append(th)
        self.pd.exec_()
        if self.pd.wasCanceled():
            for th in ths:
                if th.isRunning():
                    th.die()
        self.pd.setValue(len(rows))
        
if __name__ == "__main__":
    app = QApplication([""])
    form = CheckerDialog()
    form.exec_()
