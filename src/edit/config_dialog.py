#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = 'helljump'

import sys
if not hasattr(sys, "frozen"):
    sys.path.append('d:/work/cm2/src')

import os
from PyQt4 import QtGui
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
import shelve
from utils import paths
from utils.paths import CONFIGFILE
import icons  # @UnusedImport
from config_dialog_ui import Ui_Dialog


SECTION_NAME = 'main_settings'


class ConfigDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setupUi(self)
        self.load_settings()
        self.proxy_leb.icon = QIcon(":/ico32/img/folder.png")

    @pyqtSlot(bool, name='on_proxy_leb_clicked')
    def select_file(self):
        f = QFileDialog.getOpenFileName(self, caption=u'Выбор списка прокси', filter=u'Текстовый файл (*.txt)')
        if not f:
            return
        f = unicode(f)
        self.proxy_leb.setText(f)

    def load_settings(self):
        settings = shelve.open(CONFIGFILE)
        self.config = settings.get(SECTION_NAME, {})
        self.autosavetimeout_sb.setValue(self.config.get('autosave_timeout', 5))
        self.connecttimeout_sb.setValue(self.config.get('connect_timeout', 10))

        self.proxy_leb.setText(self.config.get('proxylist', ''))

        self.antigate_le.setText(self.config.get('antigate_key', ''))
        self.antigate_rb.setChecked(self.config.get('antigate_on', True))

        self.captchabot_le.setText(self.config.get('captchabot_key', ''))
        self.captchabot_rb.setChecked(self.config.get('captchabot_on', False))

        settings.close()

    def save_settings(self):
        settings = shelve.open(CONFIGFILE)
        self.config = {
            'autosave_timeout': self.autosavetimeout_sb.value(),
            'connect_timeout': self.connecttimeout_sb.value(),

            'proxylist': unicode(self.proxy_leb.text), # property

            'antigate_key': unicode(self.antigate_le.text()),
            'antigate_on': self.antigate_rb.isChecked(),

            'captchabot_key': unicode(self.captchabot_le.text()),
            'captchabot_on': self.captchabot_rb.isChecked(),
        }
        settings[SECTION_NAME] = self.config
        settings.close()

    def accept(self):
        self.save_settings()
        self.hide()


def get_proxy_list():
    sett = shelve.open(CONFIGFILE)
    c = sett.get(SECTION_NAME, {})
    fname = c.get('proxylist', None)
    sett.close()
    if fname and os.path.isfile(fname):
        egg = map(str.strip, open(fname, 'rt').readlines())
    else:
        egg = None
    return egg

def set_proxy_list(txt):
    sett = shelve.open(CONFIGFILE)
    c = sett.get(SECTION_NAME, {})
    fname = c.get('proxylist', None)
    sett.close()
    open(fname, 'w').write(txt)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec_())
