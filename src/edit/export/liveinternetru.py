#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

import mimetools
import urllib2
import datetime
import logging
from xml.sax.saxutils import escape

USERNAME = "unit808"
PASSWORD = "oIxH0HlS21lS1JlR3EhD"
INTERFACE = "http://www.liveinternet.ru/offline_main.php"

log = logging.getLogger(__name__)

XML_ADDPOST = u"""<?xml version="1.0" encoding="UTF-8"?>
<QUERIS username="%(username)s" password="%(password)s">
 <query QID="1" TYPE="3">
  <headerofpost>%(header)s</headerofpost>
  <message>%(message)s</message>
  <parseurl>1</parseurl>
 </query>
</QUERIS>
"""

DATA = u"""--%(boundary)s
Content-Disposition: form-data; name="xmlfile"; filename="xmlfile"
Content-Type: text/xml; charset=UTF-8

%(query)s

--%(boundary)s
"""

boundary = "---------------------%s" % mimetools.choose_boundary()

query = XML_ADDPOST % {
    "username":USERNAME,
    "password":PASSWORD,
    "header":escape(u"Заголовок поста от [%s]" % datetime.datetime.now()),
    "message":escape(u"Текст о <b>космических</b> космонавтах.\nУрааа!")
}

data = DATA % {
    "boundary":boundary,
    "query":query
}
data = data.encode("utf-8","replace")

headers = {
    "Content-Type": "multipart/form-data, boundary=%s" % boundary,
    "Content-Length": "%i" % len(data)
}

r = urllib2.Request(INTERFACE, data, headers)
rc = urllib2.urlopen(r)

log.debug(rc.read().decode("cp1251"))
