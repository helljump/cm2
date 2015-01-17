#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from lxml import etree
import re

class Sanation(object):
    SELFCLOSED_TAGS = ['img', 'br']
    HEADER_TAG = re.compile("h\d")

    def __init__(self, TAGS, ATTRS, newline):
        self.egg = []
        self.ALLOWED_TAGS = TAGS
        self.ALLOWED_ATTRS = ATTRS
        self.newline = newline

    def _sanitize_attrib(self, attrib):
        egg = []
        for k,v in attrib.items():
            if k in self.ALLOWED_ATTRS:
                egg.append( "%s=\"%s\"" % (k,v) )
        if egg:
            return " " + " ".join(egg)
        else:
            return ""
    
    def _open_tag(self, tag, attrib):
        attr = self._sanitize_attrib(attrib)
        if tag in self.SELFCLOSED_TAGS:
            self.egg.append( "<%s%s/>" % (tag, attr) )
            if self.newline and tag=='br':
                self.egg.append("\n")
        else:
            self.egg.append( "<%s%s>" % (tag, attr) )
        
    def _close_tag(self, tag):
        if tag not in self.SELFCLOSED_TAGS:
            self.egg.append( "</%s>" % tag )
        
    def start(self, tag, attrib):
        if tag in self.ALLOWED_TAGS:                
            self._open_tag(tag, attrib)
        elif 'h' in self.ALLOWED_TAGS and self.HEADER_TAG.match(tag):
            self._open_tag(tag, attrib)
            
    def end(self, tag):
        if tag in self.ALLOWED_TAGS:
            self._close_tag( tag )
        elif 'h' in self.ALLOWED_TAGS and self.HEADER_TAG.match(tag):
            self._close_tag( tag )
            
    def data(self, data):
        self.egg.append( "%s" % data )
        
    def comment(self, text):
        pass
        
    def close(self):
        return ''.join(self.egg)

def clear_html(source, tags, attrs, newline):
    parser = etree.HTMLParser(target = Sanation(tags, attrs, newline))
    result = etree.XML(source, parser)
    return result

if __name__ == "__main__":
    test_code = open(r"d:\work\wptr\html\wnetwork2.html","rt").read()
    ALLOWED_TAGS = ['b', 'i', 'img', 'h']
    ALLOWED_ATTRS = ['src', 'align']
    result = clear_html(test_code, ALLOWED_TAGS, ALLOWED_ATTRS)
    rc = result.encode('utf-8','ignore')
    open("test.html","wt").write(rc)
