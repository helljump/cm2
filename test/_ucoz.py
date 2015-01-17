#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys, re
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
import proxy

def link_from_mail():
    br = Browser( {"http":proxy.get_random()} )
    br.open("http://www.unet.com/cemail/?s=023cfe77b990eafb8e&cc=gf4r1XvNJYQ%21D28vOKJDU9YG3ilG9TR4cmi%5EGVmG%5EWHCzSZPsDklG%3Boo")
    br.dump()

def main():
    app = QtGui.QApplication(sys.argv)
    
    br = Browser( {"http":proxy.get_random()} )
    #br = Browser()
    br.open("http://www.ucoz.ru/main/?a=reg")
    br.dump()

    #/secure/?k=4138353956;m=ureg;tm=1263597842
    captcha_url = br.img( re.compile("/secure/\?k=") )
    captcha_data = br.get_data("http://www.ucoz.ru%s" % captcha_url)
    captcha_text = anticaptcha.get_answer(captcha_data)
    
    br.set_param("email",u"inna.haz@yandex.ru")
    br.set_param("password",u"jhvuj423")
    br.set_param("password1",u"jhvuj423")
    br.set_param("name",u"Алексей")
    br.set_param("surname",u"Жданов")
    br.set_param("nick",u"Alex")
    br.set_param("by","1994")
    br.set_param("bm","2")
    br.set_param("bd","19")
    br.set_param("gender","1")
    br.set_param("location","177418292")
    br.set_param("code",captcha_text)
    br.set_param("terms","1")
    br.set_param("a","doreg")
    
    br.open("http://www.ucoz.ru/main/")

    br.dump()
    
    #if soup.head.title.contents[0]!=u"Народ.Ру: Мастерская":
    #    raise BrowserError

if __name__ == "__main__":
    link_from_mail()
    