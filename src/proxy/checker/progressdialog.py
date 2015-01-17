#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
from PyQt4 import QtCore, QtGui
import logging
import urllib2, httplib
import Queue
import time
import socket

class Codes(object): (TEST, DONE, SUCC) = range(3)

class ProxytestThread(QtCore.QThread):
    def __init__(self, task_queue, done_queue, target_url, timeout, parent):
        QtCore.QThread.__init__(self, parent)
        self.task_queue = task_queue
        self.done_queue = done_queue
        self.target_url = target_url
        self.timeout = timeout
        self.connect(self, QtCore.SIGNAL("stop_proxytests()"), self.stop)
        self.online = True

    def run(self):
        logging.debug("run thread")
        for treeitem in iter(self.task_queue.get, "STOP"):
            self.test_proxy(treeitem, self.done_queue, self.target_url, self.timeout)
            if not self.online:
                break
        logging.debug("done thread")
        
    def stop(self):
        logging.debug("signal stop emitted")
        self.online = False

    def test_proxy(self, treeitem, queue, target_url, timeout):
        queue.put_nowait((Codes.TEST, treeitem))
        try:
            egg_url = target_url[0]
            egg_answer = target_url[1]
            treeitem.status = -1
            proxy_handler = urllib2.ProxyHandler({"http": treeitem.address})
            http_handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(proxy_handler, http_handler)
            opener.addheaders = [("User-agent", "Mozilla/5.0")]
            t = time.time()
            socket.setdefaulttimeout(timeout)
            req = urllib2.Request(egg_url)
            response = opener.open(req, timeout=timeout)
            data = response.read()
            data.index(egg_answer)
            treeitem.status = time.time() - t
        except urllib2.HTTPError:        
            logging.error("httperror %s" % treeitem.address)
        except (urllib2.URLError, httplib.HTTPException):        
            logging.error("urlerror %s" % treeitem.address)
        except socket.timeout:
            logging.error("socket timeout %s" % treeitem.address)
        except ValueError:
            logging.error("wrong answer %s" % treeitem.address)
        else:
            queue.put_nowait((Codes.SUCC, treeitem.address))
            logging.debug("tested %s %f ms" % (treeitem.address, treeitem.status))
        queue.put_nowait((Codes.DONE, treeitem))

class ProgressDialog(QtGui.QDialog):
    def __init__(self, treeitems, target_url, timeout, threads_amount, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi()
        self.treeitems = treeitems
        self.target_url = target_url
        self.timeout = timeout
        self.threads_amount = threads_amount
        self.start()
        
    def setupUi(self):
        self.setWindowTitle(self.tr("Checking.."))
        self.resize(373, 121)
        self.gridLayout = QtGui.QGridLayout(self)
        self.status_lb = QtGui.QLabel(self.tr("Status"), self)
        self.gridLayout.addWidget(self.status_lb, 0, 0, 1, 1)
        self.log_le = QtGui.QLineEdit(self)
        self.log_le.setReadOnly(True)
        self.gridLayout.addWidget(self.log_le, 0, 1, 1, 1)
        self.alive_lb = QtGui.QLabel(self.tr("Alive"), self)
        self.gridLayout.addWidget(self.alive_lb, 0, 2, 1, 1)
        self.label = QtGui.QLabel(self.tr("Progress"), self)
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.progress_pb = QtGui.QProgressBar(self)
        self.progress_pb.setValue(0)
        self.gridLayout.addWidget(self.progress_pb, 1, 1, 1, 3)
        self.label_2 = QtGui.QLabel(self.tr("Threads"), self)
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.threads_pb = QtGui.QProgressBar(self)
        self.threads_pb.setValue(0)
        self.threads_pb.setTextVisible(True)
        self.threads_pb.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.threads_pb.setFormat("%v")
        self.gridLayout.addWidget(self.threads_pb, 2, 1, 1, 3)
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        #self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.reject_button = self.buttonBox.addButton(self.tr("Cancel"), QtGui.QDialogButtonBox.RejectRole)
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 4)

        self.alive_le = QtGui.QLineEdit(self)
        self.alive_le.setMaximumSize(QtCore.QSize(62, 16777215))
        self.alive_le.setReadOnly(True)
        self.gridLayout.addWidget(self.alive_le, 0, 3, 1, 1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.closeEvent)

        self.threadpool = []
        self.task_queue = Queue.Queue()
        self.done_queue = Queue.Queue()

    def timerEvent(self, event):
        try:
            spam = self.done_queue.get_nowait()
            if spam[0] == Codes.TEST:
                self.log_le.setText("%s testing.." % spam[1].address)
                self.workers += 1
            elif spam[0] == Codes.SUCC:
                self.alive += 1
                self.alive_le.setText("%i" % self.alive)
            elif spam[0] == Codes.DONE:
                self.workers -= 1
                self.log_le.setText("%s done" % spam[1].address)
                self.progress_pb.setValue(self.progress_pb.value() + 1)
            self.threads_pb.setValue(self.workers)
            self.firstRun = False
        except Queue.Empty:
            pass
        for worker in self.threadpool:
            if worker.isRunning():
                break
        else:
            self.accept()

    def start(self):
        logging.debug("add threads in pool")
        
        self.workers = 0
        self.alive = 0
        self.progress_pb.setRange(0, len(self.treeitems))
        self.threads_pb.setRange(0, self.threads_amount)
        self.alive_le.setText("0")
        self.log_le.setText("")

        #заполняем очередь заданий
        for item in self.treeitems:
            self.task_queue.put_nowait(item)

        for item in range(self.threads_amount):
            self.task_queue.put_nowait("STOP")
        
        #добаляем в пул процессы
        for i in range(self.threads_amount): #@UnusedVariable
            worker = ProxytestThread(self.task_queue, self.done_queue, self.target_url, self.timeout, self)
            worker.start()
            self.threadpool.append(worker)
        
        self.firstRun = True
        self.startTimer(100)
            
    def closeEvent(self, event):
        self.close_in_process()
        event.ignore()
        
    def accept(self):
        self.close_in_process()
        self.hide()

    def reject(self):
        self.close_in_process()

    def close_in_process(self):
        logging.debug("close_in_process")
        for worker in self.threadpool:
            worker.emit(QtCore.SIGNAL("stop_proxytests()"))
            worker.terminate()
            worker.wait()
        
        self.buttonBox.setDisabled(True)
        self.reject_button.setText(self.tr("Wait..."))

class TestItem(object):
    def __init__(self, item):
        self.address = item[0]
        self.status = item[1]

if __name__ == "__main__":
                
    app = QtGui.QApplication(sys.argv)
    logging.debug("__main__ over")
