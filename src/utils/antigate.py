#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__date__ = "07.11.2010 0:06:48"
__author__ = "snöa"

import logging 
from engine.browser import Browser, FormMethod
import time

log = logging.getLogger(__name__)

SOFT_ID = '48'
URL = "http://antigate.com"
TIMEOUT = 60
SLEEPTIME = 10

class AntigateError(Exception):
    pass

class Antigate(object):
    """
                   72865d824cf54eb6b8a841547df
    ag = Antigate("9404cccf08797ec7d76bbe5224f")
    print ag.get_balance()
    print ag.get_text(open("d:\\transfer\\image.jpg", "rb"), numeric="1")
    """
    def __init__(self, key):
        self.key = key
        self.br = Browser(proxy={}, timeout=TIMEOUT)

    def check_error(self):
        if self.br.source.startswith("ERROR_"):
            raise AntigateError(self.br.source)

    def get_balance(self):
        url = "%s/res.php?key=%s&action=getbalance" % (URL, self.key)
        self.br.open(url)
        self.check_error()
        return self.br.source

    def send(self, data, phrase, regsense, numeric, calc, min_len, max_len, fname="image.gif"):
        self.br.set_param("key", self.key)
        self.br.set_file("file", data, fname)
        self.br.set_param("soft_id", SOFT_ID)
        # 1 помечает что у капчи 2-4 слова
        self.br.set_param("phrase", phrase) 
        # 1 помечает что текст капчи чувствителен к регистру
        self.br.set_param("regsense", regsense)
        # 0 по умолчанию, 1 помечает что текст капчи состоит только из цифр, 2 помечает что на капче нет цифр 
        self.br.set_param("numeric", numeric)
        # 1 помечает что цифры на капче должны быть сплюсованы
        self.br.set_param("calc", calc)
        # 0 по-умолчанию, помечает минимальную длину текста капчи
        self.br.set_param("min_len", min_len)
        # 0 - без ограничений, помечает максимальную длину капчи
        self.br.set_param("max_len", max_len)
        self.br.method = FormMethod.MULTIPART
        self.br.open("%s/in.php" % URL)
        self.check_error()
        cap_id = self.br.source.split("|")[1] 
        return cap_id

    def recv(self, cap_id):
        url = "%s/res.php?key=%s&action=get&id=%s" % (URL, self.key, cap_id)
        self.br.open(url)
        self.check_error()
        if self.br.source == "CAPCHA_NOT_READY":
            return None
        text = self.br.source.split("|")[1]
        return text

    def get_text(self, data, phrase="0", regsense="0", numeric="0", calc="0",
             min_len="0", max_len="0"):
        cap_id = self.send(data, phrase, regsense, numeric, calc, min_len, max_len)
        log.debug("cap_id %s", cap_id)
        t = time.time()
        while time.time() - t < TIMEOUT:
            answer = self.recv(cap_id)
            if answer:
                return answer
            log.debug("catcha not ready, sleep %i seconds", SLEEPTIME)
            time.sleep(SLEEPTIME)
        raise AntigateError("ERROR_ANTIGATE_TIMEOUT")

#if __name__ == "__main__":
#    ag = Antigate("9404cccf08797ec7d76bbe5224f")
#    print ag.get_balance()
#print ag.get_text(open("d:\\transfer\\yimage.gif", "rb"), numeric="1")
