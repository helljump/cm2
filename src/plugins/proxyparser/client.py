#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import logging
import requests
from urlparse import urljoin
import yaml
import os
from lxml import html


log = logging.getLogger(__name__)


def parser():
    baseurl = u'http://xn--j1ahceh8f.xn--p1ai/'\
        'HTTP%D0%BF%D1%80%D0%BE%D0%BA%D1%81%D0%B8%D0%BB%D0%B8%D1%81%D1%82.aspx'
    page = 1
    pages = 5
    sess = requests.session()

    cd = os.path.dirname(__file__)

    headers_fname = os.path.join(cd, 'headers.yml')
    sess.headers = yaml.load(open(headers_fname))
    sess.headers['Referer'] = baseurl

    data_fname = os.path.join(cd, 'data.yml')
    if os.path.isfile(data_fname):
        data = yaml.load(open(data_fname))
    else:
        data = None

    while True:
        yield u'Читаем страницу: %i' % page # label
        yield (0, 0) # range

        if page == 1:
            rc = sess.get(baseurl)
        else:
            data['__EVENTARGUMENT'] = 'Page$%i' % page
            rc = sess.post(baseurl, data=data)
        assert rc.status_code == 200

        soup = html.fromstring(rc.content)

        # #dnn_ctr597_View_proxy-list_GridView2 > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2)
        rows = soup.xpath('//table[@id="dnn_ctr597_View_proxy-list_GridView2"]/tr[@valign="top"]')
        yield (0, len(rows)) # range

        c = 0
        for row in rows:
            addr = row.xpath('td[2]/text()')[0]
            portimage = row.xpath('td[3]/img/@src')[0]
            type_ = row.xpath('td[5]/table/tr/td/span/text()')[0]
            c += 1
            yield c # counter
            #if data is not None and type_.strip() != 'Elite':
            #    continue
            yield (addr, urljoin(baseurl, portimage)) # addr, port

        page += 1
        if page > pages or data is None:
            break


def main():

    for row in parser():
        if type(row) == unicode:
            print row.encode('cp1251')
        else:
            print row
    raw_input('done')

if __name__ == '__main__':
    main()
