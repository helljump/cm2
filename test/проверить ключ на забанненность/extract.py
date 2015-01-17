#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

import sqlite3 as sqlite

users_db = sqlite.connect('users.sqlite')
egg = set()
c = users_db.cursor()
rc = c.execute('select * from users where keyname="WMID014428692510"')
for row in rc:
    egg.add(row[1])
c.close()
print egg