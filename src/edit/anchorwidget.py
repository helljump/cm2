#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QModelIndex, QVariant, QThread, pyqtSlot, pyqtSignal
from commands import EditArticleCommand
import codecs
import icons
from utils.misc import replace_by_spans
from utils.qthelpers import MyProgressDialog, ToolBarWithPopup
from anchorwidget_dialog import Ui_Dialog
from utils.paths import CONFIGFILE
import shelve
import esm
import re
import random
import logging
import math

log = logging.getLogger(__name__)

class SetupDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.save_settings)
        self.load_settings()
        
    def load_settings(self):
        egg = shelve.open(CONFIGFILE)
        settings = egg.get(str(self.__class__), {})
        egg.close()
        self.perarticle_sb.setValue(settings.get("perarticle",3))
        self.perchars_sb.setValue(settings.get("perchars",1))
        if settings.get("strategy", True):
            pass
        else:
            self.perchars_rb.setChecked(True)
            self.perarticle_sb.setDisabled(True)
            self.perchars_sb.setDisabled(False)

    def save_settings(self):
        egg = shelve.open(CONFIGFILE)
        egg[str(self.__class__)] = {
            "perarticle":self.perarticle_sb.value(),
            "perchars":self.perchars_sb.value(),
            "strategy":self.perarticle_rb.isChecked(),
        }
        egg.close()
        self.setResult(1)
        self.hide()
            
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self)
        self.parent = parent
        self.labels = [u"Анкор",u"URL"]
        self.cache = [
            #[u"Евлампий Расщепо","http://evlampy.ru"],
            #[u"Пороки","http://poroki.ru"],
        ]
    def rowCount(self, parent):
        return len(self.cache)
    def columnCount(self, parent):
        return len(self.labels)
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()
        value = ''
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            value = self.cache[row][col]
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            value = self.cache[row][col]
        return QVariant(value)
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(str(section + 1))
        return QVariant()
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
    def setData(self, index, data, role):
        try:
            row = index.row()
            col = index.column()
            self.cache[row][col] = unicode(data.toString())
            return True
        except:
            return False
    def sort(self, col, order):
        reverse = order != Qt.AscendingOrder
        self.cache.sort(reverse=reverse)
        ifrom = self.createIndex(0, 0)
        ito = self.createIndex(self.rowCount(None), self.columnCount(None))
        self.dataChanged.emit(ifrom, ito)
    def insertRows(self, pos, rows, index=QModelIndex()):
        self.beginInsertRows(index, pos, pos + rows - 1)
        for row in range(rows):
            self.cache.insert(pos, ["", ""])
        self.endInsertRows()
        return True
    def removeRows(self, pos, rows, index=QModelIndex()):
        self.beginRemoveRows(index, pos, pos + rows - 1);
        for i in range(rows):
            self.cache.pop(pos)
        self.endRemoveRows()
        return True

