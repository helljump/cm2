#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
import hunspell
import yaml
import codecs
import os
from utils.misc import get_word_spans_iter
from PyQt4 import QtGui

log = logging.getLogger(__name__)


import sys
if hasattr(sys, "frozen"):
    ROOT = os.path.dirname(sys.executable)
else:
    ROOT = os.path.dirname(__file__)
ROOT = unicode(ROOT, encoding=sys.getfilesystemencoding())
config = yaml.load(codecs.open(ROOT + '/spell/spell.yml', "r", "utf-8"))
SPELL_DIR = os.path.join(ROOT, 'spell')
SPELL_DIR = SPELL_DIR.encode(sys.getfilesystemencoding())


def load_spell(key):
    log.debug("load hunspell: %s", config[key])
    hobj = hunspell.HunSpell(os.path.join(SPELL_DIR, config[key][1]),
                             os.path.join(SPELL_DIR, config[key][0]))
    encoding = hobj.get_dic_encoding()
    return hobj, encoding

class SpellException(Exception):
    def __init__ (self, value):
        self.value = value

class SpellDialog(QtGui.QDialog):
    def __init__(self, parent, text_widget):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Проверка орфографии")
        self.resize(382, 268)
        self.parent = parent
        self.text_widget = text_widget
        self.gridLayout = QtGui.QGridLayout(self)
        self.label = QtGui.QLabel(u"Фраза", self)
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.phrase_te = QtGui.QPlainTextEdit(self)
        self.phrase_te.setReadOnly(True)
        self.gridLayout.addWidget(self.phrase_te, 3, 0, 2, 2)
        self.label_2 = QtGui.QLabel(u"Варианты", self)
        self.gridLayout.addWidget(self.label_2, 7, 0, 1, 1)
        self.variants_lw = QtGui.QListWidget(self)
        self.gridLayout.addWidget(self.variants_lw, 8, 0, 2, 2)
        self.variants_cb = QtGui.QComboBox(self)
        self.gridLayout.addWidget(self.variants_cb, 0, 1, 1, 1)
        self.skip_pb = QtGui.QPushButton(u"Начать", self)
        self.gridLayout.addWidget(self.skip_pb, 3, 2, 1, 1)
        self.replace_pb = QtGui.QPushButton(u"Заменить", self)
        self.gridLayout.addWidget(self.replace_pb, 4, 2, 1, 1)
        self.label_3 = QtGui.QLabel(u"Язык", self)
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.close_pb = QtGui.QPushButton(u"Закрыть", self)
        self.gridLayout.addWidget(self.close_pb, 9, 2, 1, 1)

        self.close_pb.clicked.connect(self.hide)
        self.skip_pb.released.connect(self.select_next_word)

        self.replace_pb.released.connect(self.replace_word)
        self.variants_lw.itemDoubleClicked.connect(self.replace_word)

        self.show_Event()

    def show_Event(self):
        """
        1. загружаем список словарей
        2. если есть русский - включаем его
        """
        for item in config.items():
            self.variants_cb.addItem(item[0], item[1])
        self.variants_cb.currentIndexChanged.connect(self.reload_dict)
        rndx = self.variants_cb.findText(u"Русский")
        if rndx > -1:
            self.variants_cb.setCurrentIndex(rndx)
        self.replace_pb.setEnabled(False)
        try:
            self.make_spans()
            self.select_next_word()
        except SpellException, ex:
            log.debug("something wrong")
            QtGui.QMessageBox.question(self.parent, u"Проверка орфографии",
                                       ex.value, QtGui.QMessageBox.Ok)
            raise

    def make_spans(self):
        QtGui.qApp.processEvents()
        log.debug("reload text from widget")
        text = unicode(self.text_widget.text())
        self.spans = list(get_word_spans_iter(text))
        from_pos = self.get_cursor_position()
        self.offset = 0
        log.debug("remove spans before cursor: %i", from_pos)
        while self.spans and from_pos:
            egg = self.spans[0]
            if egg['spans'][1] >= from_pos:
                break
            del self.spans[0]
        log.debug("spans left: %i", len(self.spans))
        if not self.spans:
            raise SpellException(u"Нет слов для проверки.")

    def reload_dict(self, i):
        """ перезагрузка словаря при смене языка """
        egg = [ os.path.join(SPELL_DIR, unicode(item))
            for item in self.variants_cb.itemData(i).toPyObject()]
        log.debug("load dic: %s", egg)
        self.hobj = hunspell.HunSpell(egg[1], egg[0])
        self.encoding = self.hobj.get_dic_encoding()
        log.debug("new hobj: %s", self.encoding)

    def get_cursor_position(self):
        cLine, cPos = self.text_widget.getCursorPosition()
        from_pos = cPos
        for l in range(cLine):
            egg = self.text_widget.text(l)
            from_pos += egg.length()
        return from_pos

    def replace_word(self, item=None):
        old_len = len(unicode(self.phrase_te.toPlainText()))
        egg = self.variants_lw.selectedItems()
        egg_text = egg[0].text()
        new_len = len(unicode(egg_text))
        self.offset += new_len - old_len
        self.text_widget.removeSelectedText()
        self.text_widget.insert(egg_text)
        self.select_next_word()

    def select_next_word(self):
        self.skip_pb.setText(u"Пропустить")
        self.replace_pb.setEnabled(True)
        try:
            while True:
                if not self.spans:
                    raise SpellException(u"Проверка орфографии окончена.")

                egg = self.spans.pop(0)
                sugs = self.hobj.suggest(egg['word'].encode(self.encoding, "replace"))
                if not sugs:
                    continue

                print egg["line"]
                self.text_widget.setSelection(0, egg['spans'][0] + self.offset - egg["line"],
                                              0, egg['spans'][1] + self.offset - egg["line"])
                self.phrase_te.setPlainText(egg['word'])
                self.variants_lw.clear()
                for word in sugs:
                    egg = unicode(word, self.encoding)
                    self.variants_lw.addItem(egg)
                    self.variants_lw.setCurrentRow(0)
                break

        except SpellException, ex:
            QtGui.QMessageBox.question(self, u"Проверка орфографии",
                                       ex.value, QtGui.QMessageBox.Ok)
            self.hide()

if __name__ == "__main__":
    src = u"человечка"
    hobj, henc = load_spell(u"Русский")
    word = hobj.stem(src.encode(henc, "replace"))
    print word[0].decode(henc)
