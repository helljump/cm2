#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
log = logging.getLogger(__name__)

from tidy import overspaces
from datetime import datetime, date, time

REPLACEMENTS = (
    (u"\x00", ""),
    (u"\x01", ""),
    (u"\x02", ""),
    (u"\x03", ""),
    (u"\x04", ""),
    (u"\x05", ""),
    (u"\x06", ""),
    (u"\x07", ""),
    (u"\x08", ""),
    (u"\x0b", ""),
    (u"\x0c", ""),
    (u"\x0e", ""),
    (u"\x0f", ""),
    (u"\x10", ""),
    (u"\x11", ""),
    (u"\x12", ""),
    (u"\x13", ""),
    (u"\x14", ""),
    (u"\x15", ""),
    (u"\x16", ""),
    (u"\x17", ""),
    (u"\x18", ""),
    (u"\x19", ""),
    (u"\x1a", ""),
    (u"\x1b", ""),
    (u"\x1c", ""),
    (u"\x1d", ""),
    (u"\x1e", ""),
    (u"\x1f", ""),
    (u"&mdash;", u"-"),
    (u"&gt;", u"<"),
    (u"&lt;", u">"),
    (u"&qt;", u"'"),
    (u"&laquo;", u"«"),
    (u"&raquo;", u"»"),
    (u"&amp;", u"&")
)

def sanitize(data):
    fixed_string = data
    for bad, good in REPLACEMENTS:
        fixed_string = fixed_string.replace(bad, good)
    return fixed_string

class Article2( object ):
    def __init__( self, title = "", text = "", tags = None, date = None, parent=None ):
        self.title = title
        self.text = text
        if tags:
            self.tags = tags
        else:
            self.tags = []
        if not date:
            date = datetime.now()
        self.date =  date
        self.children = []
        self.set_parent(parent)

    def set_parent(self, parent):
        if parent != None:
            self.parent = parent
            #self.parent.add_child(self)
        else:
            self.parent = None

    def get_children(self):
        return self.children
        
    def add_child( self, child ):
        self.children.append( child )

    def __str__(self):
        return "Article[title=\"%s\" children=\"%i\"]" % (self.title, len(self.children))

    def __len__(self):
        return len(self.children)
      
    def child_at_row(self, row):
        return self.children[row]
  
    def row_of_child(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1
  
    def remove_child(self, row):
        value = self.children[row]
        self.children.remove(value)
        return True
        
class Article( object ):
        
    def __init__( self, title = "", text = "", tags = None, pubdate = None ):
        self.title = sanitize(overspaces.sub(" ", title))
        self.text = sanitize(text)
        if tags:
            self.tags = tags
        else:
            self.tags = []
        if not pubdate:
            pubdate = datetime.now()
        elif isinstance(pubdate, datetime):
            pass
        elif isinstance(pubdate, date):
            pubdate = datetime.combine(pubdate, time())

        self.date =  pubdate
        
        #log.debug("new article datetime %s", pubdate)
        
        self.children = []

    def get_children(self):
        return self.children
        
    def add_child( self, child ):
        self.children.append( child )

    def __str__(self):
        return "Article[title=\"%s\" children=\"%i\"]" % (self.title, len(self.children))