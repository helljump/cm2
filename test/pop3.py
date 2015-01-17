#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from poplib import POP3
from email.parser import FeedParser
from email.header import decode_header
import re

link_re = re.compile("http://www\.unet\.com/cemail/.+")

pop = POP3('pop.yandex.ru')
pop.user('inna.haz')
pop.pass_('leyler')

msgs = len(pop.list()[1])
for i in range(msgs):
    parser = FeedParser()
    for j in pop.retr(i+1)[1]:
        parser.feed(j + "\n")
    msg = parser.close()
    subj = decode_header(msg['Subject'])[0] 
    subj = unicode( subj[0], subj[1] )
    if subj == u"uNet - Добро пожаловать в наше сообщество!":
        link = link_re.search(msg.as_string()).group(0)
        print "auth link", link
        #pop.dele(i)

pop.quit()
