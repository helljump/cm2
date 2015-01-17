#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from engine.browser import Browser, BrowserError
import logging

from BeautifulSoup import Comment
import random

VALID_TAGS = 'strong em p b i ul li br'.split()
VALID_ATTRS = 'href'.split()
BLACKLIST_TAGS = 'script style'.split()

def sanitize_soup(soup, valid_tags=VALID_TAGS, valid_attrs=VALID_ATTRS):
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        tag.attrs = [(attr, val) for attr, val in tag.attrs
                         if attr in valid_attrs]
        if tag.name in BLACKLIST_TAGS:
            tag.extract()
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    return soup.renderContents()

class ParserError( Exception ): pass
class StopException( Exception ): pass

HTML_HEAD = "<html><head><meta http-equiv=\"content-type\" content=\"text/html;charset=%s\"></head><body>\n"
HTML_TAIL = "</body></html>"

class ParserCode(object): (NOLINKS, ERROR, DATA) = range(3)

def write_cmsimple(fout, articles, articles_in_cat):
    '''запись симпла с разбивкой'''
    fout.write(HTML_HEAD % "utf-8")
    try:
        while articles:
            fout.write("<h1>%s</h1>\n" % articles[0]["title"])
            for i in range( random.randint(*articles_in_cat) ): #@UnusedVariable
                article = articles.pop(0)
                fout.write("<h2>%s</h2>\n" % article["title"])
                fout.write("%s\n" % article["text"])
    except IndexError:
        pass #list is empty
    fout.write(HTML_TAIL)
    
def parse(baseurl, phrase, articles_amount, proxy, queue):
    br = Browser(proxy, timeout=30)
    url = baseurl
    try:
        br.open(url)
    except:
        return
    br.set_param("q",phrase)
    br.set_param("search_btn",u"Search")
    form = br.soup.find("form")
    if not form:
        queue.put_nowait((ParserCode.NOLINKS,))
        return
    link = form['action']
    findlink = url + link
    page = 1
    articles = []
    try:
        while len(articles)<articles_amount:
            br.set_param("q",phrase)
            if page>1:
                br.set_param("page",page)
            br.open(findlink)
            links = br.soup.findAll("h3")
            if not links:
                queue.put_nowait( (ParserCode.NOLINKS,) )
                raise StopException("no more links")
            #if stopevent and stopevent.is_set():
            #    raise StopException("catch stopevent")
            for header in links:
                link = header.a['href']
                logging.debug("link %s" % link)
                if len(articles)==articles_amount:
                    raise StopException("parse job complete")
                #if stopevent and stopevent.is_set():
                #    raise StopException("catch stopevent")
                try:
                    br.open(link)
                    h1 = br.soup.find("h1")
                    if not h1:
                        raise ParserError("no title(H1) in article")
                    title = " ".join(h1.contents)
                    #<div class="article_cnt KonaBody">
                    content = br.find_tag("div", "class", "article_cnt")
                    #content = br.find_tag("div", "class", "article_cnt KonaBody")
                    #content = br.find_tag("div", "id", "hypercontext")
                    if not content:
                        raise ParserError("no content in article")
                    text = unicode( sanitize_soup(content) )
                    item = {"title":title, "text":text}
                    if queue:
                        queue.put_nowait( (ParserCode.DATA, item) )
                    articles.append( item )
                except BrowserError, err:
                    queue.put_nowait( (ParserCode.ERROR, err) )
                    logging.error("%s" % err)
            page += 1
    except StopException, err:
        logging.debug("StopException %s" % err)
    except Exception, err:
        queue.put_nowait( (ParserCode.ERROR, err) )
        logging.exception("Exception %s" % err)
    logging.debug("articles parsed %i" % len(articles))
    return articles

def parse_rusarticles(phrase, articles_amount, proxy={}, queue=None, baseurl="http://www.rusarticles.com"):
    parse(baseurl, phrase, articles_amount, proxy, queue)

def parse_articlesbase(phrase, articles_amount, proxy={}, queue=None, baseurl="http://www.articlesbase.com"):
    parse(baseurl, phrase, articles_amount, proxy, queue)

def main():
    parse_rusarticles(u"Цифровой фотоаппарат", 12, proxy={})
    #articles = parse_articlesbase(u"Digital camera", 14, proxy={"http":"211.138.124.233:80"})    

if __name__ == "__main__":
    from cProfile import Profile
    from pstats import Stats

    p = Profile()
    p.runcall(main)
    stats = Stats(p)
    stats.sort_stats('time', 'calls')
    stats.print_stats() 
