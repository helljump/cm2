#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import logging
from plugtypes import IExportPlugin
from utils.qthelpers import MyProgressDialog
from PyQt4.QtGui import QFileDialog
from pytils.translit import slugify
import os
import codecs
from time import mktime


log = logging.getLogger(__name__)

#id title datetime(1352757212) user intro full category commentperm commantcount reviews articleslug catslug


class CancelException(Exception):
    pass


class Plugin(IExportPlugin):

    def run(self, tree, parent):

        fname = QFileDialog.getSaveFileName(parent, u"Экспорт", parent.current_save_path,
            u"Kandidat CMS flatfile(*.txt)")
        if fname == "":
            return
        fname = unicode(fname)
        parent.current_save_path = os.path.split(fname)[0]

        self.pd = MyProgressDialog(u"Экспорт", u"Запись статей", u"Отмена", 0, 0, parent)
        self.pd.show()
        try:
            self.export(tree, fname)
        except CancelException:
            pass
        self.pd.close()

    def export(self, tree, fname):

        current_cat = ""
        self.names = []
        cid = 0

        if os.path.isfile(fname):
            fout = codecs.open(fname, "r+", "utf-8", "replace")
            for row in fout.readlines():
                cells = row.split('\t')
                egg = int(cells[0])
                if cid < egg:
                    cid = egg
            fout.seek(0, os.SEEK_END)
        else:
            fout = codecs.open(fname, "w", "utf-8", "replace")

        for cat in tree.get_children():
            if current_cat != cat.title:
                current_cat = cat.title

            for article in self.flatten(cat):
                cid += 1
                if not hasattr(article, "intro"):
                    article.intro = ""
                artslug = self.generate_slug(article.title)
                intro = self.escape(article.intro)
                text = self.escape(article.text)
                if not intro:
                    intro = text
                    text = ""
                seconds = int(mktime(article.date.timetuple()))
                row = [str(cid), article.title, str(seconds), u'Админ', intro, text, current_cat,
                    '1', '0', '0', artslug, slugify(current_cat), '\n']
                fout.write('\t'.join(row))

        fout.close()

    def escape(self, text):
        return text.replace('\t', '    ').replace('\r\n', '<br />').replace('\r', '<br />').replace('\n', '<br />')

    def generate_slug(self, name):
        egg = orig_egg = slugify(name)
        cnt = 1
        while egg in self.names:
            egg = "%s_%i" % (orig_egg, cnt)
            cnt += 1
        newname = egg.replace("-", "_")
        self.names.append(newname)
        return newname

    def flatten(self, item):
        children = []
        for subitem in item.get_children():
            children.append(subitem)
            children += self.flatten(subitem)
        return children
