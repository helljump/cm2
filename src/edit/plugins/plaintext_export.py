#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
try:
    from plugtypes import IExportPlugin #@UnresolvedImport
except ImportError:
    IExportPlugin = object
from pytils.translit import slugify
from utils.qthelpers import MyProgressDialog, MyPath
import os
import codecs
from utils.formlayout import fedit

log = logging.getLogger(__name__)

class CancelException(Exception):
    pass

class PlainTextExport(IExportPlugin):

    ENCODINGS = [u"UTF-8",
                 ("utf-8", "UTF-8"),
                 ("cp1251", "Windows-1251"),
                 ("ascii", "ascii")]

    def run(self, tree, parent):

        p = MyPath(parent.current_save_path)
        datalist = [(u"Каталог:", p),
                    (u"Кодировка текстов", PlainTextExport.ENCODINGS),
                    (u"Расширение файлов", "txt"),
                    (u"Использовать пробелы вместо тире", False),
                ]
        rc = fedit(datalist, title=u"Экспорт текстовых файлов", parent=parent)
        if not rc:
            return

        self.export_dir = rc[0]
        self.encoding = rc[1]
        self.extension = rc[2]
        self.spacereplace = rc[3]

        if not self.export_dir:
            return
        parent.current_save_path = unicode(self.export_dir)
        self.export_dir = unicode(self.export_dir)#.encode("mbcs")
        self.tree = tree
        self.pd = MyProgressDialog(u"Экспорт", u"Запись статей", u"Отмена", 0,
                                   self.articles_count(tree), parent)
        self.pd.setFixedWidth(320)
        self.pd.show()
        try:
            self.export()
        except CancelException:
            pass
        self.pd.close()

    def articles_count(self, root):
        def _recurse(item):
            egg = 1
            for subitem in item.get_children():
                egg += _recurse(subitem)
            return egg
        return _recurse(root)

    def write_article(self, item):
        self.pd.set_text(u"Добавление статьи %s" % item.title)
        egg = "%s.%s" % (slugify(unicode(item.title)), self.extension)
        if self.spacereplace:
            egg = egg.replace("-"," ")
        fname = os.path.join(self.export_dir, egg)
        log.debug("fout: %s", fname)
        with codecs.open(fname, "wt", self.encoding, "replace") as fout:
            fout.write(item.title)
            fout.write('\n')
            fout.write(item.text)

    def export(self):
        def recurse_tree(tree):
            for item in tree.get_children():
                if self.pd.wasCanceled():
                    raise CancelException
                self.write_article(item)
                recurse_tree(item)
                self.pd.set_value(self.pd.value() + 1)
        recurse_tree(self.tree)
