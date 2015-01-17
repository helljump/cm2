#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from plugtypes import IImportPlugin
from utils.qthelpers import MyProgressDialog, MyFile, MyString
from PyQt4 import QtCore, QtGui, Qsci
from dialog import Ui_Dialog
from preview_dialog import Ui_Dialog as Ui_Dialog_preview
import os
import re
from utils.article import Article
from utils.formlayout import fedit
from utils.tidy import autodecode
from StringIO import StringIO
import csv
from functools import partial
from utils.paths import pluginpath
import pickle
import templater
import json
import codecs
from xml.sax.saxutils import escape

LOG = logging.getLogger(__name__)
BASESPATH = os.path.join(*__file__.split(os.path.sep)[-3:-1])
ARTICLES_PREVIEW = 3

DEC = lambda x: x if type(x)==unicode else x.decode("utf-8","replace")
PARAGRAPH_RE = re.compile(r'((?:\r\n|\r|\n){2,})')
TAGS_RE = re.compile(",\s*")

class HtmlEdit(Qsci.QsciScintilla):
    def __init__(self, *args):
        Qsci.QsciScintilla.__init__(self, *args)
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(9)
        lxr = Qsci.QsciLexerHTML()
        lxr.setDefaultFont(font)
        lxr.setFont(font)
        self.setLexer(lxr)
        self.setUtf8(True)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setEdgeMode(Qsci.QsciScintilla.EdgeLine)
        self.setEdgeColumn(80)
        self.setEdgeColor(QtGui.QColor("#FFe0e0"))
        self.setBraceMatching(Qsci.QsciScintilla.SloppyBraceMatch)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#e0ffe0"))
        self.setFolding(Qsci.QsciScintilla.BoxedFoldStyle)
        self.setWrapMode( Qsci.QsciScintilla.WrapWord )        
        self.setMarginWidth(1, '')

class PreviewDialog(QtGui.QDialog, Ui_Dialog_preview):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        
class ConfigDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        
        #change widget
        egg = self.text_le.toPlainText()
        spam = self.text_le.sizePolicy()
        self.gridLayout_3.removeWidget(self.text_le)
        self.text_le.setParent(None)
        self.text_le = HtmlEdit(self.groupBox_2)
        self.text_le.setText(egg)
        self.text_le.setSizePolicy(spam)
        self.gridLayout_3.addWidget(self.text_le, 2, 0, 1, 4)
        
        egg = self.intro_le.toPlainText()
        spam = self.intro_le.sizePolicy()
        self.gridLayout_3.removeWidget(self.intro_le)
        self.intro_le.setParent(None)
        self.intro_le = HtmlEdit(self.groupBox_2)
        self.intro_le.setText(egg)
        self.intro_le.setSizePolicy(spam)
        self.gridLayout_3.addWidget(self.intro_le, 6, 0, 1, 4)
        
        self.selectfile_bp.clicked.connect(self.set_fname)
        for row in templater.get_dicts(BASESPATH):
            egg = QtGui.QListWidgetItem(row)
            egg.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | 
                QtCore.Qt.ItemIsEnabled)
            egg.setCheckState(QtCore.Qt.Unchecked)
            self.dicts_lw.addItem(egg)
            
        self.preview_bt = self.buttonBox.addButton(u"Предпросмотр", QtGui.QDialogButtonBox.ActionRole)
            
    def set_fname(self):
        egg = unicode(self.fname_le.text())
        path = os.path.split(egg)[0]
        fname = QtGui.QFileDialog.getOpenFileName(self, u"Открыть файл...", path,
            "Comma Separated Values(*.csv);;JavaScript Object Notation(*.json)")
        if not fname:
            return
        self.fname_le.setText(unicode(fname))

class CancelException(Exception):
    pass

