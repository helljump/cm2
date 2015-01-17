#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from engine.browser import Browser, FormMethod
import logging

def get_links(q, num=20):

    url = "http://yandex.ru/yandsearch"

    br = Browser()
    links = []
    p=0
    while len(links)<num:
        br.method = FormMethod.GET
        br.set_param("text", q)
        if p>0:
            br.set_param("p", p)
        soup = br.open(url)
        egg = soup.findAll("a", {"class":"cs"})
        if not egg:
            break
        for link in egg:
            links.append("%s" % link["href"])
        p+=1

    logging.debug("yandex links found: %i", len(links))
    
    return links

if __name__ == "__main__":
    l = get_links(u"free proxy list")
    print l
