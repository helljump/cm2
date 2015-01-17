#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
Created on 01.03.2010

@author: snoa
'''

import re
from engine.browser import Browser, BrowserError
from engine import anticaptcha
import logging
import Profile #@UnresolvedImport

def registration(name, surname, user, passwd):
    
    prof = Profile()
    
    br = Browser()
    url = "http://www.yandex.ru/"
    br.open(url)
    url = br.link(re.compile("http://passport\.yandex\.ru/passport\?mode=register&msg=mail"))
    soup = br.open(url)
    url = soup.find("form", attrs={"action":re.compile("http://passport\.yandex\.ru/passport\?mode=register&ncrnd=")})["action"]
    br.set_param("iname", name)
    br.set_param("fname", surname)
    br.set_param("login", user)
    br.set_param("done", u"Дальше&nbsp;&rarr;")
    br.open(url)
    captcha_url = br.img(re.compile("http://passport\.yandex\.ru/digits\?idkey="))
    captcha_data = br.get_data(captcha_url)
    captcha_text = anticaptcha.get_answer(captcha_data)
    br.set_param("code", captcha_text)
    br.set_param("passwd", prof._pass)
    br.set_param("passwd2", prof._pass)
    br.set_param("hintq", u"1") #mother name
    br.set_param("hinta", prof.surname + "12843") #hello to zeoshost
    br.set_param("agreed", "yes")
    br.set_param("newform", u"Зарегистрировать")
    br.open(url)

    src = br.source.find(u"Поздравляем, регистрация успешно завершена!")
    if src != -1:
        prof.write(open("profiles.txt", "a+t"))
        logging.debug("done")
    else:
        br.dump()
        raise BrowserError


if __name__ == '__main__':
#    registration(name, surname, user, passwd)
    pass
