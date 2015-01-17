#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import logging
import os
from client import parser
from plugtypes import IUtilitePlugin
import config_dialog
from tesseract import TessPageSegMode


log = logging.getLogger(__name__)


class Dialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        uif = os.path.join(os.path.dirname(__file__), 'dialog.ui')
        uic.loadUi(uif, self)
        self.setWindowTitle(Plugin.TITLE)

    @pyqtSlot()
    def on_actionSave_triggered(self):
        txt = unicode(self.plainTextEdit.toPlainText())
        config_dialog.set_proxy_list(txt)
        QMessageBox.information(self, Plugin.TITLE, u'Прокси сохранены в файл CM2.')
        self.close()


class Thread(QThread):

    task_setlabel = pyqtSignal(QString)
    task_setrange = pyqtSignal(int, int)
    task_setvalue = pyqtSignal(int)
    task_success = pyqtSignal(QString)
    task_error = pyqtSignal(QString)

    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.parent = parent
        self.online = True

    @pyqtSlot()
    def abort(self):
        self.online = False
        self.wait(100)
        self.terminate()

    def run(self):
        try:
            msg = []
            self.parent.tess.set_pagemode(TessPageSegMode.PSM_SINGLE_LINE)
            for row in parser():
                if type(row) is tuple and type(row[0]) is int:
                    self.task_setrange.emit(*row)
                elif type(row) is unicode:
                    self.task_setlabel.emit(row)
                elif type(row) is int:
                    self.task_setvalue.emit(row)
                else:
                    port = self.parent.tess.recognize(row[1], whitelist='0123456789')
                    egg = '%s:%s'% (row[0], port)
                    self.task_setlabel.emit(egg)
                    msg.append(egg)
            self.task_success.emit('\n'.join(msg))
        except Exception as err:
            log.exception("thread error")
            self.task_error.emit('%s' % err)


class Plugin(IUtilitePlugin):

    TITLE = u'Парсер Proxy серверов'

    def run(self, parent):
        pd = QProgressDialog(u'Подключаемся', u'Отмена', 0, 0, parent)
        pd.setWindowTitle(self.TITLE)
        pd.setModal(True)
        pd.setMinimumWidth(320)
        pd.setAutoClose(False)
        th = Thread(parent)

        def success(msg):
            pd.close()
            dlg = Dialog(parent)
            dlg.plainTextEdit.setPlainText(msg)
            dlg.exec_()

        def error(msg):
            pd.close()
            QMessageBox.critical(parent, self.TITLE, msg)

        pd.canceled.connect(th.abort)
        th.task_setlabel.connect(pd.setLabelText)
        th.task_setrange.connect(pd.setRange)
        th.task_setvalue.connect(pd.setValue)
        th.task_success.connect(success)
        th.task_error.connect(error)

        pd.show()
        th.start()

