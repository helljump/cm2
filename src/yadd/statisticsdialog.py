#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread
from logging import debug, error
from scripts.addurl import Code
from utils.qthelpers import ToolBarWithPopup, MyProgressDialog
from rc import rc #@UnusedImport
import shelve
import Queue
from engine.anticaptcha import report_wrong_captcha 

class ReportWrongsThread(QThread):
    
    def __init__(self, agkey, task_queue, progressdialog, parent):
        QtCore.QThread.__init__(self, parent)
        self.agkey = agkey
        self.task_queue = task_queue
        self.connect(self, QtCore.SIGNAL("stop()"), self.stop)
        self.progressdialog = progressdialog
        self.online = True
        
    def run(self):
        debug("report thread start")
        i = 0
        for task in iter(self.task_queue.get, "STOP"):
            report_wrong_captcha(self.agkey, task)
            #time.sleep(1)
            i += 1
            self.progressdialog.emit(QtCore.SIGNAL("setValue(int)"), i)
            if not self.online:
                break
        debug("report thread end")

    def stop(self):
        self.online = False
        self.wait(500)
        self.terminate()
        self.wait()
    
class SimpleModel(QtCore.QAbstractListModel):
    def __init__(self, parent, lines):
        super(SimpleModel, self).__init__(parent)
        self.lines = list(set(lines))
        self.lines.sort()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.lines)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if index.row() >= len(self.lines) or index.row() < 0:
            return None
        
        if role == QtCore.Qt.DisplayRole:
            return "%s" % self.lines[index.row()]

        if role == QtCore.Qt.BackgroundRole:
            batch = index.row() % 2
            if batch == 0:
                return QtGui.qApp.palette().base()

            return QtGui.qApp.palette().alternateBase()

        return None
    
    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        for i in range(rows): #@UnusedVariable
            del self.lines[position]
        self.endRemoveRows()
        return True
    
