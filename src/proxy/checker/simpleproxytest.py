#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import urllib2
import logging
import time

target_url = "http://www.google.com"
timeout = 1
inside_text="<title>Google</title>"

try:
    proxy_handler = urllib2.ProxyHandler({"http": "98.213.93.58:8085"})
    opener = urllib2.build_opener(proxy_handler)
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    t = time.time()
    req=urllib2.Request(target_url)
    response = opener.open(req, timeout=timeout)
    status = time.time() - t
except urllib2.HTTPError, err:
    logging.error("http code %s" % err.code)
except urllib2.URLError, err:
    logging.error("url error %s" % err)
except Exception, detail:
    logging.error("exception %s" % detail)
else:
    logging.debug("tested %f ms" % (status))
