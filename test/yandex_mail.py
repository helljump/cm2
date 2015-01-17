#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys, re
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
import proxy
from profile import Profile
import logging

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    
    prof = Profile()
    
    br = Browser( {"http":proxy.get_random()} )
    url = "http://www.yandex.ru/"
    br.open(url)
    url = br.link( re.compile("http://passport\.yandex\.ru/passport\?mode=register&msg=mail") )
    soup = br.open(url)
    url = soup.find("form", attrs={"action":re.compile("http://passport\.yandex\.ru/passport\?mode=register&ncrnd=")})["action"]
    br.set_param("iname", prof.name)
    br.set_param("fname", prof.surname)
    br.set_param("login", prof.username)
    br.set_param("done",u"Дальше&nbsp;&rarr;")
    br.open(url)
    #br.dump()
    captcha_url = br.img( re.compile("http://passport\.yandex\.ru/digits\?idkey=") )
    captcha_data = br.get_data( captcha_url )
    captcha_text = anticaptcha.get_answer( captcha_data )
    br.set_param("code",captcha_text)
    br.set_param("passwd", prof._pass)
    br.set_param("passwd2", prof._pass)
    br.set_param("hintq",u"1") #mother name
    br.set_param("hinta", prof.surname + "12843") #hello to zeoshost
    br.set_param("agreed","yes")
    br.set_param("newform",u"Зарегистрировать")
    br.open(url)

    src = br.source.find(u"Поздравляем, регистрация успешно завершена!")
    if src!=-1:
        prof.write( open("profiles.txt","a+t") )
        logging.debug("done")
    else:
        br.dump()
        raise BrowserError
