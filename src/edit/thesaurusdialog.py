#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import sys
import logging
from PyQt4 import QtCore, QtGui
from thesaurus import Thesaurus, ThesException
from utils.misc import get_word_spans_iter
from leven import Unic

log = logging.getLogger(__name__)

class ThesaurusModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(ThesaurusModel, self).__init__(parent)
        self.labels = u"Синоним|Сходный термин|Связанный термин|Антоним".split("|")
        self.forms = {"":""}

    def rowCount(self, parent=QtCore.QModelIndex()):
        return max([len(v) for k, v in self.forms.items()]) #@UnusedVariable

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.labels)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        try:
            if role == QtCore.Qt.DisplayRole:
                if col == 0:
                    return self.forms['syn'][row]
                elif col == 1:
                    return self.forms['sim'][row]
                elif col == 2:
                    return self.forms['con'][row]
                elif col == 3:
                    return self.forms['ant'][row]
        except IndexError:
            pass

        return QtCore.QVariant()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.labels[section])
        return QtCore.QVariant()

    def set_forms(self, forms):
        self.forms = forms
        self.reset()

class ThesaurusDialog(QtGui.QDialog):
    def __init__(self, parent, text_widget):
        super(ThesaurusDialog, self).__init__(parent)
        self.setWindowTitle(u"Рерайтер")
        self.resize(550, 550 * 0.75)

        self.parent = parent
        self.text_widget = text_widget

        self.gridLayout = QtGui.QGridLayout(self)

        self.model = ThesaurusModel(self)
        self.view = QtGui.QTableView(self)
        self.view.setModel(self.model)

        self.view.verticalHeader().hide()
        self.view.verticalHeader().setDefaultSectionSize(
            self.view.verticalHeader().fontMetrics().height() + 4)
        for i in range(len(self.model.labels)):
            self.view.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.Stretch)
        self.view.setAlternatingRowColors(True)

        self.view.doubleClicked.connect(self.double_clicked)
        self.view.clicked.connect(self.single_clicked)

        self.gridLayout.addWidget(self.view, 1, 0)

        l = QtGui.QGridLayout()
        l.addWidget(QtGui.QLabel(u"Термин"), 0, 0)
        self.phrase_le = QtGui.QLineEdit(self)
        l.addWidget (self.phrase_le, 0, 1)
        self.gridLayout.addLayout(l, 0, 0) #up

        l = QtGui.QGridLayout()

        self.progress_lb = QtGui.QLabel(u"Грузим морфологию", self)
        l.addWidget(self.progress_lb, 0, 0)

        self.progress_pb = QtGui.QProgressBar(self)
        l.addWidget (self.progress_pb, 0, 1)

        self.change_pb = QtGui.QPushButton(u"Начать", self)
        self.change_pb.clicked.connect(self.double_clicked)
        l.addWidget(self.change_pb, 0, 2)
        self.skip_pb = QtGui.QPushButton(u"&Пропустить", self)
        self.skip_pb.clicked.connect(self.select_next_therm)
        self.skip_pb.setEnabled(False)
        l.addWidget(self.skip_pb, 0, 3)
        self.close_pb = QtGui.QPushButton(u"Закрыть", self)
        self.close_pb.clicked.connect(self.hide)
        l.addWidget(self.close_pb, 0, 5)

        self.gridLayout.addLayout(l, 3, 0)

        try:
            self.make_spans()
        except ThesException, ex:
            log.debug("something wrong")
            QtGui.QMessageBox.question(self.parent, u"Обработка окончена",
                                       ex.value, QtGui.QMessageBox.Ok)
            raise

    def keyPressEvent(self, event):
        print "mod %x : scan %x" % (event.nativeModifiers(), event.nativeScanCode())
        is_alt = event.nativeModifiers() & 0x1000040 or event.nativeModifiers() & 0x4
        if (is_alt
            and event.nativeScanCode() == 0x22
            and self.skip_pb.isEnabled()==True
            ):
            self.select_next_therm()
        if (is_alt
            and event.nativeScanCode() == 0x19
            and self.change_pb.isEnabled()==True
            and self.change_pb.text()==u"Заменить"
            and hasattr(self,"cur_therm")
            ):
            self.replace_word()

    def showEvent(self, evt):
        super(ThesaurusDialog, self).showEvent(evt)

    def make_spans(self):
        self.progress_lb.setText(u"Формируем термины")
        QtGui.qApp.processEvents()
        log.debug("reload text from widget")
        text = unicode(self.text_widget.text())
        self.orig_text = text
        self.spans = list(get_word_spans_iter(text))
        from_pos = self.get_cursor_position()
        self.offset = 0
        log.debug("remove spans before cursor: %i", from_pos)
        self.progress_pb.setRange(0, len(self.spans))
        while self.spans and from_pos:
            egg = self.spans[0]
            if egg['spans'][1] >= from_pos:
                break
            del self.spans[0]
            self.progress_pb.setValue(self.progress_pb.value() + 1)
            QtGui.qApp.processEvents()
        log.debug("spans left: %i", len(self.spans))
        if not self.spans:
            raise ThesException(u"Нет слов для обработки.")

    def get_cursor_position(self):
        cLine, cPos = self.text_widget.getCursorPosition()
        from_pos = cPos
        for l in range(cLine):
            egg = self.text_widget.text(l)
            from_pos += egg.length()
        return from_pos

    def select_next_therm(self):
        try:
            while True:
                if not self.spans:
                    raise ThesException(u"Обработка окончена.")

                self.setEnabled(False)
                egg = self.spans.pop(0)

                self.phrase_le.setText(egg['word'])
                self.progress_pb.setValue(self.progress_pb.value() + 1)
                self.progress_lb.setText(u"Ищем в тезаурусе")
                QtGui.qApp.processEvents()

                rc = self.thes.get_syno(egg['word'])
                if not rc:
                    continue

                self.setEnabled(True)

                self.text_widget.setSelection(0, egg['spans'][0] + self.offset - egg["line"],
                                              0, egg['spans'][1] + self.offset - egg["line"])

                self.cur_therm = egg['word']
                self.model.set_forms(rc)
                break

        except ThesException, ex:
            QtGui.QMessageBox.information(self, u"Рерайт", ex.value,
                                       QtGui.QMessageBox.Ok)
            self.calc_shingles()
            self.hide()

    def calc_shingles(self):
        new_text = unicode(self.text_widget.text())
        new_shin = Unic(new_text)
        old_shin = Unic(self.orig_text)
        matches = len(new_shin & old_shin)
        maxlen = max([len(new_shin), len(old_shin)])
        percent = 100.0 / maxlen * matches
        QtGui.QMessageBox.information(self, u"Рерайт",
                                      u"Процент совпадения шинглов: %i%%" % percent,
                                      QtGui.QMessageBox.Ok)

    def replace_word(self):
        new_text = unicode(self.phrase_le.text())
        self.offset += len(new_text) - len(self.cur_therm)
        self.text_widget.removeSelectedText()
        self.text_widget.insert(new_text)
        self.select_next_therm()

    def double_clicked(self, index):
        if not hasattr(self, "thes"):
            self.thes = Thesaurus("ru")
            self.change_pb.setText(u"Заменить")
            self.select_next_therm()
            self.skip_pb.setEnabled(True)
        if type(index)!=type(True) and index.data().type() != QtCore.QVariant.String:
            return
        if hasattr(self,"cur_therm"):
            self.replace_word()

    def single_clicked(self, index):
        if index.data().type() == QtCore.QVariant.String:
            self.phrase_le.setText(unicode(index.data().toString()))


if __name__ == '__main__':
    sys.exit()
    app = QtGui.QApplication(sys.argv)
    ThesaurusDialog().exec_()
