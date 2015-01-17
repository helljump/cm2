#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib2
import re

address_template = re.compile("(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{2,4})")

proxylist = """http://www.free-proxy-list.info/page/1/
""".split()

http_handler = urllib2.HTTPHandler()
opener = urllib2.build_opener(http_handler)
for url in proxylist:
    response = opener.open(url)
    for item in address_template.finditer(response.read()):
        print item.groups(0)[0]
