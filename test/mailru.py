#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys, re
from PyQt4 import QtGui
import anticaptcha
from browser import Browser, BrowserError
import logging
import proxy

try:
    app = QtGui.QApplication(sys.argv)

    br = Browser( {"http":proxy.get_random()} )

    soup = br.open("http://mail.ru")
    url = br.link( re.compile("http://win\.mail\.ru/cgi-bin/signup\?reg_user=") )
    soup = br.open(url)
    codefield_name = re.search(u"(.+?)\:'Введите код на картинке'", br.source).groups(0)[0].strip()
    logging.debug("codefield_name %s" % codefield_name)
    img_url = br.img( re.compile("x_get_image") )
    logging.debug("img url %s" % img_url)
    captcha_file = br.get_data( "http://win.mail.ru/cgi-bin/%s" % img_url )
    captcha_text = anticaptcha.get_answer( captcha_file )
    
    template = "fields\[fields\.length\] = '(.+?)';\s+prompts\[prompts\.length\] = '(.+?)';"
    fields = {}
    for m in re.finditer(template, br.source, re.M | re.S | re.U):
        fields[m.group(2)] = m.group(1)     

    br.set_param(fields[u'Имя'],u"Амран")
    br.set_param(fields[u'Фамилия'],u"Инширов")
    br.set_param(fields[u'День рождения'],"1")
    br.set_param(fields[u'Месяц рождения'],u"10")
    br.set_param(fields[u'Год рождения'],"1990")
    br.set_param(fields[u'E-mail'],"inshir11")
    br.set_param("RegistrationDomain","mail.ru")
    br.set_param(fields[u'Пароль'],"sdvj43bnj")
    br.set_param(fields[u'Подтверждение пароля'],"sdvj43bnj")
    br.set_param("Password_Question",u"Я незнаю что тут у вас за вопрос")
    br.set_param(fields[u'Ответ на секретный вопрос'],u"Радости и счастья населению марса")
    br.set_param(fields[u'Ваш пол'],"1")
    br.set_param("my_create","0")
    br.set_param(codefield_name, captcha_text)
    br.set_param("mra1","0")
    br.set_param("B1",u" Зарегистрировать почтовый ящик ")
 
    soup = br.open("http://win.mail.ru/cgi-bin/reg")

    success = soup.find("h3", attrs={"class":"head_1"})
    if "".join(success.contents).strip() != u"Авторизация":
        raise BrowserError

except:
    br.dump()
    raise
