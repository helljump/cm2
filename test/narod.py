#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys, re
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
import proxy

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    
    br = Browser( {"http":proxy.get_random()} )
    br.open("http://passport.yandex.ru/passport?mode=auth&retpath=http://narod.yandex.ru/")
    br.set_param("login",u"anuytka1666")
    br.set_param("passwd",u"dfk6i4fgmh")
    br.set_param("In",u"Войти")
    br.open("http://passport.yandex.ru/passport?mode=auth")
    url = br.link(re.compile("http://narod\.yandex\.ru/userarea/after_register\.xhtml\?random_nocache="))
    soup = br.open(url)
    br.dump()
    if soup.head.title.contents[0]!=u"Народ.Ру: Мастерская":
        raise BrowserError
