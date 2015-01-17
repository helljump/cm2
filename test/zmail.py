#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys, re, logging
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
    
if __name__ == "__main__":
        
    app = QtGui.QApplication(sys.argv)

    brwr = Browser({"http":"201.234.207.178:8080"})
    url = "https://stat.zenon.net/c/cgpaccount"
    soup = brwr.open(url)
    
    recaptcha_url = soup.find("iframe", 
        attrs={"src":re.compile("api-secure\.recaptcha\.net")})["src"]

    recaptcha_code = anticaptcha.get_recaptcha_answer( brwr, recaptcha_url )

    brwr.set_param("login","ivankovich43")
    brwr.set_param("domain","zmail.ru")
    brwr.set_param("fullname",u"Ivankovick Sergey")
    brwr.set_param("RecoverPassword","")
    brwr.set_param("genpass","own")
    brwr.set_param("newpass","djvgt554f")
    brwr.set_param("newpass2","djvgt554f")
    brwr.set_param("recaptcha_challenge_field",recaptcha_code)
    brwr.set_param("create",u"зарегистрировать")
    soup = brwr.open(url)

    success = soup.find("meta", attrs={"content":"0;URL=http://www.zmail.ru/?C="})
    if not success:
        raise BrowserError
