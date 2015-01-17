#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
import sys
import random
import yaml
import os
import csv
from StringIO import StringIO
import re
from pytils import numeral

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

INWORDS = False
PATH = ""
BASE = {}
CACHE = {}

tokenizer_re = re.compile("(\{\$.+?\})")
token_re = re.compile("\{.+?\}")

token_inwords = re.compile("\{.+?:s\}")
token_dict = re.compile("\{.+?:\w+\.yml\}")

TEMPLATE_SAMPLE = u"""{$1}, {$имеет массу|располагает массой|приблизительно весит} {$2}, цвет - {$3}, ёмкость АКБ - {$4} мА/ч"""

CSV_SAMPLE = StringIO(u""""Мобильник Gnusmas 1810g";49;"зеленый";2000
"Мобильник Лыжи";198;"красный";1001
"Мобильник Лыжи2";1981;"синий";1500
""".encode("utf-8"))

DICT_SAMPLE = u"""
!!python/tuple [0,50.9]:
- "%s кг, что достаточно мало"
- "%s кг, это вообщем скромно"
!!python/tuple [51,99]:
- "%s кг, что удовлетворительно"
- "%s кг, что обычно для этого продукта"
!!python/tuple [100,1000]:
- "более ста килограмм"
- "%s кг, что довольно много"

"зеленый":
- "%s"
- "светлозеленый"
"красный":
- "%s"
- "пурпурный"
"""

class RandomToken(object):
    """
    >>> random.seed(1)
    >>> rt = RandomToken([1,2,3,4,5])
    >>> print rt()
    1
    >>> print rt()
    5
    >>> print rt()
    4
    """
    def __init__(self, li):
        self.data = li
    def __call__(self):
        return random.choice(self.data)

class DictToken(object):
    def __init__(self, v, base):
        self.v = v
        self.base = base
    def __call__(self):
        for key, val in self.base.iteritems():
            if isinstance(key,tuple) and self.v >= key[0] and self.v <= key[1]:
                return self.format(random.choice(val), unicode(self.v))
            if isinstance(key,unicode) and isinstance(self.v,unicode) and self.v == key:
                return self.format(random.choice(val), self.v)
        if INWORDS and (isinstance(self.v, int) or isinstance(self.v, float)):
            return numeral.in_words(self.v)
        return unicode(self.v)
    def format(self, s, v):
        try:
            s = s % v
        except TypeError: # no params
            pass
        return s
        
class TextToken(object):
    def __init__(self, t):
        self.t = t
    def __call__(self):
        return self.t

def get_dicts(path):
    return [fname for fname in os.listdir(path) if fname.endswith(".yml")]

def load_bases(d):
    BASE.clear()
    for fname in d:
        egg = os.path.join(PATH, fname)
        LOG.debug("load base: %s", egg)
        BASE.update(yaml.load(open(egg)))

def generate(template, params):
    u"""
    >>> random.seed(1)
    >>> BASE.update(yaml.load(DICT_SAMPLE))
    >>> INWORDS = True
    >>> for row in csv.reader(CSV_SAMPLE, delimiter=";", quotechar='"'):
    ...     print generate(TEMPLATE_SAMPLE, row)
    Мобильник Gnusmas 1810g, имеет массу 49 кг, это вообщем скромно, цвет - светлозеленый.
    Мобильник Лыжи, имеет массу более ста килограмм, цвет - красный.
    Мобильник Лыжи2, располагает массой 1981 килограмм, цвет - .
    """
    tokenized = tokenizer_re.split(template)
    egg = []
    for t in tokenized:
        
        if token_dict.match(t):
            ct, dt = t[2:-1].split(":")
            try:
                v = params[int(ct)-1]
            except IndexError:
                v = ""
            try:
                if v.find(".") != -1:
                    v = float(v)
                else:
                    v = int(v)
            except ValueError:
                v = v.decode("utf-8","ignore")
            if not CACHE.has_key(dt):
                CACHE[dt] = yaml.load(open(os.path.join(PATH,dt)))
            egg.append(DictToken(v, CACHE[dt]))

        elif token_inwords.match(t):
            ct = t[2:-3]
            try:
                v = params[int(ct)-1]
                if v.find(".") != -1:
                    v = float(v)
                else:
                    v = int(v)
                v_inwords = numeral.in_words(v)
                egg.append(TextToken(v_inwords))
            except (IndexError, ValueError):
                pass
        elif token_re.match(t):
            ct = t[2:-1]
            if t.find("|")!=-1:
                egg.append(RandomToken(ct.split("|")))
            else:
                try:
                    v = params[int(ct)-1]
                except IndexError:
                    v = ""
                try:
                    if v.find(".") != -1:
                        v = float(v)
                    else:
                        v = int(v)
                except ValueError:
                    if type(v) != unicode:
                        v = v.decode("utf-8","ignore")
                egg.append(DictToken(v, BASE))
        else:
            egg.append(TextToken(t))
    return "".join([t() for t in egg])
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
