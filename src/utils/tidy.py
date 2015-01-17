#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging 
log = logging.getLogger(__name__)

import re
from engine.constants import encodings
import chardet
import xml.sax.saxutils as saxutils

html_tags_re = re.compile("<[^>]*>", re.I | re.U | re.S | re.M)
overspaces = re.compile("\s{1,}", re.M | re.S)

META_ENCODING = re.compile("<meta[^>]*charset=([^;\"\']*)[^>]*?>", re.I)

def encode_html_entities(text):
    return saxutils.quoteattr(text)[1:-1]

def autodecode(source, maxlen=0):
    m = META_ENCODING.search(source)
    if m:
        egg = m.groups(0)[0].replace("-", "").lower()
        codepage = encodings[egg]
        log.debug("encoding detected from meta %s" % codepage)
    else:
        try:
            if not maxlen:
                maxlen = len(source)
            codepage = encodings[ chardet.detect(source[:maxlen])["encoding"].replace("-", "").lower() ]
        except Exception:
            log.exception("autodetect fail")
            codepage = "utf-8"
        log.debug("1.encoding detected by chardet(ugly page) %s" % codepage)
        if codepage not in ["utf-8", "ascii", "cp1251"]:
            codepage = "utf-8" 
        log.debug("2.encoding detected by chardet(ugly page) %s" % codepage)
    return unicode(source, codepage, "ignore")

def sql_quote(text):
    text = unicode(text)
    text = text.replace("&mdash;", "-")
    return text.replace(r"'", r"\'").replace("\"", r"\"").replace("\n", "\\n")

def do_truncate_html(s, length=255, killwords=False, end='...'):
    s = re.sub(html_tags_re, "", s)
    return do_truncate(s, length, killwords, end)
    
def do_truncate(s, length=255, killwords=False, end='...'):
    """ spizhzheno u jinja """
    if len(s) <= length:
        return s
    elif killwords:
        return s[:length] + end
    words = s.split(' ')
    result = []
    m = 0
    for word in words:
        m += len(word) + 1
        if m > length:
            break
        result.append(word)
    result.append(end)
    return u' '.join(result)
    
if __name__ == "__main__":
    
    a = """<a href=\"http://sireni.ru/sy2/wp-content/uploads/catalog/lil_you_devil.jpg\"><img class=\"alignleft size-thumbnail wp-image-30\" title=\"You Devil\" src=\"http://sireni.ru/sy2/wp-content/uploads/catalog/thumb/lil_you_devil.jpg\" alt=\"\" width=\"150\" height=\"150\" /></a>woc ibdwfv oiybwfdv olybiwefpbic bweofu cvybweosc diybwoeycdiwsioc dbwdsoc iybqwdc oiybwod uctvw qeucdbqwoeiysbx wefc<br/>\n"""
    #a = html_tags_re.sub("-",a)
    #print a
    print encode_html_entities(u"Новости \"PokerStars\" & Всякая 'фигня'")
    
