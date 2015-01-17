# -*- coding: UTF-8 -*-

from plugtypes import IProcessPlugin
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from utils.qthelpers import MyProgressDialog, ToolBarWithPopup
import re
import os
from pytils.translit import slugify
import image_renamer_rc
import random
import shutil

class ImageRenamer(IProcessPlugin):

    img_tags_re = re.compile('(?imsu)<\s*(img|a) [^\>]*(src|href)\s*=\s*[\""\']?([^\""\'\s>]*)')
    deminus_re = re.compile('(?u)[\-]{2,}')
    images_exts = [".jpg",".gif",".png"]
    image_cache = []
    maxlen = 30
    
    def gen_new_name(self, title, ext):
        c = 1
        chop = self.deminus_re.sub("-",slugify(title[:self.maxlen])).strip("-")
        rc = "%s%s" % (chop, ext)
        while rc in self.image_cache:
            rc = "%s_%i%s" % (chop, c, ext)
            c += 1
        self.image_cache.append(rc)
        return rc
    
    def run(self, items, parent):
        pd = MyProgressDialog(u"Переименование изображений", u"Поиск в статьях", u"Отмена", 0, len(items), parent)
        pd.show()
        images = {}
        for item in items:
            for field in [item.article.text, getattr(item.article,"intro","")]:
                for url in self.img_tags_re.finditer(field):
                    egg = url.group(3)
                    fname, ext = os.path.splitext(egg)
                    if ext.lower() in self.images_exts:
                        images[egg] = item
            pd.inc_value()
            qApp.processEvents()
        pd.close()
        if len(images)==0:
            QMessageBox.warning(parent, u"Переименование изображений", 
                u"Изображений не найдено. Добавьте изображения в статьи.")
            return
            
        path = unicode(QFileDialog.getExistingDirectory(parent, u"Каталог изображений", parent.current_load_path))
        if path == "": 
            return
        parent.current_load_path = path

        dlg = Dialog(parent, path)
        dlg.setModal(True)
        dlg.set_data(images)
        dlg.show()
        
        pd = MyProgressDialog(u"Переименование изображений", u"Генерация новых имен", u"Отмена", 0, len(images), dlg)
        pd.show()
        
        self.image_cache = os.listdir(path)
        
        c = 0
        for row in dlg.get_data():
            row[Model.Column.FOUND] = os.path.isfile(os.path.join(path, row[Model.Column.NAME]))
            if row[Model.Column.FOUND]:
                c += 1
            fname, ext = os.path.splitext(row[Model.Column.NAME])
            newname = self.gen_new_name(row[Model.Column.TITLE], ext)
            row[Model.Column.NEWNAME] = newname
            
            pd.inc_value()
            qApp.processEvents()            
            if pd.wasCanceled():
                dlg.hide()
                return
                
        dlg.table.model().updateAll()
        
        if c==0 or c==len(dlg.get_data()):
            dlg.notfound_tb.setDisabled(True)
            
        if c==0:
            pd.close()
            QMessageBox.warning(dlg, u"Переименование изображений", 
                u"Файлов ненайдено. Добавьте изображения в каталог.")
            dlg.hide()
            return
        
        pd.close()
        dlg.exec_()

class Model(QAbstractTableModel):

    class Column(object): (NAME, NEWNAME, PATH, TITLE, FOUND, ARTICLE) = range(6)

    def __init__(self, parent):
        QAbstractTableModel.__init__(self)
        self.parent = parent
        self.labels = [u"Имя файла", u"Новое имя", u"Путь", u"Страница"]
        self._cache = []
        self.found_icon = QIcon(":/images/tick.png")
        self.notfound_icon = QIcon(":/images/cancel.png")
        
    def rowCount(self, parent):
        return len(self._cache)
        
    def columnCount(self, parent):
        return len(self.labels)
        
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.DecorationRole:
            return QVariant()
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            value = self._cache[row][column]
        elif role == Qt.DecorationRole:
            if column==0:
                value = self.found_icon if self._cache[row][Model.Column.FOUND] else self.notfound_icon
            else:
                value = None
        return QVariant(value)
        
    def data2(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        value = ''
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            value = self._cache[row][col]
        return QVariant(value)
        
    def appendRow(self, data):
        self._cache.append(data)
        
    def getData(self):
        return self._cache
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section + 1)
        return QVariant()
        
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def updateAll(self):
        ifrom = self.createIndex(0, 0)
        ito = self.createIndex(len(self._cache), self.columnCount(self))
        self.dataChanged.emit(ifrom, ito)
        
