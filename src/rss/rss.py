#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import urllib2, socket
from xml.dom import minidom
import sys
from datetime import datetime
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread
from logging import debug, exception
from Queue import Queue, Empty
from time import sleep
import staticpage_qrc #@UnusedImport

class RSSThread(QThread):
    def __init__(self, command_q, data_q, timeout, parent):
        QtCore.QThread.__init__(self, parent)
        self.timeout = timeout
        self.data_q = data_q
        self.command_q = command_q

    def stop(self):
        self.wait(1000)
        self.terminate()
        self.wait()

    def get_data(self, item, elem): 
        return item.getElementsByTagName(elem)[0].childNodes[0].data.strip()

    def run(self):
        socket.setdefaulttimeout(30)
        opener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.ProxyHandler(None))
        online = True
        
        while online:
            feed = []
            
            url = "http://blap.ru/forum/index.php?type=rss;action=.xml"
            debug("open %s" % url)
            dt_format = "%a, %d %b %Y %H:%M:%S %Z"
            try:
                response = opener.open(url)
                dom = minidom.parse(response)
                for item in dom.getElementsByTagName("item"):
                    pubDate = datetime.strptime(self.get_data(item, "pubDate"), dt_format)
                    rssitem = RSSItem(self.get_data(item, "title"),
                                      self.get_data(item, "link"), pubDate, "blap.ru/forum")
                    feed.append(rssitem)
            except Exception, err:
                exception("rss error %s", err)

            url = "http://blap.ru/feed/"
            debug("open %s" % url)
            dt_format = "%a, %d %b %Y %H:%M:%S"
            try:
                response = opener.open(url)
                dom = minidom.parse(response)
                for item in dom.getElementsByTagName("item"):
                    pubDate = datetime.strptime(self.get_data(item, "pubDate")[:-6], dt_format)
                    rssitem = RSSItem(self.get_data(item, "title"),
                                      self.get_data(item, "link"), pubDate, "blap.ru")
                    feed.append(rssitem)
            except Exception, err:
                exception("rss error %s", err)
            
            url = "http://feeds.feedburner.com/lipf"
            debug("open %s" % url)
            try:
                response = opener.open(url)
                dom = minidom.parse(response)
                dt_format = "%a, %d %b %Y %H:%M:%S"
                pubDate = datetime.strptime(self.get_data(dom, "lastBuildDate")[:-6], dt_format)
                for item in dom.getElementsByTagName("item"):    
                    rssitem = RSSItem(self.get_data(item, "title"),
                                      self.get_data(item, "feedburner:origLink"), pubDate, "lipf.ru")
                    feed.append(rssitem)
            except Exception, err:
                exception("rss error %s", err)

            feed.sort(cmp=lambda x, y: cmp(x.pubdate, y.pubdate), reverse=True)
            debug("articles in feed %i" % len(feed))
            self.data_q.put(feed, False)
            for i in range(self.timeout * 100): #@UnusedVariable
                try:
                    if self.command_q.get(False) == True:
                        online = False
                        break
                except Empty:
                    pass
                sleep(.01)

        debug("feed thread is dead")

class RSSItem(object):
    def __init__(self, title, link, pubdate, site):
        self.title = title
        self.link = link
        self.pubdate = pubdate
        self.site = site
    
    def __repr__(self):
        return ("<RSSItem>" + self.title + "\n" + 
            self.link + "\n" + self.pubdate.strftime("%d/%m/%y %H:%M") + 
            "\n" + self.site + "\n</RSSItem>")

class RSSWidget(QtGui.QTextBrowser):
    def __init__(self, show_static=True, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.anchorClicked.connect(self.launchBrowser)
        self.setOpenLinks(False)

        self.timer = self.startTimer(1800)
        self.sleep = 1800

        self.commandqueue = Queue()
        self.dataqueue = Queue()
        self.task = RSSThread(self.commandqueue, self.dataqueue, self.sleep, self)
        self.task.start()

        if show_static:
            #self.setFixedWidth(230)
            self.set_static()
        else:
            self.setHtml("<br/><br/><center>%s</center>" % self.tr("Connecting..."))
    
    def hideEvent(self, event):
        #debug("event %s" % event)
        self.closeEvent()
        event.accept()
    
    def launchBrowser(self, url):
        debug("browse %s" % url)
        QtGui.QDesktopServices.openUrl(url)
        return True

    def timerEvent (self, event):
        
        try:
            feed = self.dataqueue.get(False)
            output = []
            div_color = "#fff"
            for item in feed:
                output.append("<div style=\"background-color:%s;\">" % div_color)
                output.append("<a href=\"%s\"><b>%s</b></a>" % (item.link, item.title))
                output.append("(%s)<br/>" % item.site)
                output.append("<small>%s</small>" % (item.pubdate.strftime("%d/%m/%y %H:%M")))
                output.append("</div>")
                if div_color == "#fff":
                    div_color = "#eee"
                else:
                    div_color = "#fff"
            self.setText("\n".join(output))
        except Empty:
            pass

    def closeEvent(self):
        debug("close widget 1")
        self.commandqueue.put(True)
        #self.task.wait(2000)
        #self.task.terminate()
        self.task.stop()
        debug("close widget 2")

    def set_static(self):
        debug("set static")
        html_text = QtCore.QResource(":/banner/static.html").data()
        self.setText(unicode(html_text))

class RSSDialog(QtGui.QDialog):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setWindowTitle(self.tr("Rss"))
        self.setWindowFlags(QtCore.Qt.Window) 
        self.resize(320, 480)
        gridLayout = QtGui.QGridLayout(self)
        rssWidget = RSSWidget(True, self)
        gridLayout.addWidget(rssWidget, 0, 0, 1, 1)
        self.connect(self, QtCore.SIGNAL("pizdets()"), rssWidget.closeEvent)

    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL("pizdets()"))
        event.accept()
        debug("done")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    RSSDialog().exec_()


