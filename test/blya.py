#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import urllib2, cookielib

BROWSER_HEADERS = [
("User-agent", "Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7"),
("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
("Accept-Language", "ru,en-us;q=0.7,en;q=0.3"),
("Accept-Charset", "windows-1251,utf-8;q=0.7,*;q=0.7"),
("Keep-Alive", "300"),
("Connection", "keep-alive"),
("Cache-Control", "max-age=0")
]

cj = cookielib.CookieJar()
http_handler = urllib2.HTTPHandler()
redirect_handler = urllib2.HTTPRedirectHandler()
https_handler = urllib2.HTTPSHandler()
cookie_handler = urllib2.HTTPCookieProcessor( cj )
proxy_support = urllib2.ProxyHandler()

opener = urllib2.build_opener(proxy_support, http_handler, https_handler, cookie_handler, redirect_handler)

opener.cookie_jar = cj
opener.addheaders = BROWSER_HEADERS

o = opener.open("http://www.ucoz.ru/main/?a=reg")
xml = o.read()

open("dump.html","wb").write(xml)