class Dialog(QDialog):

    def __init__(self, parent, path):
        self.path = path
        QWidget.__init__(self, parent)
        self.setWindowTitle(u"Переименование изображений")
        self.resize(800, 600)
        layout = QGridLayout(self)
        tb = ToolBarWithPopup(self, Qt.ToolButtonTextBesideIcon)
        self.found_tb = tb.addAction(QIcon(":/images/cog_go.png"), u"Переименовать", self.run)        
        self.notfound_tb = tb.addAction(QIcon(":/images/no_image.png"), u"Отсутствующие случайными", self.run_noimage)        
        layout.addWidget(tb, 0, 0, 1, 1)
                
        self.table = QTableView(self)
        self.table.verticalHeader().setDefaultSectionSize(self.table.verticalHeader().fontMetrics().height() + 4)
        self.table.setAlternatingRowColors(True)
        model = Model(self.table)
        
        self.table.setModel(model)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table, 1, 0, 1, 1)
        
        bbox = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal, self)
        bbox.rejected.connect(self.reject)
        layout.addWidget(bbox, 2, 0, 1, 1)
        
        self.errmsg = QErrorMessage(self)
        self.errmsg.setModal(True)
            
    def get_data(self):
        return self.table.model().getData()
            
    def set_data(self, data):
        model = self.table.model()
        for url, article in data.items():
            egg = os.path.split(url)
            model.appendRow([egg[1], u"", egg[0], article.title, False, article])
        
    def show_error(self, err):
        self.pd.hide()
        self.errmsg.setWindowTitle(u"Ошибка")
        self.errmsg.showMessage(err)
    
    def run_noimage(self):
        cnt = self.renamer()
        data = self.table.model().getData()
        pd = MyProgressDialog(u"Переименование изображений", u"Отсутствующие случайными", u"Отмена", 0, len(data), self)
        newnames = [row[Model.Column.NEWNAME] for row in data if row[Model.Column.FOUND]]
        added = 0
        for row in data:
            if not row[Model.Column.FOUND]:
                real_old = row[Model.Column.NAME]
                old = random.choice(newnames)
                new_ = row[Model.Column.NEWNAME]
                pd.set_text(u"%s » %s" % (old, new_))
                article = row[Model.Column.ARTICLE].article
                article.text = article.text.replace(real_old, new_)
                if hasattr(article, "intro"):
                    article.intro = article.intro.replace(real_old, new_)                
                shutil.copy(os.path.join(self.path, old), os.path.join(self.path, new_))
                added += 1
            pd.inc_value()
            qApp.processEvents()            
            if pd.wasCanceled():
                break                        
        pd.close()
        QMessageBox.information(self, u"Переименование изображений", 
            u"Файлов переименовано: %i\nФайлов добавлено: %i" % (cnt, added))
        self.hide()

    def renamer(self):
        data = self.table.model().getData()
        pd = MyProgressDialog(u"Переименование изображений", u"Переименование", u"Отмена", 0, len(data), self)
        cnt = 0
        for row in data:
            if row[Model.Column.FOUND]:
                old = row[Model.Column.NAME]
                new_ = row[Model.Column.NEWNAME]
                pd.set_text(u"%s » %s" % (old, new_))
                article = row[Model.Column.ARTICLE].article
                article.text = article.text.replace(old, new_)
                if hasattr(article, "intro"):
                    article.intro = article.intro.replace(old, new_)                
                os.rename(os.path.join(self.path, old), os.path.join(self.path, new_))
                cnt += 1
            pd.inc_value()
            qApp.processEvents()            
            if pd.wasCanceled():
                break                        
        pd.close()
        return cnt
            
    def run(self):
        cnt = self.renamer()
        QMessageBox.information(self, u"Переименование изображений", u"Файлов переименовано: %i" % cnt)
        self.hide()

if __name__ == "__main__":
    pass
