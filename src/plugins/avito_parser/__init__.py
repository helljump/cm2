#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

"""
spynner не работает в отдельной нитке!
"""


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import logging
import os
import yaml
import unicodecsv as csv

from plugtypes import IUtilitePlugin
import config_dialog
from tesseract import TessPageSegMode
from avito import Avito


log = logging.getLogger(__name__)


"""
def try_except(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception, e:
            et, ei, tb = sys.exc_info()
            raise MyError, MyError(e), tb
    return wrapped
"""


class SettingsDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        egg = os.path.join(os.path.dirname(__file__), 'settings.ui')
        uic.loadUi(egg, self)
        self.settfile = os.path.join(os.path.dirname(__file__), 'settings.yml')
        try:
            data = yaml.load(open(self.settfile))
            self.lineEdit.setText(data['url'])
            self.lineEditButton.setText(data['path'])
            self.checkBox.setChecked(data['use_proxy'])
            self.spinBox.setValue(data['timeout'])
            self.att_spinBox.setValue(data['attempts'])
        except (IOError, yaml.scanner.ScannerError, TypeError, KeyError):
            pass

    @pyqtSlot(bool, name='on_lineEditButton_clicked')
    def set_fname(self, v):
        egg = unicode(self.lineEditButton.text)
        path = os.path.dirname(egg)
        fname = QFileDialog.getSaveFileName(self, directory=path, filter="Comma Separated Values(*.csv)")
        if not fname:
            return
        self.lineEditButton.setText(unicode(fname))

    def accept(self):
        sett = {
            'url': unicode(self.lineEdit.text()),
            'path': unicode(self.lineEditButton.text),
            'use_proxy': self.checkBox.isChecked(),
            'timeout': self.spinBox.value(),
            'attempts': self.att_spinBox.value(),
        }
        yaml.dump(sett, open(self.settfile, 'w'), encoding='utf-8', default_flow_style=False)
        QDialog.accept(self)


class Plugin(IUtilitePlugin):

    def _make_pd(self, parent, title):
        pd = QProgressDialog(u'Подключаемся', u'Отмена', 0, 0, parent)
        pd.setWindowTitle(title)
        pd.setModal(True)
        pd.setMinimumWidth(320)
        pd.setAutoClose(False)
        return pd

    def run(self, parent):
        dlg = SettingsDialog(parent)
        rc = dlg.exec_()
        if not rc:
            return
        foutname = unicode(dlg.lineEditButton.text)
        baseurl = unicode(dlg.lineEdit.text())
        use_proxy = dlg.checkBox.isChecked()
        timeout = dlg.spinBox.value()
        attempts = dlg.att_spinBox.value()
        proxylist = config_dialog.get_proxy_list() if use_proxy else None

        parser = Avito(baseurl, os.path.dirname(foutname), proxylist, timeout=timeout,
            attempts=attempts)

        pd = self._make_pd(parent, dlg.windowTitle())
        pd.show()

        try:
            parent.tess.set_pagemode(TessPageSegMode.PSM_SINGLE_LINE)
            fout = open(foutname, 'wb')
            writer = csv.writer(fout, encoding='utf-8', delimiter=';', quotechar='\"',
                quoting=csv.QUOTE_NONNUMERIC)
            cnt = 0

            # title, phoneimage, intro, full, seller, price, datestring, images

            for row in parser.parse_items():
                if pd.wasCanceled():
                    parser.browser.hide()
                    break

                if type(row) is not tuple:
                    pd.setLabelText(row)
                    continue

                cnt += 1
                row = list(row)
                pd.setLabelText(u'Распознаем %s' % row[0])

                phone = parent.tess.recognize(row[3], basewidth=300, whitelist='0123456789-')
                row[3] = phone

                images = row[-1]
                del row[-1]
                row.extend(images)

                writer.writerow(row)

            pd.close()
            QMessageBox.information(parent, dlg.windowTitle(), u'Обработано %i позиций' % cnt)

        except Exception as err:
            log.exception("thread error")
            pd.close()
            QMessageBox.critical(parent, dlg.windowTitle(), unicode(err))

        finally:
            fout.close()
