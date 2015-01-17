#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
import itertools
import re
import logging

text = u"""когда был [ленин|сталин|вовчик] [маленький|большой|злой]
с [кудрявой|лысой] головой
он тоже [бегал|ползал|прыгал] в [валенках|тапках|коньках]
по горке ледяной"""

text = unicode(open("market.template.txt").read())

template = re.compile("(\[[\|\w\s']+\])", re.U)

spam = []
for token in template.split(text):
    if template.match(token):
        spam.append( token[1:-1].split("|") )
    else:
        spam.append( [token] )

for egg in itertools.product(*spam):
    print "".join(egg)
    print "-"*80
