#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
from engine.anticaptcha import get_answer
from engine.browser import Browser
from scripts.addurl import Code, AddUrlResult
import logging
import re

def addurl(site, proxy={}, queue=None, queueimg=None, userkey="", timeout=30):
    '''
    Добавление адреса в яндекс с ипользованием прокси
    
    @param site: адрес сайта
    @param proxy: словарь прокси {"http":"12.34.56.78:808"}
    @param queue: очередь для общения с гуем
    
    если все плохо - выбрасываем исключение
    '''
    brwr = Browser(proxy, timeout=timeout)
    
    if not brwr.url_is_alive(site): return AddUrlResult(Code.NOTADDED)
    
    url = "http://webmaster.yandex.ru/addurl.xml"
    brwr.open(url)
    captcha_url = brwr.img(re.compile("captcha"))
    data = brwr.get_data(captcha_url)    
    captcha_text, cap_id = get_answer(data, queue, userkey, queueimg)
    brwr.select_form(nr=1)#select second form fix
    brwr.set_param("url", site)
    brwr.set_param("rep", captcha_text)
    brwr.set_param("do", "add")
    brwr.open(url)
    #brwr.dump()
    
    if brwr.source.find(u"Вы неверно указали цифровой код.") > 0:
        rc = AddUrlResult(Code.WRONGCAPTCHA)
        rc.cap_id = cap_id 
        return rc
    elif brwr.source.find(u"уже проиндексирован</a>") > 0:
        return AddUrlResult(Code.ALREADYININDEX)
    elif brwr.source.find(u"Указанный URL запрещен к индексации.") > 0:
        return AddUrlResult(Code.BANNED)
    elif brwr.source.find(u"успешно добавлен") == -1:
        return AddUrlResult(Code.NOTADDED) 
    return AddUrlResult(Code.DONE)
    logging.debug("add successfully [%s]" % site)
    
if __name__ == "__main__":
    reload(sys)
    if hasattr(sys, "setdefaultencoding"): 
        sys.setdefaultencoding("utf-8")
        
    userkey = "404cccf08797ec7d76bbe5224f"
    addurl("http://www.its-free.ru/engine/redirect.php?url=http://s-center.ru", 
        proxy={"http":"219.139.158.59:8080"},
        userkey=userkey)
