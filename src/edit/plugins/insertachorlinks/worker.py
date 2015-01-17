#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
import Queue
from PyQt4.QtCore import * #@UnusedWildImport

log = logging.getLogger(__name__)

class Worker(QThread):
    def __init__(self, queue, parent=None):
        QThread.__init__(self, parent)
        self.queue = queue
        self.online = True
    def run(self):
        log.debug("start %s" % QThread.currentThread())
        while self.online:
            try:
                task = self.queue.get_nowait()
                result = task()
                self.emit(SIGNAL('taskDone(PyQt_PyObject)'), result)
            except Queue.Empty:
                QThread.usleep(10)
        log.debug("stop %s" % QThread.currentThread())
    def die(self):
        self.online = False
        self.wait(100)
        self.terminate()

