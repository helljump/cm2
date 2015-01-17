#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__date__ = "07.11.2010 0:06:59"
__author__ = "snöa"

import logging
from engine.browser import Browser, FormMethod
import re
import random
import urllib

log = logging.getLogger(__name__)

TIMEOUT = 60
PROXYLIST = None

class SearchEngine(object):
    def __init__(self):
        if PROXYLIST:
            proxy = {"http":random.choice(PROXYLIST)}
        else:
            proxy = None
        self.br = Browser(proxy, timeout=TIMEOUT)

class ImageSize(object): ALL, LARGE, MEDIUM, SMALL = range(4)

class GoogleRu(SearchEngine):
    URL = "http://www.google.ru"
    IMAGEPATTERN = r"\\x3d(http://.+?)\\x26imgrefurl\\x3d(http://.+?)\\x26"

    def search(self, q):
        self.br.method = FormMethod.GET
        self.br.set_param("q", q)
        self.br.set_param("num", 10)
        url = "%s/search" % self.URL
        while True:
            soup = self.br.open(url)
            egg = soup.findAll("h3", {"class":"r"})
            if not egg:
                raise StopIteration()
            links = [link.a["href"] for link in egg]
            while links:
                yield links.pop()
            egg = soup.find("a", {"id":"pnnext"})
            if not egg: # no next page
                raise StopIteration()
            url = "%s%s" % (self.URL, egg["href"])

    def images(self, q, size=ImageSize.ALL):
        self.br.method = FormMethod.GET
        self.br.set_param("q", q)
        if size == ImageSize.LARGE:
            self.br.set_param("tbs", "isch:1,isz:l")
        if size == ImageSize.MEDIUM:
            self.br.set_param("tbs", "isch:1,isz:m")
        if size == ImageSize.SMALL:
            self.br.set_param("tbs", "isch:1,isz:i")
        url = "%s/images" % self.URL
        pattern = re.compile(self.IMAGEPATTERN, re.I)
        while True:
            soup = self.br.open(url)
            links = pattern.findall(self.br.source)
            if not links:
                log.debug("no links")
                raise StopIteration()
            while links:
                yield links.pop()
            egg = soup.find("a", {"id":"pnnext"})
            if not egg: # no next page
                raise StopIteration()
            url = "%s%s" % (self.URL, egg["href"])

class GoogleCom(GoogleRu):
    URL = "http://www.google.com"

class YouTube(SearchEngine):
    URL = "http://www.youtube.com"
    PATTERN = re.compile(r'<a href="(/watch\?v=[^>]+?)" class="video-thumb', re.I)
    def search(self, q):
        self.br.method = FormMethod.GET
        self.br.set_param("search_query", q)
        self.br.set_param("aq", "f")
        url = "%s/results" % self.URL
        while True:
            soup = self.br.open(url)
            links = self.PATTERN.findall(self.br.source)
            if not links:
                log.debug("no links")
                raise StopIteration()
            while links:
                egg = "%s%s" % (self.URL, links.pop())
                yield egg
            egg = soup.find("a", {"class":"yt-uix-pager-link"})
            if not egg:
                raise StopIteration()
            url = "%s%s" % (self.URL, egg["href"])

class YandexRu(SearchEngine):
    URL = "http://yandex.ru"
    IMAGEPATTERN = r"img_url=([^>]+?)&amp;"

    def search(self, q):
        self.br.method = FormMethod.GET
        self.br.set_param("text", q)
        url = "%s/yandsearch" % self.URL
        while True:
            soup = self.br.open(url)
            egg = soup.findAll("a", {"class":"b-serp-item__title__link"}) 
            if not egg:
                raise StopIteration()
            links = [link["href"] for link in egg]
            while links:
                yield links.pop()
            egg = soup.find("a", {"id":"next_page"}) 
            if not egg: # no next page
                raise StopIteration()
            url = "%s%s" % (self.URL, egg["href"])

    def images(self, q, size=ImageSize.ALL):
        self.br.method = FormMethod.GET
        self.br.set_param("text", q)
        self.br.set_param("stype", "image")
        if size == ImageSize.LARGE:
            self.br.set_param("isize", "large")
        if size == ImageSize.MEDIUM:
            self.br.set_param("isize", "medium")
        if size == ImageSize.SMALL:
            self.br.set_param("isize", "small")
        url = "%s/yandsearch" % self.URL
        pattern = re.compile(self.IMAGEPATTERN, re.I)
        while True:
            soup = self.br.open(url)
            links = pattern.findall(self.br.source)
            if not links:
                log.debug("no links")
                raise StopIteration()
            while links:
                egg = "http://%s" % urllib.unquote(links.pop())
                yield (egg, None)
            egg = soup.find("a", {"class":"b-pager__next"})
            if not egg: # no next page
                raise StopIteration()
            url = "%s%s" % (self.URL, egg["href"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    y = YouTube()
    for row in y.search(u"Роботы"):
        print row
