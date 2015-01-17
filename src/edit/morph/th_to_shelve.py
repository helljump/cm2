#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"
import logging 
import shelve
import cPickle
import re

log = logging.getLogger(__name__)

"""
абонировать|2
(синоним)|нанимать|брать в наем|брать внаймы
(сходный термин)|нанимать
"""

finpname = "th_ru_RU_v2.dat"
th = {}
db = shelve.open("ru/th.shelve", protocol=cPickle.HIGHEST_PROTOCOL)

with open(finpname) as finp:
    lns = finp.readlines()
    encoding = lns.pop(0).strip()
    print "encoding:", encoding
    while lns:
        word, cnt = lns.pop(0).split("|")
        word = unicode(word, encoding).upper()
        cnt = int(cnt)
        # print word, cnt
        d = {}
        for i in range(cnt):
            egg = unicode(lns.pop(0), encoding).upper()
            therms = egg.split("|")
            v = therms.pop(0)[1:-1].lower()
            if v not in d:
                d[v] = []
            for j in range(len(therms)):
                therms[j] = re.sub("\(.+?\)","",therms[j]).strip()
            d[v] += therms
        # th[word] = d
        db[ word.encode("koi8-r") ] = d

# db['thesaurus'] = th
db.close()
