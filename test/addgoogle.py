#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys, re
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
import logging

def addurl( site, proxy ):
    brwr = Browser( proxy )
    soup = brwr.open("http://www.google.ru/addurl")
    brwr.set_param("q",site)
    brwr.set_param("dq",u"Очень хороший сайт")
    brwr.set_param("submit",u"Добавить URL")
    soup = brwr.open("http://www.google.ru/addurl")
    rc = soup.find("div", attrs={"class":"content"}).p.b.contents[0]
    if rc != u"Спасибо.":
        raise BrowserError
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    for i in range(100):
        try:
            addurl( "http://transport.iblogger.org" , {"http":"221.130.13.204:80"} )
        except Exception, err:
            logging.error("err %s" % err)
