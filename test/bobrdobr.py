#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

#taufik-sanzharov|heqa70wip

import sys, re
from PyQt4 import QtGui
import engine.anticaptcha as anticaptcha
from engine.browser import Browser, BrowserError, FormMethod
import logging

def register():
    app = QtGui.QApplication(sys.argv)
            
    #br = Browser( {"http":proxy.get_random()}, timeout=10 )
    br = Browser( timeout=60 )
    url = "http://bobrdobr.ru/registration/"
    br.open(url)
    
    br.select_form(nr=2)
        
    br.set_param("username", "Ulpan-ogly")
    br.set_param("password", "sdhbk4khb")
    br.set_param("email", "sulpan983@yandex.ru")
    br.set_param("fullname", u"Ulpan Ismaev")
        
    captcha_data = br.get_data( "http://bobrdobr.ru" + br.img(re.compile("/captcha/")) )
    captcha_text = anticaptcha.get_answer( captcha_data )
    br.set_param("captcha_1", captcha_text)
    
    br.set_param("accept_terms", "on")
    br.set_param("submit",u"Зарегистрироваться")
    
    br.open(url)
    
    br.dump()

if __name__ == "__main__":
    register()
