#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from engine.browser import Browser, FormMethod
import logging

def get_links(q, num=20):

    url = "http://www.google.ru/search"
    br = Browser()
    p=0
    links = []
    links_on_page = 10
    
    while len(links)<num:
        br.method = FormMethod.GET
        br.set_param("q", q)
        br.set_param("num", links_on_page)
        if p>0:
            br.set_param("start", p)
        soup = br.open(url)

        egg = soup.findAll("a", {"class":"l"})
        if not egg:
            break
            
        for link in egg:
            if link["href"].find(url)==-1:
                links.append("%s" % link["href"])
        p += links_on_page

    logging.debug("google links found: %i", len(links))
    
    return links

if __name__ == "__main__":
    l = get_links(u"free proxy list")
    print l