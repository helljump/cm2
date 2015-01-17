#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import hashlib
from pidors import pidors

b = []

blocked = ['Adminchik-ADMINCHIK-PC', 'feb2013-plati-key05', 'Z155490765817',
]

for pidor in pidors:
    if pidor.find('@') > -1 or pidor[0].lower() == 'z' or pidor[0].lower() == 'r':
        blocked.append(pidor)

for pidor in blocked:
    m = hashlib.md5()
    m.update(pidor)
    b.append(m.hexdigest())

with open("pidorshash.py", "wt") as fout:
    fout.write("pidors = [\n")
    c = 0
    for item in b:
        fout.write("'%s', " % item)
        c += 1
        if c > 2:
            c = 0
            fout.write("\n")
    fout.write("]\n")
