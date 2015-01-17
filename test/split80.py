#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import re


text = open(u"граблики.html","rt").read()
text = unicode(text,"utf-8","ignore")

text = re.sub("([^>]{20,})\s", "\n[[\1]]\n", text)

#text = "\n-+-\n".join(egg)

open("test.txt","wt").write(text.encode("utf-8","ignore"))
