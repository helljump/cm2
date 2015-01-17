#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

try:
    from plugtypes import IImportPlugin #@UnresolvedImport
except ImportError:
    IImportPlugin = object
    import sys
    sys.path.append("d:\\work\\cm2\\src")

from collections import defaultdict
from random import choice, randint
from utils.qthelpers import MyProgressDialog
from PyQt4 import QtGui, QtCore
from utils.article import Article
import logging 

log = logging.getLogger(__name__)

class MarkovChain(IImportPlugin):
    def run(self, parent):
        dlg = Dialog(parent)
        if not dlg.exec_():
            return None
        qty = dlg.qty_sb.value()
        _from = dlg.from_sb.value()
        _to = dlg.to_sb.value()
        _text = unicode(dlg.textedit.toPlainText())
        log.debug("run markovgen")
        root = Article()
        textgen = TextGenerator()
        textgen.train(_text)
        pd = MyProgressDialog(u"Генератор", u"Генерация статей", u"Отмена",
                              0, qty, parent)
        pd.setMaximumWidth(320)
        pd.show()
        for i in range(qty):
            words = randint(_from, _to)
            text = textgen.gentext(words)
            title = text.split(".")[0]
            root.add_child(Article(title, text))
            pd.set_value(i)
            pd.set_text(title)
            QtGui.qApp.processEvents()
        pd.close()    
        return root

warning = u"""Это <b>пример</b> импорт-плагина.
Не используйте сгененированные им тексты на рабочих сайтах.
"""

class Dialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Генератор текста")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(500, 500 * 0.73)
        self.parent = parent
        layout = QtGui.QGridLayout(self)
        egg = QtGui.QHBoxLayout()
        egg.addWidget(QtGui.QLabel(u"Количество статей"))
        self.qty_sb = QtGui.QSpinBox()
        self.qty_sb.setRange(1, 10000)
        self.qty_sb.setValue(200)
        egg.addWidget(self.qty_sb, 1)
        egg.addWidget(QtGui.QLabel(u"Слов в статье, от"))
        self.from_sb = QtGui.QSpinBox()
        self.from_sb.setRange(1, 1000)
        self.from_sb.setValue(150)
        egg.addWidget(self.from_sb, 1)
        egg.addWidget(QtGui.QLabel(u"до"))
        self.to_sb = QtGui.QSpinBox()
        self.to_sb.setRange(1, 1000)
        self.to_sb.setValue(250)
        egg.addWidget(self.to_sb, 1)
        layout.addLayout(egg, 0, 0)
        layout.addWidget(QtGui.QLabel(u"Базовый текст"), 1, 0)
        self.textedit = QtGui.QTextEdit(self)
        self.textedit.setText(text)
        layout.addWidget(self.textedit, 2, 0)
        layout.addWidget(QtGui.QLabel(warning), 3, 0)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        layout.addWidget(buttonBox, 4, 0)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)

class TextGenerator(object): 
    def __init__(self):
        self._data = defaultdict(list)
    def train(self, text):
        words = [None, None]
        for word in text.split():
            words[0], words[1] = words[1], word
            if words[0]:
                self._data[words[0]].append(words[1])
    def gentext(self, num_words):
        text = []
        text.append(choice(self._data.keys()).title())
        while len(text) < num_words:
            if self._data.has_key(text[-1]):
                text.append(choice(self._data[text[-1]]))
            else:
                text.append(choice(self._data.keys()))
        return ' '.join(text) + '.'

text = """
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
JFOFCQHTUYuQ""".decode("base64").decode("bz2").decode("utf8").strip()

if __name__ == '__main__':
    #import sys
    #app = QtGui.QApplication(sys.argv)
    #MarkovChain().run(None)
    
    tg = TextGenerator()
    tg.train("ага, давай так я вчера чуть не утонул вечером под дождем Списался с АИ,"\
        " выбрали ром и сигары. Вродеб заказал через инет все я убегаю акисмет можно ж ?"\
        " я просто к чему можно заказать написание примерно 10-15 комментов в день с нужными"\
        " ключами и прочим это очень полезно для сео дополнительный контент, обновление постоянное и пр")
    print tg.gentext(15)
