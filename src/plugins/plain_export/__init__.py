#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"


import logging
from plugtypes import IExportPlugin
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import codecs


log = logging.getLogger(__name__)


def unroll(start):
    yield start
    for child in start.get_children():
        for subchild in unroll(child):
            yield subchild


class SaveThread(QThread):

    task_setlabel = pyqtSignal(QString)
    task_setrange = pyqtSignal(int, int)
    task_setvalue = pyqtSignal(int)
    task_success = pyqtSignal(QString)
    task_error = pyqtSignal(QString)

    def __init__(self, parent, tree, fname):
        QThread.__init__(self, parent)
        self.parent = parent
        self.tree = tree
        self.fname = fname
        self.online = True

    @pyqtSlot()
    def abort(self):
        self.online = False
        self.wait(100)
        self.terminate()

    def run(self):
        try:
            fout = codecs.open(self.fname, 'wt', 'UTF-8')
            for el in unroll(self.tree):
                if el.text:
                    fout.write(el.text)
                    fout.write('\n')
                    self.task_setlabel.emit(el.title)
            fout.close()
            self.task_success.emit(u'Готово')
        except Exception as err:
            log.exception("Thread error")
            self.task_error.emit('%s' % err)


class PlainExportPlugin(IExportPlugin):

    TITLE = u'Построчный экспорт'

    def run(self, tree, parent):

        fname = QFileDialog.getSaveFileName(parent, u"Построчный экспорт", parent.current_save_path,
            u"Plain text (*.txt)")
        if fname == "":
            return
        fname = unicode(fname)
        parent.current_save_path = os.path.split(fname)[0]

        pd = QProgressDialog(u'Экспорт', u'Отмена', 0, 0, parent)
        pd.setWindowTitle(self.TITLE)
        pd.setModal(True)
        pd.setMinimumWidth(320)
        pd.setAutoClose(False)
        th = SaveThread(parent, tree, fname)

        def success(msg):
            pd.close()
            QMessageBox.information(parent, self.TITLE, msg)

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
