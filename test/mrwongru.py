#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

#taufik-sanzharov|heqa70wip

import sys, re
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
import proxy
from profile import Profile
import logging

def register():
    app = QtGui.QApplication(sys.argv)
    
    prof = Profile("-")
            
    br = Browser( {"http":proxy.get_random()} )
    url = "http://bobrdobr.ru/registration/"
    br.open(url)
    #br.dump()
    
    #sys.exit()
           
    br.set_param("username", prof.username)
    br.set_param("email", "vovao43@yandex.ru")
    br.set_param("password", prof._pass)
    br.set_param("do_reg",u"Зарегистрироваться")
    br.set_param("fullname", u"%s %s" % (prof.name,prof.surname))
    
    captcha_url = "http://bobrdobr.ru" + br.img( re.compile("/captcha/") )
    captcha_data = br.get_data( captcha_url )
    captcha_text = anticaptcha.get_answer( captcha_data )
    
    br.set_param("captcha_1", captcha_text)
    br.set_param("accept_terms", u"on")
    br.set_param("submit",u"Зарегистрироваться")

    br.open(url)
    
    br.dump()
    print "%s" % prof
    sys.exit()
    
    
    src = br.source.find(u"успешно зарегистрировались")
    if src!=-1:
        prof.write( open("profiles.txt","a+t") )
        logging.debug("done")
        logging.debug("%s" % prof)
        
    else:
        br.dump()
        raise BrowserError

def post():

    app = QtGui.QApplication(sys.argv)
    
    my_url="http://gogo33333333333e3333.ru"
    
    prof = Profile()
    prof.username ="taufik-sanzharov"
    prof._pass = "heqa70wip"
    
    #br = Browser( {"http":proxy.get_random()} )
    br = Browser( {"http":"110.137.64.180:8080"} )
    url = "http://moemesto.ru/login/"
    br.open(url)
    
    br.set_param("login", prof.username)
    br.set_param("password", prof._pass)
    br.set_param("do_auth",u"войти")
    br.set_param("bind_ip","1")

    br.open(url)

    br.link("/post.php")

    url = "http://moemesto.ru/post"
    br.open(url)

    br.set_param("url",my_url)
    br.set_param("title",u"поисковик гого")
    br.set_param("desc",u"удобный поисковичек с глазками")
    br.set_param("tags",u"гого")
    br.set_param("status",u"ALL")
    
    br.set_param("save","on")
    br.set_param("do_post",u"Добавить")
    
    try: 
        br.open(url)
    except Exception, e:
        logging.warning ("%s" % e)    
    #br.dump()
    
    url = "http://moemesto.ru/%s" % prof.username
    br.open(url)
    br.link(my_url)
    

if __name__ == "__main__":
    register()
    