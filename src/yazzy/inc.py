#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import unicodecsv as csv
import codecs

d = {}

finp = open("fullthematik_old.csv", 'rb')
reader = csv.reader(finp, encoding='utf-8', delimiter=';', quotechar='\"')
for row in reader:
    d[row[0]] = row[1]

finp = codecs.open("ru_sinonim_morf270046.txt", 'r', 'cp1251')
for row in finp.readlines():
    k, v = row.split(',')
    d[k.strip()] = v.strip()

fout = open("fullthematik.csv", 'wb')
writer = csv.writer(fout, encoding='utf-8', delimiter=';', quotechar='\"', quoting=csv.QUOTE_NONNUMERIC)
for k, v in d.items():
    writer.writerow([k, v])
