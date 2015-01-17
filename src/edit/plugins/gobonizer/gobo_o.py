#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import bz2
import logging
import pickle
import re
import zipfile
import random

log = logging.getLogger(__name__)


class DictItem( object ):
    #html_tags = re.compile( "</{0,1}[^>]*?>", re.U | re.M | re.S )
    html_tags = re.compile( "<[^>]*?>", re.U | re.M | re.S )
    overspaces = re.compile( "[ \t]{1,}", re.U | re.M | re.S )
    delim = "[\W\s]{1}"

    def __init__( self, phrase, description ):
        self.phrase = self._cleaning( phrase )
        self.description = [self._cleaning( description ), ]
        self.description_len = len( self.description )
        self.len = len( self.phrase )
        ph = "%s(%s)%s" % ( self.delim, self.phrase, self.delim )
        #print ":", ph.encode("cp866","ignore")
        self.phrase_re = re.compile( ph, re.I | re.S | re.U )

    def add_description( self, desc ):
        self.description.append( desc )
        self.description_len = len( self.description )

    def get_description( self ):
        return self.description[random.randint( 0, self.description_len - 1 )]

    def _cleaning( self, phrase ):
        phrase = unicode( phrase, "utf-8", "replace" )
        phrase = self.html_tags.sub( "", phrase )
        phrase = self.overspaces.sub( " ", phrase ).strip()
        return phrase

def read(finp):
    if finp.endswith(".gob"):
        rc = read_gob(finp)
    elif finp.endswith(".ods"):
        rc = read_ods(finp)
    return rc


def read_gob(finp):
    packed_dump = open(finp, "rb").read()
    unpacked = bz2.decompress(packed_dump)
    unpacked = unpacked.replace("plugins.gobo", "gobo_o")
    unpacked = unpacked.replace("__main__", "gobo_o")
    libr = pickle.loads(unpacked)
    return libr


def read_ods( finp ):
    myfile = zipfile.ZipFile( finp )
    listoffiles = myfile.infolist()
    dict_template = re.compile( "<table:table-row table:style-name=\"ro1\">.*?"\
    "<text:p>(.*?)</text:p>.*?<text:p>(.*?)</text:p>.*?</table:table-row>", re.DOTALL )
    dict = None
    for s in listoffiles:
        if s.orig_filename == "content.xml":
            content = myfile.read( s.orig_filename )
            rows = dict_template.findall( content )
            dict = [DictItem( phrase, desc ) for phrase, desc in rows]
            return dict
    return None

def remove_douples( dict ):
    filtered = []
    dict.sort( cmp = lambda x, y: cmp( x.len, y.len ), reverse = True )
    for i in range( len( dict ) - 1 ):
        if dict[i] == None:
            continue
        if dict[i].phrase.lower() != dict[i + 1].phrase.lower(): #snoa 20jul
            filtered.append( dict[i] )
    else:
        filtered.append( dict[i + 1] )
    return filtered

def pack_douples( dict ):
    dict.sort( cmp = lambda x, y: cmp( x.len, y.len ), reverse = True )
    packed = None
    for item in dict:
        if packed == None:
            packed = []
            packed.append( item )
            continue
        if packed[-1].phrase == item.phrase: # dup
            packed[-1].add_description( item.description )
        else:
            packed.append( item ) # nondup
    return dict

class FoundItem( object ):
    div_template = "<a class=\"[goboclass]\" href=\"#\">%s<span>%s</span></a>"
    def __init__( self, dict_item, span, text, groups ):
        self.dict_item = dict_item
        self.startpos = span[0] + 1
        #self.startpos = span[0] #snoa 20jul
        self.endpos = span[1] - 1
        self.phrase = text[self.startpos:self.endpos]
        self.enabled = True
        self.groups = groups
    def __str__( self ):
        egg = self.dict_item.get_description()
        if type(egg)==list:
            logging.debug("Select random row for " + self.phrase)
            egg = random.choice(egg)
        try:
            desc = egg % self.groups[1:]
        except TypeError:
            logging.error("Procent(%%) must be escaped in " + self.phrase)
            esc_desc = egg.replace("%","%%")
            desc = esc_desc % self.groups[1:]

        return self.div_template % ( self.phrase, desc )

def distant_filter( fitems, distance ):
    fitems.sort( cmp = lambda x, y: cmp( x.startpos, y.startpos ) )
    last_live_item_offset = -1
    for item in fitems:
        if last_live_item_offset < 0:
            last_live_item_offset = item.startpos
        elif distance > item.startpos - last_live_item_offset:
            item.enabled = False
        else:
            last_live_item_offset = item.startpos
    fitems = filter( lambda x: x.enabled, fitems )
    return fitems

def xref_remove( fitems ):
    len_fitems = len( fitems )
    for i in range( len_fitems ):
        for j in range( len_fitems ):
            r1 = set( range( fitems[i].startpos, fitems[i].endpos ) )
            r2 = set( range( fitems[j].startpos, fitems[j].endpos ) )
            if r1 & r2 and fitems[i].enabled and fitems[j].enabled:
                if fitems[i].dict_item.len > fitems[j].dict_item.len:
                    fitems[j].enabled = False
    fitems = filter( lambda x: x.enabled, fitems )
    return fitems

def remove_founded_dupes( fitems ):
    fitems.sort( cmp = lambda x, y: cmp( x.dict_item, y.dict_item ) ) # сортировать по ссылке на токен
    for i in range( len( fitems ) - 1 ):
        if fitems[i].dict_item is fitems[i + 1].dict_item:
            fitems[i + 1].enabled = False
    fitems = filter( lambda x: x.enabled, fitems )
    return fitems

def find_tokens(dict, text):
    fitems = []
    if dict==None:
        return fitems
    splitted = re.split('(?imsu)(<[^>]*?>)', text)

    splittedlen = 0
    for item in splitted:
        #print 'item ', item
        if item.startswith('<'):
            splittedlen += len(item)
            continue
        for dict_item in dict:
            for mobj in dict_item.phrase_re.finditer(item):
                span = (mobj.span()[0]+splittedlen, mobj.span()[1]+splittedlen)
                print
                fitems.append( FoundItem( dict_item, span, text, mobj.groups() ) )
        splittedlen += len(item)
    return fitems

def goboize_text( fitems, text ):
    fitems.sort( cmp = lambda x, y: cmp( x.startpos, y.startpos ), reverse = True )
    for item in fitems:
        if item.enabled:
            head = text[:item.startpos]
            tail = text[item.endpos:]
            text = "%s%s%s" % ( head, item, tail )
    return text