class AnchorWidget(QtGui.QWidget):

    WORDDELIM = re.compile("(<a.+?/a>|</{0,1}[^>]*?>)", re.M | re.I)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.mainwindow = parent.parent()
        gridLayout = QtGui.QGridLayout(self)
        
        self.table = QtGui.QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setDefaultSectionSize(self.table.verticalHeader().fontMetrics().height() + 4)
        self.table.setAlternatingRowColors(True)
        model = TableModel(self.table)
        self.table.setModel(model)
        
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)

        gridLayout.addWidget(self.table, 1, 0, 1, 1)
        gridLayout.setContentsMargins(0, 0, 0, 0)

        tb = QtGui.QToolBar(self)
        tb.addAction(QtGui.QIcon(":/ico/img/cog_go.png"), u"Обработка", self.process)
        tb.addSeparator()
        tb.addAction(QtGui.QIcon(":/ico/img/add1.png"), u"Добавить", self.add_item)
        tb.addAction(QtGui.QIcon(":/ico/img/delete1.png"), u"Удалить", self.del_item)
        tb.addAction(QtGui.QIcon(":/ico/img/document_import.png"), u"Импорт", self.import_from_file)
        gridLayout.addWidget(tb, 0, 0, 1, 1)
        
    def set_list(self, rows):
        self.clear()
        model = self.table.model()
        model.beginInsertRows(QModelIndex(), 0, len(rows)-1)
        model.cache = rows
        model.endInsertRows()
        model.reset()

    def clear(self):
        model = self.table.model()
        rows = model.rowCount(None)
        model.removeRows(0, rows)
        
    def get_list(self):
        model = self.table.model()
        return model.cache
        
    def add_item(self, anchor="", url=""):
        try:
            if self.mainwindow.textEdit.hasFocus():
                w = self.mainwindow.textEdit
            if self.mainwindow.introTextEdit.hasFocus():
                w = self.mainwindow.introTextEdit
            anchor = unicode(w.selectedText())
        except (AttributeError, UnboundLocalError):
            pass #no parent
        model = self.table.model()
        row = model.rowCount(None)
        model.insertRows(row, 1)
        index = model.createIndex(row, 0)
        model.setData(index, QVariant(anchor), Qt.DisplayRole)
        index = model.createIndex(row, 1)
        model.setData(index, QVariant(url), Qt.DisplayRole)
        
    def del_item(self):
        rows = [ndx.row() for ndx in self.table.selectedIndexes() if ndx.column() == 0]
        if len(rows)>1:
            rc = QtGui.QMessageBox.question(self, u"Удаление", u"Удалить указанные строки?", 
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if rc == QtGui.QMessageBox.No:
                return
        rows.sort(reverse=True)
        model = self.table.model()
        for row in rows:
            model.removeRows(row, 1)
        
    def import_from_file(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u"Импорт...", 
            self.mainwindow.current_load_path, "Links file (*.txt)")
        if not fileName:
            return
        fileName = unicode(fileName)
        model = self.table.model()
        rows = [row.strip() for row in codecs.open(fileName, "r", "utf-8", "replace")]
        rows_in_model = model.rowCount(None)
        if len(rows)>rows_in_model:
            model.insertRows(rows_in_model, len(rows)-rows_in_model)
        for i in range(len(rows)):
            index = model.createIndex(i, 1)
            model.setData(index, QVariant(rows[i]), Qt.DisplayRole)
        ifrom = model.createIndex(0, 1)
        ito = model.createIndex(len(rows), 1)
        model.dataChanged.emit(ifrom, ito)
            
    def process(self):
        model = self.table.model()
        arts = self.mainwindow.get_selected_items()                
        dlg = SetupDialog(self.mainwindow)
        if not dlg.exec_():
            return
        perarticle = dlg.perarticle_sb.value()
        perchars = dlg.perchars_sb.value()
        strategy = dlg.perarticle_rb.isChecked()
        
        self.p = QtGui.QProgressDialog(u"Вставка ссылок...", u"Отмена", 1, len(arts), self)
        self.th = Thread(arts, self, perarticle=perarticle, perchars=perchars, strategy=strategy, anchors=model.cache)
        
        self.p.canceled.connect(self.th.cancel)
        self.th.increment.connect(self.incProgress)
        self.th.done.connect(self.doneProgress)
        
        #self.p.show()
        
        self.mainwindow.undo_stack.beginMacro(u"Вставка ссылок по анкорам")
        self.th.start()  
 
    def doneProgress(self, links):
        self.mainwindow.undo_stack.endMacro()
        self.mainwindow._reload_current_item()
        log.debug("done progress")
        QtGui.QMessageBox.information(self, u"Вставка ссылок", u"Ссылок добавлено: %i" % links)
 
    def incProgress(self, item, newtext):
        self.p.setValue(self.p.value()+1)
        #log.debug("inc progress %s", item)
        if newtext:
            command = EditArticleCommand(self.mainwindow.treeWidget.tree, item, {"text":unicode(newtext)})
            self.mainwindow.undo_stack.push(command)
        
class Thread(QThread):

    done = pyqtSignal(int)
    increment = pyqtSignal('PyQt_PyObject', unicode)

    def __init__(self, articles, parent, **kwargs):
        QtCore.QThread.__init__(self, parent)
        self.canceled = False
        self.articles = articles
        self.kwargs = kwargs
        
    @pyqtSlot()
    def cancel(self):
        self.canceled = True
      
    def run(self):
        try:
                
            actree = esm.Index()
            acdict = dict()
            for k,v in self.kwargs["anchors"]:
                en_lo_k = k.lower().encode("utf-8","replace")
                en_k = k.encode("utf-8","replace")
                acdict[en_lo_k] = {"url":v.encode("utf-8","replace")}
                actree.enter(en_lo_k)
            actree.fix()
            
            matches = 0
                       
            #log.debug("articles %i", len(self.articles))
                       
            for item in self.articles:        
            
                #log.debug("begin %s", item)
        
                if self.canceled:
                    break
        
                en_text = item.article.text.encode("utf-8","replace")
                en_lo_text = item.article.text.lower().encode("utf-8","replace")
                
                fragments = AnchorWidget.WORDDELIM.split( en_lo_text )
                current_position = 0
                
                founded = []
                
                for fragment in fragments:
                    
                    fraglen = len(fragment)

                    if (len( fragment.strip()) == 0
                        or fragment[0] == "<" #tags
                        or fragment[:2] == "{{" ): #templates
                        current_position += fraglen
                        continue

                    spans = actree.query(fragment)
                    """
                    query возвращает список кортежей в виде
                    [
                        ((38, 69), '\xd0\xb5\xd0\xb2\xd0\xbb\xd0\xb0\xd0\xbc\xd0\xbf\xd0\xb8\xd0\xb9 \xd1\x80\xd0\xb0\xd1\x81\xd1\x89\xd0\xb5\xd0\xbf\xd0\xbe'), 
                        ((162, 174), '\xd0\xbf\xd0\xbe\xd1\x80\xd0\xbe\xd0\xba\xd0\xb8'), 
                        ((204, 216), '\xd0\xbf\xd0\xbe\xd1\x80\xd0\xbe\xd0\xba\xd0\xb8')
                    ]
                    """
                    
                    # добавили только целые слова
                    for (span, word) in spans:
                        start = span[0]
                        end = span[1]
                        if ((start > 0 and ord(fragment[start-1])>64) or
                            (end < fraglen and ord(fragment[end])>64)):                            
                            continue #not space                  

                        #print "borders", fragment[start-1], fragment[end]
                            
                        acdict[word]["word"] = en_text[current_position+start:current_position+end]
                        founded.append({
                            "spans":(start+current_position, end+current_position),
                            "word":'<a href="%(url)s">%(word)s</a>' % acdict[word]
                        })
                    current_position += fraglen

                if not founded:
                    self.increment.emit(item, "")
                    continue # next article
                        
                founded.sort(cmp = lambda a, b: cmp(a["spans"][0], b["spans"][0]), reverse=True)
                
                #отстрел пересечений            
                last_founded_sorted = founded[0]
                founded_sorted = []
                founded_sorted.append(last_founded_sorted)
                for i in range(1, len( founded )):
                    if (last_founded_sorted["spans"][0]>=founded[i]["spans"][0] and 
                            last_founded_sorted["spans"][1]<=founded[i]["spans"][0]):
                        continue
                    if (last_founded_sorted["spans"][0]>=founded[i]["spans"][1] and 
                            last_founded_sorted["spans"][1]<=founded[i]["spans"][1]):
                        continue
                    if last_founded_sorted["spans"][1] - founded[i]["spans"][1] > 2:
                        last_founded_sorted = founded[i]
                        founded_sorted.append(founded[i])                    
                founded = founded_sorted
                
                #применение стратегии
                random.shuffle(founded)
                if(self.kwargs["strategy"]):
                    founded = founded[:self.kwargs["perarticle"]]
                else:
                    c = int(math.ceil(float(len(item.article.text))/1000*self.kwargs["perchars"]))
                    founded = founded[:c]            
                founded.sort(cmp = lambda a, b: cmp(a["spans"][0], b["spans"][0]), reverse=True)

                matches += len(founded)
                
                #обработка
                egg = []
                remain = len(en_text)
                for spans in founded:
                    end = spans["spans"][1]
                    egg.insert(0,en_text[end:remain])
                    egg.insert(0,spans["word"])
                    remain = spans["spans"][0]
                else:
                    egg.insert(0,en_text[0:remain])
                
                newtext = "".join(egg).decode("utf-8","replace")
                self.increment.emit(item, newtext)
            
            #self.emit(SIGNAL("done"))
            self.done.emit(matches)
            
        except Exception:
            log.exception("exception")
        
        log.debug("thread done")
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg = AnchorWidget()
    dlg.show()
    rc = app.exec_()
