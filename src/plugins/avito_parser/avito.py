#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging
import spynner
import re
from urlparse import urlsplit
from urlparse import urljoin
from datetime import datetime, timedelta
from random import choice
import sys
import os


log = logging.getLogger(__name__)


class Avito():

    USERAGENT = "Mozilla/5.0 (Windows NT 6.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"

    try:
        from donate import AVITOLINKS, AVITOPAGES
    except ImportError as err:
        AVITOLINKS = 4
        AVITOPAGES = 1

    MONTHS = {
        u'янв.': 1,
        u'фев.': 2,
        u'мар.': 3,
        u'апр.': 4,
        u'май':  5,
        u'июнь': 6,
        u'июль': 7,
        u'авг.': 8,
        u'сен.': 9,
        u'окт.': 10,
        u'ноя.': 11,
        u'дек.': 12,
    }

    YESTERDAY = re.compile(u'вчера в (\d\d:\d\d)', re.U|re.S)
    TODAY = re.compile(u'сегодня в (\d\d:\d\d)', re.U|re.S)
    OTHERDAY = re.compile(u'(\d{1,2}) ([\w\.]+) в (\d\d:\d\d)', re.U|re.S)

    def __init__(self, baseurl, savepath, proxies=None, timeout=30, attempts=3):
        self.browser = spynner.Browser(download_directory=savepath, debug_level=spynner.WARNING,
            user_agent=Avito.USERAGENT)
        self.browser.set_url_filter(self.url_filter)
        if not hasattr(sys, "frozen"):
            self.browser.show(False)
        self.baseurl = baseurl
        self.proxies = proxies
        self.savepath = savepath
        self.timeout = timeout
        self.attempts = 3

    def load(self, *args, **kwargs):
        c = self.attempts
        rc = None
        while c:
            if self.proxies:
                self.browser.set_proxy(choice(self.proxies))
            rc = self.browser.load(*args, **kwargs)
            if self.browser.errorCode in [200, 301]:
                break
            log.warning('Load error code %s', self.browser.errorCode)
            c -= 1
        return rc

    def url_filter(self, operation, url):
        egg = urlsplit(url)
        if 'avito' not in egg[1]:
            return False
        else:
            return True

    def _extract_image(self, el):
        image = QImage(el.geometry().size(), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        el.render(painter)
        painter.end()
        return image

    def _get_phoneimage(self):
        c = 20
        phoneimage = None
        while True:
            egg = self.browser.webframe.findFirstElement('span.phone>img')
            phoneurl = unicode(egg.attribute('src'))
            if 'ajax-loader.gif' not in phoneurl:
                phoneimage = self._extract_image(egg)
                break
            self.browser.wait(0.5)
            if not c:
                break
            else:
                c -= 1
        return phoneimage

    def _parse_date(self, s):
        d = datetime.now()

        m = self.YESTERDAY.search(s)
        if m:
            ofs = timedelta(days=-1)
            hh, mm = m.group(1).split(':')
            d = d.replace(hour=int(hh), minute=int(mm))
            d += ofs
            return d

        m = self.TODAY.search(s)
        if m:
            hh, mm = m.group(1).split(':')
            d = d.replace(hour=int(hh), minute=int(mm))
            return d

        m = self.OTHERDAY.search(s)
        if m:
            day = int(m.group(1))
            hh, mm = m.group(3).split(':')
            m = self.MONTHS[m.group(2)]
            y = d.year
            if m<d.month:
                y -= 1
            d = d.replace(year=y, month=m, day=day, hour=int(hh), minute=int(mm))
            return d

        return d

    def parse_item_page(self, url):
        self.browser.headers = [('Referer', url)]
        self.load(url, load_timeout=self.timeout)
        self.browser.click('a[class="icon-link pseudo-link"]', wait_load=False) # load phone

        item = self.browser.webframe.findFirstElement('div.item')
        if item.isNull():
            return None

        title = unicode(item.findFirst('h1').toPlainText())
        datestring = unicode(item.findFirst('div.item_subtitle').toPlainText())
        datestring = self._parse_date(datestring)
        price = unicode(item.findFirst('span.p_i_price>strong>span').toPlainText())
        price = re.sub('\D', '', price)
        seller = unicode(item.findFirst('div#seller>strong').toPlainText())
        phoneimage = self._get_phoneimage()
        intro = unicode(item.findFirst('dl.description-expanded').toPlainText())
        full = unicode(item.findFirst('dl.description-text').toPlainText())
        city = unicode(item.findFirst('div#map>a').toPlainText())

        egg = item.findFirst('span#toggle_map').parent()
        egg.removeAllChildren()
        address = unicode(egg.parent().toPlainText())

        images = []
        egg = item.findFirst('img#big-picture')
        if not egg.isNull():
            i = urljoin(url, unicode(egg.attribute('src')))
            images.append(i)
        for egg in item.findAll('div[class="ll fit"]>a'):
            i = urljoin(url, unicode(egg.attribute('href')))
            images.append(i)

        for i in range(len(images)):
            imageurl = images[i]
            images[i] = imageurl.split('/')[-1]
            fnout = os.path.join(self.savepath, imageurl.split('/')[-1])
            if os.path.isfile(fnout):
                continue
            log.debug('download %s to %s', imageurl, fnout)
            with open(fnout, 'wb') as fout:
                self.browser.download(imageurl, fout, timeout=self.timeout)
                fout.close()

        return (title, city, address, phoneimage, intro, full, seller, price, str(datestring.date()),
            datestring.strftime('%H:%M:%S'), images)

    def parse_items(self):
        pageurl = self.baseurl
        pages = self.AVITOPAGES
        while pages:
            self.browser.headers = [('Referer', pageurl)]
            yield u'Получаем страницу: %s' % pageurl
            self.load(pageurl, load_timeout=self.timeout)
            webframe = self.browser.webframe
            egg = webframe.findFirstElement('a.logo-auto')
            if egg.isNull():
                raise Exception(u'Слишком много дохлых прокси или Вас забанили.')
            els = webframe.findAllElements('h3.t_i_h3>a.second-link')
            if not len(els):
                break
            links = self.AVITOLINKS
            for el in els:
                url = urljoin(self.baseurl, unicode(el.attribute('href')))
                yield self.parse_item_page(url)
                if links:
                    links -= 1
                else:
                    break
            egg = webframe.findFirstElement("a.next")
            if egg.isNull():
                break
            pages -= 1
            pageurl = urljoin(self.baseurl, unicode(egg.attribute('href')))
        self.browser.hide()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    proxies = None#map(str.strip, open(r'd:\work\cm2\test\proxylist_loc.txt', 'r').readlines())
    p = Avito('http://www.avito.ru/lipetsk/avtomobili_s_probegom', os.path.dirname(__file__), proxies)

    #for i in p.parse_items():
    #    if type(i) is tuple:
    #        print i

    #print p.parse_item_page('http://www.avito.ru/lipetsk/avtomobili_s_probegom/lada_priora_2011_203844328')
    print p.parse_item_page('http://www.avito.ru/lipetsk/kvartiry/4-k_kvartira_80_m_410_aet._102563389')
    #print p.parse_item_page('http://www.avito.ru/lipetsk/avtomobili_s_probegom/volkswagen_passat_1997_203033341')
    #raw_input('done')
