#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from plugtypes import IImportPlugin
from utils.qthelpers import MyProgressDialog, MyFile, MyString
from PyQt4 import QtCore, QtGui, Qsci
from dialog2 import Ui_Dialog
import os
from utils.article import Article
from utils.formlayout import fedit
from utils.tidy import autodecode
from StringIO import StringIO
import csv
from functools import partial
from utils.paths import pluginpath
import pickle
import jext
import help
import json
import codecs

LOG = logging.getLogger(__name__)
DEC = lambda x: x.decode("utf-8","replace")
BASESPATH = os.path.join(*__file__.split(os.path.sep)[-3:-1])

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


def replace_control(control, layout, parent, position):
    egg = control.toPlainText()
    spam = control.sizePolicy()
    layout.removeWidget(control)
    control.setParent(None)
    newcontrol = HtmlEdit(parent)
    newcontrol.setText(egg)
    newcontrol.setSizePolicy(spam)
    layout.addWidget(newcontrol, *position)
    return newcontrol


class ConfigDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.text_le = replace_control(self.text_le, self.gridLayout_3, self.frame, (1, 0, 1, 1))
        self.intro_le = replace_control(self.intro_le, self.gridLayout_5, self.frame_2, (1, 0, 1, 1))
        self.selectfile_bp.clicked.connect(self.set_fname)
        self.buttonBox.helpRequested.connect(self.show_help)
        #self.buttonBox.clicked.connect(self.clicked)

    def clicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QtGui.QDialogButtonBox.ResetRole:
            tmp = Ui_Dialog()
            tmp.retranslateUi(None)
            self.text_le.setText(tmp.text_le.text())

    def set_fname(self):
        egg = unicode(self.fname_le.text())
        path = os.path.split(egg)[0]
        fname = QtGui.QFileDialog.getOpenFileName(self, u"Открыть файл...", path,
            "Comma Separated Values(*.csv);;JavaScript Object Notation(*.json)")
        if not fname:
            return
        self.fname_le.setText(unicode(fname))

    def show_help(self):
        dlg = QtGui.QDialog(self)
        ui = help.Ui_Dialog()
        ui.setupUi(dlg)
        dlg.exec_()


class CancelException(Exception):
    pass


class Plugin(IImportPlugin):

    configfile = os.path.join(pluginpath, "csv_import2_pro.pkl")

    def run(self, parent):
        cd = ConfigDialog(parent)
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
            cd.intro_le.setText(settings["intro"])
            cd.cattitle_le.setText(settings["cattitle"])
        except IOError:
            LOG.debug("use defaults params")

        rc = cd.exec_()
        if not rc:
            return

        #get fields
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
            "intro": unicode(cd.intro_le.text())
        }
        pickle.dump(settings, open(Plugin.configfile, "wt"))
        parent.current_load_path = os.path.split(settings["fname"])[0] #save path

        jext.fromdir_cache = None
        env = jext.get_env()

        #-----------------------------------------

        pd = MyProgressDialog(u"Импорт", u"Открытие файла", u"Отмена", 0, 0, parent)
        pd.show()
        try:
            pd.set_text(u"Читаем файл")
            pd.set_text(u"Генерируем статьи")
            tmproot = root = Article()

            if settings["fname"].endswith(".json"):
                data = json.load(codecs.open(settings["fname"], "r", "utf-8"))
                for row in data:

                    intro_env = env.from_string(settings["intro"])
                    text_env = env.from_string(settings["text"])
                    tags_env = env.from_string(settings["tags"])
                    title_env = env.from_string(settings["title"])
                    cattitle_env = env.from_string(settings["cattitle"])

                    for i in range(len(row)):
                        if type(row[i]) == int:
                            row[i] = str(row[i])
                    if settings["ignorefirst"]:
                        settings["ignorefirst"] = False
                        continue
                    if settings["allowcat"] and len(row) == 1:
                        egg = cattitle_env.render(data=row)
                        tmproot = Article(egg)
                        root.add_child(tmproot)
                        pd.set_text(u"Добавили категорию: %s" % row[0])
                        LOG.debug("add category %s", tmproot)
                    else:
                        pd.set_text(u"Добавили материал: %s" % row[0])
                        title = title_env.render(data=row)
                        text = text_env.render(data=row)
                        intro = intro_env.render(data=row)
                        tags = [tags_env.render(data=row)]
                        art = Article(title, text, tags)
                        art.intro = intro
                        tmproot.add_child(art)
                    QtGui.qApp.processEvents()
                    if pd.wasCanceled():
                        raise CancelException
            else:
                data = open(settings["fname"], "rb").read()
                if settings["encoding"] == u"Автоопределение":
                    encoded = autodecode(data, 1024)
                else:
                    encoded = data.decode(settings["encoding"], "replace")
                eggfunc = partial(csv.reader, StringIO(encoded.encode("utf-8", "replace")))
                if settings["fielddelim"]:
                    eggfunc = partial(eggfunc, delimiter=settings["fielddelim"].encode("utf-8", "replace"))
                if settings["textdelim"]:
                    eggfunc = partial(eggfunc, quotechar=settings["textdelim"].encode("utf-8", "replace"))

                c = 0

                for row in eggfunc():

                    c += 1

                    intro_env = env.from_string(settings["intro"])
                    text_env = env.from_string(settings["text"])
                    tags_env = env.from_string(settings["tags"])
                    title_env = env.from_string(settings["title"])
                    cattitle_env = env.from_string(settings["cattitle"])

                    if settings["ignorefirst"]:
                        settings["ignorefirst"] = False
                        continue
                    # row = filter(lambda x: len(x)>0, row)
                    row = [unicode(i, "utf-8") for i in row]
                    if settings["allowcat"] and len(row) == 1:
                        egg = cattitle_env.render(data=row)
                        tmproot = Article(egg)
                        root.add_child(tmproot)
                        pd.set_text(u"Добавили категорию: %s" % row[0])
                        LOG.debug("add category %s", tmproot)
                    else:
                        pd.set_text(u"Добавили материал: %s" % row[0])
                        title = title_env.render(data=row)
                        text = text_env.render(data=row)

                        #print text.encode("utf-8")

                        intro = intro_env.render(data=row)
                        tags = [tags_env.render(data=row)]
                        art = Article(title, text, tags)
                        art.intro = intro
                        tmproot.add_child(art)
                    QtGui.qApp.processEvents()
                    if pd.wasCanceled():
                        raise CancelException

        except (CancelException, jext.JinjaException):
            pass
        pd.close()
        return root

if __name__ == '__main__':
    pass
