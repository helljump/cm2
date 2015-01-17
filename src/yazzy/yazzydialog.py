#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

if __name__ == '__main__':
    import sys
    sys.path.append('..')

from logging import debug
from PyQt4 import QtCore, QtGui
import edit.icons  # @UnusedImport
from utils.qthelpers import MyProgressDialog
from utils.misc import iget_dir_content
import os
from stopdialog import StopDialog
from yasyn2 import getYASName
import shelve

from utils.paths import CONFIGFILE


class MyListItem(QtGui.QListWidgetItem):
    def __init__(self, fname, parent):
        QtGui.QWidget.__init__(self, parent)
        self.fname = fname
        self.setCheckState(QtCore.Qt.Unchecked)
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable |
            QtCore.Qt.ItemIsEnabled)
        rname = getYASName(fname)
        self.setText(rname)


class YazzyDialog(QtGui.QDialog):

    DICT_PATH = "dict"

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.resize(320, 480)
        self.setWindowTitle(u"Синонимизация")

        gridLayout = QtGui.QGridLayout(self)
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)

        frame = QtGui.QFrame(self)
        fl = QtGui.QGridLayout(frame)
        fl.addWidget(QtGui.QLabel(u"Минимальное расстояние", frame), 0, 0)

        self.worddistant = QtGui.QSpinBox(self)
        self.worddistant.setRange(0, 1024)
        fl.addWidget(self.worddistant, 0, 1)

        self.use_internal = QtGui.QCheckBox(u"Встроенный словарь", self)
        fl.addWidget(self.use_internal, 1, 0)

        self.syno_title = QtGui.QCheckBox(u"Заголовок", self)
        fl.addWidget(self.syno_title, 0, 3)

        self.syno_text = QtGui.QCheckBox(u"Текст", self)
        fl.addWidget(self.syno_text, 0, 4)

        self.syno_intro = QtGui.QCheckBox(u"Вступление", self)
        fl.addWidget(self.syno_intro, 1, 4)

        self.use_stopwords = QtGui.QCheckBox(u"Стоп-слова", self)
        fl.addWidget(self.use_stopwords, 0, 6)

        self.gen_template = QtGui.QCheckBox(u"Генерировать шаблон", self)
        fl.addWidget(self.gen_template, 0, 7)

        stopwords_pb = QtGui.QPushButton(u"Список стоп-слов", self)
        stopwords_pb.clicked.connect(self.edit_stopwords)
        fl.addWidget(stopwords_pb, 1, 6)

        self.process_cats = QtGui.QCheckBox(u"Обработка категорий", self)
        fl.addWidget(self.process_cats, 1, 3)

        gridLayout.addWidget(frame, 1, 0, 1, 1)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        gridLayout.addWidget(buttonBox, 2, 0, 1, 1)

        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)

        settings = shelve.open(CONFIGFILE)
        config = settings.get("YazzyDialog", {})
        self.worddistant.setValue(config.get("worddistant", 1))
        self.use_internal.setChecked(config.get("use_internal", False))
        self.use_stopwords.setChecked(config.get("use_stopwords", False))
        self.syno_title.setChecked(config.get("syno_title", True))
        self.syno_text.setChecked(config.get("syno_text", True))
        self.syno_intro.setChecked(config.get("syno_intro", True))
        self.process_cats.setChecked(config.get("process_cats", True))
        self.gen_template.setChecked(config.get("gen_template", False))
        self.stopwords = config.get("stopwords", [])
        self.bases = config.get("bases", [])
        settings.close()
        self.reload_dictlist(parent)

    #def showEvent(self, event):
    #    event.accept()

    def edit_stopwords(self):
        dlg = StopDialog(self.stopwords, self)
        rc = dlg.exec_()
        if rc:
            self.stopwords = dlg.result

    def reload_dictlist(self, parent):
        debug("reload dicts")

        if not os.path.isdir(self.DICT_PATH):
            return  # os.mkdir(self.DICT_PATH)

        pd = MyProgressDialog(u"Словари", u"Поиск", u"Отмена", 0, 0, parent)
        pd.setMaximumWidth(320)
        pd.show()

        dicts = []
        for d in iget_dir_content(self.DICT_PATH, [".csv", ".yas"]):
            dicts.append(d)
            QtGui.qApp.processEvents()

        pd.set_text(u"Формирование списка")

        for fname in dicts:
            debug("found %s", fname)
            item = MyListItem(os.path.join(self.DICT_PATH, fname), self.listWidget)
            if os.path.join(self.DICT_PATH, fname) in self.bases:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            QtGui.qApp.processEvents()

        pd.close()

    def accept(self):
        self.setResult(1)
        settings = shelve.open(CONFIGFILE)
        self.params = config = {}
        config['worddistant'] = int(self.worddistant.value())
        config['use_internal'] = self.use_internal.isChecked()
        config['use_stopwords'] = self.use_stopwords.isChecked()
        config['syno_title'] = self.syno_title.isChecked()
        config['syno_text'] = self.syno_text.isChecked()
        config['syno_intro'] = self.syno_intro.isChecked()
        config['process_cats'] = self.process_cats.isChecked()
        config['gen_template'] = self.gen_template.isChecked()
        config['stopwords'] = self.stopwords
        self.bases = []
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState() == QtCore.Qt.Checked:
                item = unicode(self.listWidget.item(i).fname)
                self.bases.append(item)
        config['bases'] = self.bases
        settings["YazzyDialog"] = config
        settings.close()
        self.hide()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg = YazzyDialog()
    dlg.show()
    rc = dlg.exec_()
