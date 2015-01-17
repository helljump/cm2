#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging 
log = logging.getLogger(__name__)
#log.setLevel(logging.WARNING)

from BeautifulSoup import BeautifulSoup
from constants import encodings
from pytils.translit import slugify
import chardet
#from logging import debug, warning, exception, error
import os
import re
import urllib
import urllib2
import httplib
import cookielib
import mimetools, mimetypes
import socket
import time
import ConfigParser

class FormMethod(object): (POST, GET, MULTIPART) = range(3)
class BrowserError(Exception): pass

def get_browser_headers():
    default_headers = [
        ("User-agent", "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; FDM)"),
        ("Accept", "image/gif,image/x-xbitmap,image/jpeg,image/pjpeg,application/x-ms-application,application/x-ms-xbap,application/vnd.ms-xpsdocument,application/xaml+xml,*/*"),
        ("Accept-Language", "ru"),
        ("Connection", "keep-alive")
    ]

    try:
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.read("browser.ini")
        default_headers = config.items('headers')
    except Exception:
        log.debug("using default browser headers")

    return default_headers

class Browser(object):

    """ Умелое прикидывание браузером """

    STRIP_TAGS = re.compile(r'<(?!(?:a\s|/a|!))[^>]*>')
    META_ENCODING = re.compile("<meta[^>]*charset=([^;\"\']*)[^>]*?>", re.I)

    def __init__(self, proxy=None, dbg=False, timeout=30):
        
        """ Создаем кучу хандлеров и куков """
        
        log.debug("init Browser")
        socket.setdefaulttimeout(timeout)
        if proxy:
            log.debug("use proxy %s", proxy)
        cj = cookielib.CookieJar()
        #cj = cookielib.MozillaCookieJar("browser.cookies")
        http_handler = urllib2.HTTPHandler(debuglevel=dbg)
        redirect_handler = urllib2.HTTPRedirectHandler()
        https_handler = urllib2.HTTPSHandler(debuglevel=dbg)
        cookie_handler = urllib2.HTTPCookieProcessor(cj)
        proxy_support = urllib2.ProxyHandler(proxy)

        self.opener = urllib2.build_opener(proxy_support, http_handler, https_handler, 
            cookie_handler, redirect_handler)

        self.opener.cookie_jar = cj
        self.source = ""
        self.soup = None
        self.values = {}
        self.response = None
        self.encoding = "utf-8"
        self.method = FormMethod.POST
        self.referer = None
        self.opener.addheaders = get_browser_headers()
        self.timeout = timeout
        self.post_files = {}
        
        #self.parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
        
    def strip_tags(self, text):
        
        """ Выкусываем хтмл теги, вспомогательная функция """
        
        text = self.STRIP_TAGS.sub('', text)
        return text.strip()

    def exchange_referer(self, url):
        
        """ Меняем реферера в заголовках открывателя на последний открытый адрес """
        
        numba = -1
        for i in range(len(self.opener.addheaders)):
            if self.opener.addheaders[i][0] == "Referer":
                numba = i
                break;
        else:
            self.opener.addheaders.append(("Referer", url))
            log.debug("set referer to %s", url)
        if numba != -1:
            self.opener.addheaders[numba] = ("Referer", url)
            log.debug("exchange referer to %s", url)

    def _detect_image_ext(self, fname):
        ext = os.path.splitext(fname.lower())
        exts = {".jpg":"image/pjpeg",
                ".jpeg":"image/pjpeg",
                ".png":"image/png",
                ".gif":"image/gif"}
        return exts.get(ext, "image/pjpeg")

    def make_multipart_request(self, url):
        ''' 
        Формируем multipart запрос
        @param url: адрес запроса
        параметры берем из self.values
        файлы берем из self.post_files
        
        @return: сформированный запрос
        '''
        params = {}
        params["boundary"] = "-----------------------------%s" % mimetools.choose_boundary()
        params["fboundary"] = params["boundary"] 
        bodyfrag = []
        bodyfrag.append("--%(boundary)s" % params)
        bodyfrag.append("Content-Disposition: form-data; name=\"method\"")
        bodyfrag.append("")
        bodyfrag.append("post")
        #spam = 0
        for (k, v) in self.values.items():
            params["key"] = k
            params["value"] = v
            #spam += len(params["value"]) - len(v) #fixme
            bodyfrag.append("--%(boundary)s" % params)
            bodyfrag.append("Content-Disposition: form-data; name=\"%(key)s\"" % params)
            bodyfrag.append("")
            #egg = u"%(value)s" % params
            bodyfrag.append(params["value"])
            
        #добавить в отправку файлы из self.post_files
        
        if len(self.post_files) > 1:
            params["fboundary"] = "-----------------------------%s" % mimetools.choose_boundary()
            bodyfrag.append("--%(boundary)s" % params)
            bodyfrag.append("Content-Disposition: form-data; name=\"files\"")
            bodyfrag.append("Content-Type: multipart/mixed; boundary=%(fboundary)s" % params)
            bodyfrag.append("")
     
        for (k, v) in self.post_files.items():
            params["name"] = k
            params["data"] = v[1]
            params["fname"] = v[0]
            #content_type = self._detect_image_ext(k)
            content_type = mimetypes.guess_type(v[1])[0] or 'application/octet-stream'
            bodyfrag.append("--%(fboundary)s" % params)
            bodyfrag.append("Content-Disposition: form-data; name=\"%(name)s\"; filename=\"%(fname)s\"" % params)
            bodyfrag.append("Content-Type: %s" % content_type)
            bodyfrag.append("")
            bodyfrag.append(params["data"])
            
        if len(self.post_files) > 1:
            bodyfrag.append("--%(fboundary)s--" % params)
        
        bodyfrag.append("--%(boundary)s--" % params)
        bodyfrag.append("")
                
        data = "\r\n".join(map(str,bodyfrag))
        
        headers = {
            'Content-Type' : 'multipart/form-data; boundary=%(boundary)s' % params,
            'Content-Length' : '%i' % len(data)
            #'Content-Length' : '%i' % len(data.encode(self.encoding,"ignore")) #bad!!!
        }

        r = urllib2.Request(url, data, headers)
        #logging.info("%i == %i" % ((len(data)+spam), len(r.get_data())) )

        return r

    def _timeout_open(self, req, data=None):
        """ 
        обработка запроса с хитрым таймаутом
        
        @param req: запрос
        @param data: данные для отправки
        @return: полученные данные
        @note: служебную инфу в self.respone
        """
        socket.setdefaulttimeout(self.timeout)
        t = time.time()
        while time.time() - t < self.timeout:
            try:
                self.response = self.opener.open(req, data, timeout=self.timeout)
                #help(self.opener.open)
                log.debug("response status: %i url: %s" % (self.response.code, self.response.url))
                source = self.response.read()
                self.response.close()
                return source
            except httplib.HTTPException, err:
                log.error("httplib.HTTPException [%s]", err)
            except urllib2.HTTPError, err:
                log.error("urllib2.HTTPError [%s]", str(err.code))
                if err.code == 404:
                    raise BrowserError("%s" % err)
            except urllib2.URLError, err:
                log.error("urllib2.URLError [%s]", str(err.reason[0]))
                if err.reason[0] == 11001: #не удалось определить адрес хоста
                    raise BrowserError("%s" % err)
                if err.reason[0] == 10060: #timeout
                    pass
            except socket.timeout, err:
                log.error("socket.timeout [%s]", err)
            time.sleep(1)
        raise BrowserError("%s" % err)

    def open(self, url):
        
        """ Получаем данные с урла, определяем кодировку
        создаем суп, детектим тип форм """
                
        #поменяли реферера
        if self.referer:
            self.exchange_referer(self.referer)
        
        if self.values:
            if self.method == FormMethod.MULTIPART:
                log.debug("open url[MULTIPART] %s" % url)
                r = self.make_multipart_request(url)
                source = self._timeout_open(r)
            elif self.method == FormMethod.GET:
                data = urllib.urlencode(self.values)
                log.debug("open url[GET] %s" % url)
                source = self._timeout_open("%s?%s" % (url, data))
            else:
                data = urllib.urlencode(self.values)
                log.debug("open url[POST] %s" % url)
                source = self._timeout_open(url, data)
        else:
            source = self._timeout_open(url)

        #определили кодировку        
        m = self.META_ENCODING.search(source)
        if m:
            codepage = encodings[ m.groups(0)[0].replace("-", "").lower() ]
            log.debug("encoding detected from meta %s" % codepage)
        else:
            codepage = encodings[ chardet.detect(source[:1024])["encoding"].replace("-", "").lower() ]
            log.debug("encoding detected by chardet(ugly page) %s" % codepage)
        self.encoding = codepage
        
        #сварили суп
        #UnicodeDecodeError: 'utf8' codec can't decode byte 0xd0 in position 6670: unexpected end of data
        log.debug("encoding") 
        self.source = unicode(source, codepage, "ignore")

        log.debug("heh, soupin'") 
        
        #self.soup = self.parser.parse(self.source)
        self.soup = BeautifulSoup(self.source)
        
        self.detect_method()
            
        #запомнили реферера и скопировали скрытеы поля ввода
        self.referer = self.response.url
        self.values = {}
        self.post_files = {}
        self.copy_hidden()

        log.debug("return soup") 
        return self.soup
        
    def detect_method(self, soup=None):
        #определили метод передачи параметров
        if soup is None:
            soup = self.soup.find("form")
        #logging.debug("--->" + str(soup))
        if soup is None:
            return
        m = soup.get('method', 'get')
        if m.lower() == 'post':
            if soup.get('enctype', '').lower() == "multipart/form-data":
                self.method = FormMethod.MULTIPART
                log.debug("method in form [MULTIPART]")
            else:
                self.method = FormMethod.POST
                log.debug("method in form [POST]")            
        else:
            self.method = FormMethod.GET
            log.debug("method in form [GET]")
        
    def select_form(self, nr= -1, attrs={}):
        self.values = {}
        if nr > -1:
            form = self.soup.findAll("form")[nr]
        elif attrs:
            form = self.soup.find("form", attrs=attrs)
        else:
            raise BrowserError("form not found")
        #print form
        self.copy_hidden(form)
        self.detect_method(form)
        log.debug("form selected, hidden copied")

    def dump(self, fname=None):
        
        """ дампим текущий исходняк в файл, если имя не задано, берем его из урла """
        
        if not fname:
            fname = "%s.html" % slugify(self.referer)
        log.debug("dump source to %s" % fname)
        rc = open(fname, "wb")
        rc.write(self.source.encode("utf-8","ignore"))
        rc.close()
    
    def set_param(self, name, value):
        
        """ добавляем параметр вызова """
        if type(value) is unicode:
            value = value.encode(self.encoding)
        if not type(value) is str:
            value = str(value)
        log.debug("set_param [%s]" % name)
        self.values[name] = value

    def set_file(self, name, source, fname='file'):
        "добавляем в отправляемую форму файл"
        if type(source) is file: 
            data = source.read()
            fname = os.path.basename(source.name)
        else:
            data = source
        self.post_files[name] = (fname, data)

    def copy_hidden(self, soup=None):
        
        """ копируем скрытые поля в параметры следующего вызова """
        
        log.debug("--> copy_hidden")
        
        if not soup:
            soup = self.soup.find("form")
            #debug(soup)
        
        if not soup:
            log.debug("FORM not found")
            return
            
        for hidden_field in soup.findAll("input", attrs={"type":"hidden"}):
            try:
                self.set_param(hidden_field["name"], hidden_field["value"])
                log.debug("copy hidden [%s]" % hidden_field["name"])
            except KeyError:
                log.warning("hidden input no has name or value(no nam pohuy)")

        #log.debug("--> copy_hidden")
    
    def find_tag(self, tag, attr, value):
        
        """ ищем тег в супе """
        
        egg = self.soup.find(tag, attrs={attr:value})
        if egg is None:
            log.exception("find tag error [%s]" % tag)
            raise BrowserError("tag [%s] not found" % tag)
        return egg

    def get_data(self, url):
        
        """ получаем данные с урла(для изображений) """
        
        log.debug("get_data %s" % url)
        data = self._timeout_open(url)

        return data
    
    def img(self, src):
        
        """ получаем src аттрибут изображения """
        
        return self.find_tag("img", "src", src)["src"]
    def link(self, href):

        """ получаем href аттрибут ссылки """

        return self.find_tag("a", "href", href)["href"]

    def input(self, name):
        
        """ получаем value аттрибут поля ввода """

        return self.find_tag("input", "name", name)["value"]

    def search(self, regex):
        return re.search(regex, self.source, re.I | re.U)

    def url_is_alive(self, url):
        socket.setdefaulttimeout(self.timeout)        
        try:
            response = self.opener.open(url, timeout=self.timeout)
            response.close()
            return response.code==200
        except Exception, err:
            log.error("url_probe %s", err)
        return False

if __name__ == '__main__':
    br = Browser()
    br.open("http://www.kinopoisk.ru/level/1/film/300/")
    br.dump()
    