class Plugin(IImportPlugin):
    configfile = os.path.join(pluginpath, "csv_import_pro.pkl")
    def run(self, parent):
        cd = ConfigDialog(parent)
        self.mainwindow = cd
        cd.preview_bt.clicked.connect(self.preview)
        #cd.preview_bt.clicked.connect(lambda: cd.fname_le.setDisabled(True))
        try:
            settings = pickle.load(open(Plugin.configfile, "rt"))
            LOG.debug("use plugin params")
            cd.fname_le.setText(settings["fname"])
            egg = cd.encoding_cb.findText(settings["encoding"])
            if egg != -1:
                cd.encoding_cb.setCurrentIndex(egg)
            cd.fielddelim_le.setText(settings["fielddelim"])
            cd.textdelim_le.setText(settings["textdelim"])
            cd.ignorefirst_cb.setCheckState(QtCore.Qt.Checked if settings["ignorefirst"] 
                else QtCore.Qt.Unchecked)
            cd.allowcat_cb.setCheckState(QtCore.Qt.Checked if settings["allowcat"] 
                else QtCore.Qt.Unchecked)
            cd.title_le.setText(settings["title"])
            cd.tags_le.setText(settings["tags"])
            cd.text_le.setText(settings["text"])
            cd.intro_le.setText(settings.get("intro","{$1}"))
            cd.cattitle_le.setText(settings.get("cattitle","{$1}"))
            for d in settings.get("dicts",[]):
                items = cd.dicts_lw.findItems(d, QtCore.Qt.MatchExactly)
                if items:
                    items[0].setCheckState(QtCore.Qt.Checked)
            cd.inwords_cb.setCheckState(QtCore.Qt.Checked if settings.get("inwords", False) 
                else QtCore.Qt.Unchecked)
        except IOError:
            LOG.debug("use defaults params")
        rc = cd.exec_()
        if not rc:
            return
            
        #get fields
        settings = self.make_settings(cd)
        pickle.dump(settings, open(Plugin.configfile, "wt"))            
        #save path
        parent.current_load_path = os.path.split(settings["fname"])[0]

        templater.INWORDS = settings["inwords"] #hack?
        templater.PATH = BASESPATH
        templater.load_bases(settings["dicts"])
        
        pd = MyProgressDialog(u"Импорт", u"Открытие файла", u"Отмена", 0, 0, parent)
        pd.show()
        try:
            pd.set_text(u"Читаем файл")
            pd.set_text(u"Генерируем статьи")
            tmproot = root = Article()

            for row in self.get_iterator(settings):
                for i in range(len(row)):
                    if type(row[i]) == int:
                        row[i] = str(row[i])
                if settings["ignorefirst"]:
                    settings["ignorefirst"] = False
                    continue
                if settings["allowcat"] and len(row)==1:
                    egg = templater.generate(settings["cattitle"], row)
                    tmproot = Article(egg)
                    root.add_child(tmproot)
                    pd.set_text(u"Добавили категорию: %s" % DEC(row[0]))
                    LOG.debug("add category %s", tmproot)
                else:
                    pd.set_text(u"Добавили материал: %s" % DEC(row[0]))
                    title, tags, text, intro = self.generate(row, settings)
                    tags = TAGS_RE.split(tags)
                    art = Article(title, text, tags)
                    art.intro = intro
                    tmproot.add_child(art)
                QtGui.qApp.processEvents()
                if pd.wasCanceled():
                    raise CancelException

        except CancelException:
            pass
        pd.close()
        return root

    def preview(self):
        settings = self.make_settings(self.mainwindow)
        
        templater.INWORDS = settings["inwords"] #hack?
        templater.PATH = BASESPATH
        templater.load_bases(settings["dicts"])        

        dlg = PreviewDialog(self.mainwindow)
        dlg.setModal(True)
        dlg.show()
        QtGui.qApp.processEvents()
        articles_preview = ARTICLES_PREVIEW
        template = u"""<h2>Заголовок: "%s"</h2>
        <h3>Метки: "%s"</h3>
        <h3>Текст</h3>
        %s
        <h3>Вступление</h3>
        %s
        <br/>
        """
        for row in self.get_iterator(settings):        
            for i in range(len(row)):
                if type(row[i]) == int:
                    row[i] = str(row[i])
            if settings["ignorefirst"]:
                settings["ignorefirst"] = False
                continue
            egg = self.generate(row, settings)
            spam = map(escape, egg)
            spam = [PARAGRAPH_RE.sub(r"<br/>\1", v) for v in spam]
            dlg.textEdit.append(template % tuple(spam))
            articles_preview -= 1
            if not articles_preview:
                break
        dlg.exec_()
        
    def get_iterator(self, settings):
        if settings["fname"].lower().endswith(".json"):
            rc = json.load(codecs.open(settings["fname"], "r", "utf-8"))
        else:
            data = open(settings["fname"], "r").read()
            if settings["encoding"] == u"Автоопределение":
                encoded = autodecode(data, 1024)
            else:
                encoded = data.decode(settings["encoding"], "replace")
            egg = partial(csv.reader, StringIO(encoded.encode("utf-8","replace")))
            if settings["fielddelim"]:
                egg = partial(egg, delimiter=settings["fielddelim"].encode("utf-8"))
            if settings["textdelim"]:
                egg = partial(egg, quotechar=settings["textdelim"].encode("utf-8"))
            rc = egg()
        return rc
        
    def generate(self, row, settings):
        title = templater.generate(settings["title"], row)
        tags = templater.generate(settings["tags"], row)
        text = templater.generate(settings["text"], row)
        intro = templater.generate(settings["intro"], row)
        return (title, tags, text, intro)
        
    def make_settings(self, cd):
        settings = {
            "fname": unicode(cd.fname_le.text()),
            "encoding": unicode(cd.encoding_cb.currentText()),
            "fielddelim": unicode(cd.fielddelim_le.text()),
            "textdelim": unicode(cd.textdelim_le.text()),
            "ignorefirst": cd.ignorefirst_cb.checkState() & QtCore.Qt.Checked,
            "allowcat": cd.allowcat_cb.checkState() & QtCore.Qt.Checked,
            "title": unicode(cd.title_le.text()),
            "cattitle": unicode(cd.cattitle_le.text()),
            "tags": unicode(cd.tags_le.text()),
            "text": unicode(cd.text_le.text()),
            "intro": unicode(cd.intro_le.text()),
            "dicts": [unicode(cd.dicts_lw.item(i).text()) for i in range(cd.dicts_lw.count()) if cd.dicts_lw.item(i).checkState() & QtCore.Qt.Checked],
            "inwords": cd.inwords_cb.checkState() & QtCore.Qt.Checked,
        }
        return settings
        
if __name__ == '__main__':
    pass
