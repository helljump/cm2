#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

import sqlite3 as sqlite
from collections import defaultdict

USERS_DB_NAME = 'users.sqlite'
users_db = sqlite.connect(USERS_DB_NAME)

accum = defaultdict(list)

c = users_db.cursor()
softname = "treeedit"
rc = c.execute('select keyname, sysname from users where keyname not like "%%snoa%%" and softname="%s" order by keyname' % softname)
for row in rc:
    accum[row[0]].append(row[1])

pidorsset = set()
    
for k,v in accum.items():
    egg = set(v)
    if len(egg)>2:
        #print k, ":" , ", ".join(egg)
        pidorsset.add(k)
        pidorsset |= egg

print len(pidorsset), "pidors"
        
pidorsset -= set([
    "snoa-MULYAZH",
    "jkvoka@gmail.com2","tom-TOMSON","Z107871011505","Papi-TT-SVZ3QO6W7CNN",
    "Admin-MICROSOF-C9D6F3","Admin-MICROSOF-1A39F2","Z197532265446",
    "Dima-PADAYATRA","dima-PADAYATRA","main-TATO",
    "kam-K", "kam1-KAM",
    "yuri_kirilin@mail.ru", "yuri-WIN7", "Yuri-KHINCO",
    "Admin-H1", "dovbyshv@mail.ru", # "Откуда другие не знаю" :/
    "sales@bel-seo.ru", "SiG-X997",
    "evgenij_k@list.ru", "1-SAMLAB", "Office-SAMLAB",
    "Administrateur-ZZ-92A7W51YBHHS", "zZ-ZZ-8AC2E607YM87",
    ])

pidorsset |=set([
    # кредитчик, не ходил на форум, тупил, вернули 35 баксов
    "Admin-36EEA004231E4FD","Z535321499778",
    "Z237980445101", # не понравился синонимайзер, вернул бабло
    "cuba-plati-key01", # не стал разбираться, ушлепан
    ])

print len(pidorsset), "pidors after filter"
    
with open("pidors.py","wt") as fout:
    fout.write("pidors = [\n")
    c = 0
    for item in pidorsset:
        fout.write("'%s', " % item)
        c+=1
        if c>4:
            c=0;
            fout.write("\n")
    fout.write("]\n")
