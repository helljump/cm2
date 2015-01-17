#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import pyDes
import pickle

#http://blap.ru/exchange/get_fingerprint.7z

with open('fp.bin', 'rb') as fout:
    data = fout.read()
    h = 'savuyg9734gf;sd81g30f8g1[;4444444gahjldsfg9714pfgwhgd;lkfhv'
    d = pyDes.des(h[5:13], padmode=pyDes.PAD_PKCS5)
    e = d.decrypt(data)
    p = pickle.loads(e)
    print p
    print p['system'].decode('cp1251')
