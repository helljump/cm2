#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import cPickle
import re


"""
абонировать|2
(синоним)|нанимать|брать в наем|брать внаймы
(сходный термин)|нанимать
"""

finpname = "th_ru_RU_v2.dat"
foutname = "ru/th.pkl"
# словарь хеш(word.unicode.upper) - ТОбъект
th = {}


def TObject():
    return {'syn': set(), 'sim': set(), 'ant': set(), 'con': set()}


def clean(word):
    return re.sub("\(.+?\)", "", word).strip()


curline = 1
subline = 0
with open(finpname) as finp:
    lns = finp.readlines()
    encoding = lns.pop(0).strip()
    print "encoding:", encoding
    while lns:
        word, cnt = lns.pop(0).split("|")
        word = unicode(word, encoding).upper()
        cnt = int(cnt)
        tobject = th[hash(word)] = th.get(hash(word), TObject())
        curline += 1
        subline += 1
        for i in range(cnt):
            egg = unicode(lns.pop(0), encoding).upper()
            spam = re.search('\(([\w\s]+)\)([\w\s\|]+)', egg, re.U)
            wtype = spam.group(1)
            therms = spam.group(2).split("|")
            therms = map(clean, therms)
            if wtype == u"СИНОНИМ":
                tobject['syn'] |= set(therms)
            elif wtype == u"АНТОНИМ":
                tobject['ant'] |= set(therms)
            elif wtype == u"СХОДНЫЙ ТЕРМИН":
                tobject['sim'] |= set(therms)
            elif wtype == u"СВЯЗАННЫЙ ТЕРМИН":
                tobject['con'] |= set(therms)
            else:
                raise Exception("unknown wtype %i" % curline)
            curline += 1

cPickle.dump(th, open(foutname, "wb"), protocol=cPickle.HIGHEST_PROTOCOL)
print 'lemms', subline, curline
