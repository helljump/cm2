#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from email.parser import Parser
from email.header import decode_header

parser = Parser()
msg = parser.parse( open("mail1", 'rb') )
print msg['Subject']
print unicode(decode_header(msg['Subject'])[0][0])
print msg['X-Mailer']
