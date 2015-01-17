#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = 'helljump'

import logging
import sys

if not hasattr(sys, "frozen"):
    sys.path.append('d:/work/cm2/src')
    sys.path.append('d:/work/cm2/src/edit')
    logging.basicConfig(level=logging.DEBUG)

from lxml import etree
from lxml.html.clean import Cleaner
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from spynner_dialog import SpynnerDialog
from antigate import get_service
from random import choice


log = logging.getLogger(__name__)


class ABParserError(Exception):
    pass


class RusParser(object):

    ERRORS = 5
    BASEURL = 'http://www.rusarticles.com/'
    ARTICLEPATH = '//div[@class="article_pg"]'
    TITLEPATH = '//h1[@itemprop="name"]/text()'
    TEXTPATH = '//index'
    BTNSEL = 'input[name=search_btn]'

    def __init__(self, parent, proxylist=None, sleep=60):
        self.browser = SpynnerDialog(parent)
        self.cleaner = Cleaner()
        self.captcha = get_service()
        self.proxylist = proxylist
        self.sleep = sleep
        self.errors = ABParser.ERRORS
        self.done = 0

    def _set_random_proxy(self):
        if self.proxylist:
            self.browser.set_proxy(choice(self.proxylist))

    def get_articles(self, query):
        self.browser.headers.append(('Referer', self.BASEURL))
        self.browser.show()
        self.browser.message(u'Подключаемся')
        self._set_random_proxy()
        self.browser.load(self.BASEURL, load_timeout=60)
        self.browser.wait(5)
        self.ban_test()
        self.captcha_test()
        if self.browser.webframe.findFirstElement('input[name=q]').isNull():
            raise Exception('no input field')
        self.browser.fill('input[name=q]', query)
        self.browser.click(self.BTNSEL, wait_load=True)
        nextlink = 'a[class=next]'
        while True:
            pageurl = self.browser.url

            # div.article_row > div > h3 > a
            for articleurl in self.browser.soup.xpath('//div[@class="article_row"]/div/h3/a/@href'):
                self._set_random_proxy()
                self.browser.load(articleurl, load_timeout=60)
                if self.ban_test():
                    continue
                self.captcha_test()
                spam = self.browser.soup
                try:
                    article = spam.xpath(self.ARTICLEPATH)[0]
                    title = article.xpath(self.TITLEPATH)[0]
                    text = article.xpath(self.TEXTPATH)[0]
                    cleantext = etree.tostring(self.cleaner.clean_html(text), pretty_print=True, encoding=unicode)
                    yield(title, cleantext)
                    self.done += 1
                    self.browser.message(u'Статья: %s(%i)' % (title, self.done))
                except Exception:
                    log.exception("article parser")
                    self.browser.dump()
            self._set_random_proxy()
            self.browser.load(pageurl, load_timeout=60)
            if self.ban_test():
                continue
            self.captcha_test()
            if self.browser.webframe.findFirstElement(nextlink).isNull():
                break
            self.browser.message(u'Следующая страница')
            self.browser.click_link(nextlink)

    def captcha_test(self):
        cnt = 2
        while cnt > 0:
            img = self.browser.webframe.findFirstElement('img[id=captchaImage]')
            if img.isNull():
                return
            data = self.browser.extract_image('img[id=captchaImage]')
            self.browser.message(u'Капча на экране, обращаемся к китайцам..')
            th = self.captcha.create_thread(data)
            th.run()
            if not th.result:
                QMessageBox.critical(self.browser, u"Парсер", u"Ошибка распознования капчи: %s" % th.error)
                self.browser.hide()
                raise ABParserError('captcha error [%s]' % th.error)
            self.browser.wk_fill('input[id=captchaInput]', th.result)
            self.browser.wait(1)
            self.browser.click('button[id=submitObject]', wait_load=True)
            self.browser.message(u'Отправили ответ')
            cnt -= 1

    def ban_test(self):
        if not self.errors:
            QMessageBox.critical(self.browser, u"Парсер", u'Вы забанены сервисом. Следующий раз делайте '\
                u'более длительную задержку между вызовами.')
            self.browser.dump()
            self.browser.hide()
            raise ABParserError('banned')
        if self.browser.html_contains('(?i)Forbidden'):
            egg = self.sleep / self.errors
            self.errors -= 1
            self.browser.message(u'Бан, осталось попыток: %i, ждём %i с' % (self.errors, egg))
            self.browser.wait(egg)
            return True
        else:
            self.errors = ABParser.ERRORS
            return False


class ABParser(RusParser):

    BASEURL = 'http://www.articlesbase.com/'
    ARTICLEPATH = '//div[@id="main"]'
    TITLEPATH = '//h1[@itemprop="name"]/text()'
    TEXTPATH = '//div[@class="post"]'
    BTNSEL = 'input[class=search_btn]'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = ABParser(None, proxylist=['192.168.1.23:8000'])
    for art in parser.get_articles(u'robots'):
        pass
