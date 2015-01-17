#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys, re, logging
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
import proxy

def main():
    app = QtGui.QApplication(sys.argv)

    brwr = Browser({"http":proxy.get_random()})
    url = "http://memori.ru"
    soup = brwr.open(url + "/registration/")
    recaptcha_url = soup.find("iframe", 
        attrs={"src":re.compile("api\.recaptcha\.net")})["src"]
        
    recaptcha_code = anticaptcha.get_recaptcha_answer( brwr, recaptcha_url )
    brwr.set_param("login","anuytka1666")
    brwr.set_param("email","anuytka1666@yandex.ru")
    brwr.set_param("password","djvgt554f")
    brwr.set_param("password_confirm","djvgt554f")
    brwr.set_param("recaptcha_challenge_field",recaptcha_code)
    brwr.set_param("create",u"зарегистрировать")
    brwr.method_get = False
    brwr.referer = url + "/registration/"
    soup = brwr.open(url + "/register/")
    brwr.dump()

    #success = soup.find("meta", attrs={"content":"0;URL=http://www.zmail.ru/?C="})
    #if not success:
    #    raise BrowserError


if __name__ == "__main__":
    main()
