#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snöa

from logging import debug, exception
import traceback
import codecs
from pytils.translit import slugify
import os
import random
import sys
from datetime import date, datetime

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread
from utils.qthelpers import MyDirEdit
from utils.tidy import encode_html_entities
import shelve
import staticres #@UnusedImport

from edit.htmledit import HtmlEdit

ul_menu = u"""<ul>%s</ul>"""
li_menu = u"""<li><a href="%(url)s" title="%(title)s">%(title)s</a>%(intro)s</li>"""
li_articles = u"""<li><a href="%(url)s" title="%(title)s">%(title)s</a></li>"""
page_div = u"""<div align=\"center\">%s</div>"""
page_link = u"""<a href="%(url)s">%(title)i</a>"""
page_delim = " | "
main_page_title = u"Главная страница"

encodings = {"utf-8":"utf8", "windows-1251":"cp1251"}

from utils.paths import CONFIGFILE

class ExportThread(QThread):
    def __init__(self, tree, fname, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.tree = tree
        self.fname = unicode(fname)
        self.pd = progressdialog
        self.parent = parent
    def run(self):
        olddir = os.getcwd()
        try:
            self.write()
        except IOError, err:
            exception("export error")
            if err[0] == 2:
                self.error = u"Не удалось создать файл"
            else:
                raise
        except:
            exception("export error")
            self.error = traceback.format_exc()
        os.chdir(olddir)
    def stop(self):
        debug("terminate")
        self.terminate()
        debug("wait")
        self.wait()

class ExportDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Статичный сайт")
        self.setWindowFlags(QtCore.Qt.Window)
        self.resize(800, 600)   
        mainlayout = QtGui.QGridLayout(self)
        fields_l = QtGui.QHBoxLayout()

        fields_l.addWidget(QtGui.QLabel(u"Первый пункт", self))
        self.mainpage_le = QtGui.QLineEdit(self)
        fields_l.addWidget(self.mainpage_le)

        fields_l.addWidget(QtGui.QLabel(u"На странице", self))
        self.onpage_sb = QtGui.QSpinBox(self)
        self.onpage_sb.setSuffix(u" статей")
        fields_l.addWidget(self.onpage_sb)

        fields_l.addWidget(QtGui.QLabel(u"Случайных", self))
        self.random_sb = QtGui.QSpinBox(self)
        self.random_sb.setSuffix(u" статей")
        fields_l.addWidget(self.random_sb)
        
        fields_l.addWidget(QtGui.QLabel(u"Имя(не более)", self))
        self.maxlen_sb = QtGui.QSpinBox(self)
        self.maxlen_sb.setSuffix(u" символов")
        self.maxlen_sb.setRange(5, 1000)
        fields_l.addWidget(self.maxlen_sb)
        
        mainlayout.addLayout(fields_l, 0, 0)

        # fields_l = QtGui.QHBoxLayout()
        # fields_l.addWidget( QtGui.QLabel(u"Заголовок для главной страницы",self) )
        # self.mainpagetitle_le = QtGui.QLineEdit(self)
        # fields_l.addWidget( self.mainpagetitle_le )
        # mainlayout.addLayout(fields_l, 1, 0)

        t = QtGui.QHBoxLayout()        
        t.addWidget(QtGui.QLabel(u"Главная страница", self))
        self.mainpagetitle_le = QtGui.QLineEdit(self)
        t.addWidget(self.mainpagetitle_le)
        self.encoding_cb = QtGui.QComboBox(self)
        for k, v in encodings.items():
            self.encoding_cb.addItem(k, v)
        t.addWidget(self.encoding_cb)
        mainlayout.addLayout(t, 1, 0)

        templates_l = QtGui.QHBoxLayout()
        templates_l.addWidget(QtGui.QLabel(u"Вставить шаблон", self), 0)
        templates_tb = QtGui.QToolBar(self)
        templates_l.addWidget(templates_tb, 1)
        mainlayout.addLayout(templates_l, 2, 0)

        templates_tb.addAction(u"Заголовок", self.insert_template_title)
        templates_tb.addAction(u"Меню", self.insert_template_menu)
        templates_tb.addAction(u"Содержимое", self.insert_template_content)
        templates_tb.addAction(u"Случайные", self.insert_template_random)
        templates_tb.addAction(u"Кодировка", self.insert_template_encoding)
        
        templates_tb.addAction(u"Описание", self.insert_template_description)
        templates_tb.addAction(u"Ключевые слова", self.insert_template_keywords)
        
        '''
        templates = [
            (u"Заголовок","{title}"),
            (u"Меню","{menu}"),
            (u"Содержимое","{content}"),
            (u"Случайные","{random}")
        ]
        for item in templates:
            egg = QtGui.QAction(item[0], self.templates_tb)
            self.connect(egg, QtCore.SIGNAL('triggered()'),  lambda val=item[1]: self.insert_template(val))
            self.templates_tb.addAction(egg)
        '''

        self.textEdit = HtmlEdit(self)
        mainlayout.addWidget(self.textEdit, 3, 0)
                
        path_l = QtGui.QHBoxLayout()
        path_l.addWidget(QtGui.QLabel(u"Каталог", self), 0)
        self.path = MyDirEdit(self)
        path_l.addWidget(self.path, 1)
        mainlayout.addLayout(path_l, 4, 0)

        bbar = QtGui.QDialogButtonBox(self)
        b = bbar.addButton(u"Генерировать", QtGui.QDialogButtonBox.ActionRole)
        b.clicked.connect(self.generate)
        b = bbar.addButton(u"Закрыть", QtGui.QDialogButtonBox.ActionRole)
        b.clicked.connect(self.cancel)
        mainlayout.addWidget(bbar, 5, 0)
        
    def insert_template_title(self):
        self.insert_template("{title}")
    def insert_template_menu(self):
        self.insert_template("{menu}")
    def insert_template_content(self):
        self.insert_template("{content}")
    def insert_template_random(self):
        self.insert_template("{random}")
    def insert_template_encoding(self):
        self.insert_template("{encoding}")
        
    def insert_template_description(self):
        self.insert_template("{description}")
    def insert_template_keywords(self):
        self.insert_template("{keywords}")
        
    def insert_template(self, text):
        self.textEdit.insert(text)

    def generate(self):
        self.setResult(1)
        self.accept()

    def cancel(self):
        self.reject()

cmpdate = lambda x, y: cmp(x['date'], y['date'])
cmppost = lambda x, y: cmp(x['post'], y['post'])

class Export(ExportThread):
    
    template = unicode(QtCore.QResource(":/static/index.html").data(), 'utf8')
    random_count = 5
    maxlen_count = 80
    onpage_count = 20
    main_page_menu = u"Главная"

    def config(self):
        dlg = ExportDialog(self.parent)
        settings = shelve.open(CONFIGFILE)
        config = settings.get("ExportStaticDialog", {})
        dlg.random_sb.setValue(config.get("random", self.random_count))
        dlg.maxlen_sb.setValue(config.get("maxlen", self.maxlen_count))
        dlg.onpage_sb.setValue(config.get("onpage", self.onpage_count))
        dlg.mainpage_le.setText(config.get("mainpage", self.main_page_menu))
        dlg.mainpagetitle_le.setText(config.get("mainpagetitle", main_page_title))
        dlg.textEdit.setText(config.get("template", self.template))
        dlg.path.setText(config.get("fname", self.fname))
        egg = dlg.encoding_cb.findText(config.get("encoding", "utf-8"))
        if egg != -1:
            dlg.encoding_cb.setCurrentIndex(egg)
        settings.close()
        if not dlg.exec_():
            return False
        settings = shelve.open(CONFIGFILE)
        self.params = {}
        self.params["random"] = int(dlg.random_sb.value())
        self.params["maxlen"] = int(dlg.maxlen_sb.value())
        self.params["onpage"] = int(dlg.onpage_sb.value())
        self.params["mainpage"] = unicode(dlg.mainpage_le.text())
        self.params["mainpagetitle"] = unicode(dlg.mainpagetitle_le.text())
        self.params["fname"] = unicode(dlg.path.text())
        self.params["template"] = unicode(dlg.textEdit.text())
        self.params["encoding"] = unicode(dlg.encoding_cb.currentText())
        settings["ExportStaticDialog"] = self.params
        settings.close()
        return True

    def _make_fname(self, title):
        egg = slugify(title)[:self.params["maxlen"]]
        return egg

    def _recurse(self, cat):

        flatlist = self.flatter(cat, cat is self.tree)

        egg = [ li_menu % {"url":"/" + self._make_fname(item.title) + "/", #narod fix
            "title":encode_html_entities(item.title), "intro":""} for item in self.tree.get_children() ]
                    
        egg.insert(0, li_menu % {"url":"/", "title":self.params["mainpage"], "intro":""})
        menu = '\n'.join(egg)

        title = getattr(cat, 'title', u'')
        content = getattr(cat, 'text', u'')

        flatlist.sort(cmp=cmpdate, reverse=True)
        
        if cat is self.tree:
            flatlist = [item for item in flatlist if item['post']]
            # title=main_page_title
            title = self.params["mainpagetitle"]
        else:
            flatlist.sort(cmp=cmppost, reverse=True)
        
        params = {"title":title,
            "content":content,
            "menu": ul_menu % menu,
            "encoding": self.tenc}
            
        self.write_index_by_pages(params, flatlist)
        
        for subitem in cat.get_children():
            if self.pd:
                self.pd.set_text(u"Сохраняем %s" % subitem.title)
            
            if subitem.get_children():#category
                catname = self._make_fname(subitem.title)
                if not os.path.isdir(catname):
                    os.mkdir(catname)
                olddir = os.getcwd()
                os.chdir(catname)
                self._recurse(subitem)
                os.chdir(olddir)
                
            else: #article
                title = getattr(subitem, 'title', u'')
                content = getattr(subitem, 'text', u'')
                tags = getattr(subitem, 'tags', [])
                fout = codecs.open("%s.html" % self._make_fname(title), "wt", self.fenc, "replace")
                params = {"title":title,
                    "content":content,
                    "menu": ul_menu % menu,
                    "random": self._random_generator(flatlist),
                    "encoding": self.tenc,
                    "description": title,
                    "keywords": ", ".join(tags)}
                fout.write(self.templater(params))
                fout.close()
        
    def write(self):
        self.tenc = self.params['encoding']
        self.fenc = encodings[self.tenc]
        curdir = os.getcwd()
        os.chdir(self.params['fname'])
        if self.pd:
            self.pd.set_text(u"Запись файла")
        self._recurse(self.tree)            
        os.chdir(curdir)

    def templater(self, params):
        egg = self.params["template"]
        for param, val in params.items():
            egg = egg.replace("{%s}" % param, val)
        return egg

    def _recurse2(self, item, parent, scan_recurse):
        sublist = []
        for subitem in item.children:
            if scan_recurse:
                egg = "%s/%s" % (parent, self._make_fname(subitem.title))
            else:
                egg = self._make_fname(subitem.title)
            post = not subitem.children
            intro = getattr(subitem, 'intro', u'')
            if intro:
                intro = "<br/>\n%s" % intro
            params = {"title":encode_html_entities(subitem.title),
                "url":egg, "date":subitem.date,
                "intro":intro, "post":post, "tags":subitem.tags}
            if not subitem.children:
                params['url'] += ".html"
            sublist.append(params)
            if scan_recurse:
                spam = self._recurse2(subitem, egg, scan_recurse)
                sublist.extend(spam)
        return sublist

    def flatter(self, root, scan_recurse):
        flatlist = self._recurse2(root, "", scan_recurse)
        debug("flatter size: %i", len(flatlist))
        return flatlist
        
    def _random_generator(self, flatlist):
        random.shuffle(flatlist)
        random_articles = (li_articles % item for item in flatlist[:self.params["random"]])
        egg = ul_menu % "\n".join(random_articles)
        return egg

    def write_index_by_pages(self, params, items):
        onpage = self.params["onpage"]
        orig_content = params['content']
        pages, remainder = divmod(len(items), onpage)
        if remainder > 0:
            pages += 1
        if not pages:
            pages = 1
        files = ["index-%i.html" % (i + 1) for i in range(pages)]
        files[0] = "index.html"
        links = [ page_link % {"url":files[i], "title":(i + 1)} for i in range(pages) ]
        if pages > 1:
            pager = page_div % page_delim.join(links)
        else:
            pager = ""
        
        for i in range(pages):
            start = i * onpage
            content = ul_menu % "\n".join(
                [li_menu % item for item in items[start:start + onpage]]
            )
            params['content'] = "%s%s%s" % (params['content'], content, pager)
            params['random'] = self._random_generator(items[:])
            
            keywords = []
            descriptions = []
            for item in items[start:start + onpage]:
                keywords += item['tags']
                descriptions.append(item['title'])
            keywords = set(keywords)
            params["description"] = ", ".join(descriptions).replace("\""," ")
            params["keywords"] = ", ".join(keywords)
            
            fname = files[i]
            
            fout = codecs.open(fname, "wt", self.fenc, "replace")
            fout.write(self.templater(params))
            fout.close()
            
            params['content'] = orig_content

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    #tree = cPickle.load(open("..\\autoload.prt","rb"))
    export = Export(None, "d:\\work\\promidol\\test\\static1")
    if export.config():
        export.run()