class Statistic_Dialog(QtGui.QDialog):
    
    def __init__(self, parent, statistics, prjmodel):
        super(Statistic_Dialog, self).__init__(parent)
        self.statistics = statistics
        self.prjmodel = prjmodel
        self.setupUi()
    
    def setupUi(self):
        self.setWindowTitle(self.tr("Statistics"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(640, 480)
        dialoglayout = QtGui.QVBoxLayout(self)
        tabWidget = QtGui.QTabWidget(self)
        
        lines = self.statistics.get(Code.DONE, []) 
        tab = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(tab)
        tb = ToolBarWithPopup(self)
        listView = QtGui.QListView(tab)
        tb.addAction(QtGui.QIcon(":/yadd/remove.png"), self.tr("Remove from projects"),
                     lambda view=listView, remove_djenah=False: self.remove_links(view, remove_djenah))
        tb.addAction(QtGui.QIcon(":/yadd/disk.png"), self.tr("Export to file"),
                     lambda lines=lines: self.export_array_to_file(lines))
        layout.addWidget(tb)
        model = SimpleModel(self, lines)
        listView.setModel(model)
        listView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        layout.addWidget(listView)
        tabWidget.addTab(tab, self.tr("Success") + "(%i)" % listView.model().rowCount())
        
        lines = self.statistics.get(Code.NOTADDED, []) 
        tab = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(tab)
        tb = ToolBarWithPopup(self)
        tb.addAction(QtGui.QIcon(":/yadd/disk.png"), self.tr("Export to file"),
                     lambda lines=lines: self.export_array_to_file(lines))
        layout.addWidget(tb)
        model = SimpleModel(self, lines)
        listView = QtGui.QListView(tab)
        listView.setModel(model)
        layout.addWidget(listView)
        tabWidget.addTab(tab, self.tr("Not added") + "(%i)" % listView.model().rowCount())
        
        lines = self.statistics.get(Code.ALREADYININDEX, []) 
        tab = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(tab)
        tb = ToolBarWithPopup(self)
        listView = QtGui.QListView(tab)
        tb.addAction(QtGui.QIcon(":/yadd/remove.png"), self.tr("Remove links"),
                     lambda view=listView: self.remove_links(view))
        tb.addAction(QtGui.QIcon(":/yadd/disk.png"), self.tr("Export to file"),
                     lambda lines=lines: self.export_array_to_file(lines))
        layout.addWidget(tb)
        model = SimpleModel(self, lines)
        listView.setModel(model)
        listView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        layout.addWidget(listView)
        tabWidget.addTab(tab, self.tr("Already in index") + "(%i)" % listView.model().rowCount())
        
        lines = self.statistics.get(Code.BANNED, []) 
        tab = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(tab)
        tb = ToolBarWithPopup(self)
        listView = QtGui.QListView(tab)
        tb.addAction(QtGui.QIcon(":/yadd/remove.png"), self.tr("Remove banned"),
                     lambda view=listView: self.remove_links(view))
        tb.addAction(QtGui.QIcon(":/yadd/disk.png"), self.tr("Export to file"),
                     lambda lines=lines: self.export_array_to_file(lines))
        layout.addWidget(tb)
        model = SimpleModel(self, lines)
        listView.setModel(model)
        listView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        layout.addWidget(listView)
        tabWidget.addTab(tab, self.tr("Banned") + "(%i)" % listView.model().rowCount())
        
        lines = self.statistics.get(Code.WRONGCAPTCHA, []) 
        tab = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(tab)
        tb = ToolBarWithPopup(self)
        tb.addAction(QtGui.QIcon(":/yadd/disk.png"), self.tr("Export to file"),
                     lambda lines=lines: self.export_array_to_file(lines))
        tb.addAction(QtGui.QIcon(":/yadd/award.png"), self.tr("Send to antigate"),
                     lambda lines=lines: self.send_to_antigate(lines))
        layout.addWidget(tb)
        model = SimpleModel(self, lines)
        listView = QtGui.QListView(tab)
        listView.setModel(model)
        listView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        layout.addWidget(listView)
        tabWidget.addTab(tab, self.tr("Wrong captches") + "(%i)" % listView.model().rowCount())
             
        dialoglayout.addWidget(tabWidget)

        bbox = QtGui.QDialogButtonBox(self)
        bbox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.connect(bbox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.accept)
        dialoglayout.addWidget(bbox)

    def send_to_antigate(self, captchas):
        
        ''' отправляем список капчей на антигейт '''
        
        pd = MyProgressDialog("Antigate report", self.tr("Send wrong captchas.."), self.tr("Cancel"),
                              1, len(captchas), self)
        self.connect(pd, QtCore.SIGNAL("setValue(int)"), pd, QtCore.SLOT("setValue(int)"))
        pd.setFixedWidth(300)
        cfg = shelve.open("yadd.cfg")
        agkey = cfg.get("yadd.antigate_key", "")
        cfg.close()
        pd.show()
        task_queue = Queue.Queue()
        for task in captchas:
            task_queue.put_nowait(task) 
        task_queue.put_nowait("STOP") 
        th = ReportWrongsThread(agkey, task_queue, pd, self)
        th.start()
        while th.isRunning():
            if pd.wasCanceled():
                pd.close()
                th.emit(QtCore.SIGNAL("stop()"))
            QtGui.qApp.processEvents()
        pd.close()

    def remove_links(self, view, remove_djenah=True):
        model = view.model() 
        if model.rowCount() < 1:
            debug("no data in model")
            return

        selectionModel = view.selectionModel()
        indexes = selectionModel.selectedRows()
        if len(indexes) < 1:
            debug("no selection in model")
            return

        djlinks = []        
        if remove_djenah:
            cfg = shelve.open("yadd.cfg")
            djlinks = cfg.get("yadd.djenah_links", [])
            cfg.close()
            djupdated = False
        
        indexes.sort(cmp=lambda x, y: cmp(x.row(), y.row()), reverse=True)
        for index in indexes:
            row = index.row()
            url = model.data(index)
            if url.find('[SITEURL]') == -1:
                for row in range(self.prjmodel.rowCount()):
                    prj = self.prjmodel.projects[row]
                    if prj.url == url:
                        debug("del project %s" % prj)
                        self.prjmodel.removeRow(row)
                        break
                else:
                    error("no project %s", prj)
            elif remove_djenah:
                try:
                    djlinks.remove(url)
                    djupdated = True
                    debug("del djenah %s", url)
                except ValueError, err:
                    error("%s url:%s", err, url)
            model.removeRow(row)
                    
        if remove_djenah and djupdated:
            cfg = shelve.open("yadd.cfg")
            cfg["yadd.djenah_links"] = djlinks 
            cfg.close()

    def export_array_to_file(self, lines):
        try:
            fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"), ".", "Text file (*.txt)")
            if fileName == "": 
                return
            debug("save to %s" % fileName)
            with open(fileName, "wt") as fout:
                for l in lines:
                    fout.write("%s\n" % str(l))
        except IOError:
            QtGui.QMessageBox.error(self, self.tr("Save file"), self.tr("File not saved"))

if __name__ == "__main__":
    import sys, pickle
    app = QtGui.QApplication(sys.argv)
    statistics = pickle.load(open("results.log", "rb"))
    dlg = Statistic_Dialog(None, statistics, [])
    sys.exit(dlg.exec_())

