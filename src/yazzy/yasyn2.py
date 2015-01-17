#!/usr/bin/env python
#-*- coding: UTF-8 -*-

#@author: snoa

from logging import debug, exception
import re
import cPickle
import os
import esm

#import sys
#sys.path.append("d:\\work\\cm2\\src")

from utils.tidy import autodecode
import bz2
import random

#WORDDELIM = re.compile( "(</{0,1}[^>]*?>|{{[^>]+}})", re.M | re.U | re.I )
WORDDELIM = re.compile( "(</{0,1}[^>]*?>|{{[^>]+}})", re.M | re.I )

YS_HEADER = "Yet Another Synonimizer DB V1\x1b"

def getYASName(fname):
    """ чтение названия файла для листбокса """
    if fname.lower().endswith(".yas"):
        finp = open( fname, "rb" )
        header = finp.read( len( YS_HEADER ) )
        if header != YS_HEADER: raise IOError
        base_name = cPickle.load( finp )
        finp.close()
        return base_name
    else:
        return os.path.split(fname)[-1]
            
def _loadCSV( fname ):
    """
    возвращает имя файла и список кортежей (фраза, синоним, вес)
    игнорирует строки комментариев #
    """
    outarr = []
    try:
        csvsrc = open( fname ).read()
        egg = autodecode(csvsrc, 2048)
        arr = egg.splitlines()
        CSV_TEMPLATE = re.compile( "\"(.+)\";\"(.+)\";*(\d*)", re.I | re.U )
        for item in arr:
            item = unicode( item.strip() )
            if item[0] == "#": continue
            m = CSV_TEMPLATE.split( item )
            if len( m ) < 3: continue
            m[1] = m[1].lower().strip()
            m[2] = m[2].strip()
            weight = int( m[3] ) if len( m ) > 3 and m[3].isdigit() else 1
            outarr.append( ( m[1], m[2], weight ) )
    except IOError:
        exception( "CSV load error: %s", fname)
    return fname, outarr

def _loadYAS( fname ):
    """
    загрузка YAS
    возвращаем имя базы и список кортежей (фраза, синоним, вес) 
    """
    base_name = ""
    outarr = []
    try:
        finp = open( fname, "rb" )
        header = finp.read( len( YS_HEADER ) )
        if header != YS_HEADER:
            raise IOError( "wrong YAS header" )
        base_name = cPickle.load( finp )
        s = bz2.decompress( finp.read() )
        base = cPickle.loads( s )
        for item in base:
            egg0 = item[0] if type(item[0])==type(u"") else item[0].decode('utf-8')
            egg1 = item[1] if type(item[1])==type(u"") else item[1].decode('utf-8')
            outarr.append((egg0, egg1, item[2]))
        finp.close()
    except IOError:
        exception( "YAS load error: %s", fname)
    return base_name, outarr

def load( fname ):
    dic = []
    name = ""
    if fname.endswith( ".csv" ):
        name, dic = _loadCSV( fname )
    elif fname.endswith( ".yas" ):
        name, dic = _loadYAS( fname )
    return name, dic

def save( fname, dbname, db ):
    try:
        fout = open( fname, "wb" )
        fout.write( YS_HEADER )
        cPickle.dump( "%s(%i)" % ( dbname, len( db ) ), fout )
        s = cPickle.dumps( db, cPickle.HIGHEST_PROTOCOL )
        fout.write( bz2.compress( s ) )
        fout.close()
    except IOError:
        raise

def save_py( fname, dbname ):
    outarr = []
    for item in dbname:
        outarr.append( "%s|%s|%i" % ( item[0], item[1], item[2] ) )
    p = "\n".join( outarr )
    spam = p.encode( "cp1251", "xmlcharrefreplace" ).encode( "bz2" ).encode( "base64" )
    fout = open( fname, "wt" )
    fout.write( "internal_db=\"\"\"\n%s\"\"\".decode(\"base64\")"\
                ".decode(\"bz2\").decode(\"cp1251\").encode(\"utf8\")"\
                ".splitlines()\n" % spam )
    fout.close()

def load_py( arr ):
    egg = []
    for item in arr:
        item = unicode(item,"utf-8")
        spam = item.split( "|" )
        spam[0] = spam[0]
        spam[1] = spam[1]
        spam[2] = int(spam[2])
        egg.append(tuple(spam))
    return egg

class ACDict( object ):
    def __init__( self, stoplist = [], progressbar = None ):
        self.synonyms = {}
        self.actree = self.tags = esm.Index()
        self.pb = progressbar
        self.stoplist = stoplist
        self.founded_sorted_qty = 0
        self.not_fixed = True

    def addDictionary( self, dic ):
        """ добавляем словарь в ЕСМ исключая стопслова """
        if self.pb: self.pb.set_text(u"Добавляем словарь")
        for item in dic:
            for stopword in self.stoplist:
                if stopword.search( item[0] ):
                    break
            else:
                self.addPhrase( item[0], item[1], item[2] )

    def _make( self ):
        """ подготовка ЕСМ для обработки """
        if not self.not_fixed:
            return
        self.not_fixed = False
        self.actree.fix()

    def addPhrase( self, phrase, synonym, weight ):
        '''
        Добавления фразы в дерево и хешсловарь
        @param phrase: фраза в уникоде
        @param synonym: синоним
        @param weight: вес синонима  
        '''
        assert type( phrase ) == type( unicode( "" ) )
        assert type( synonym ) == type( unicode( "" ) )
        phrase = phrase.lower()
        if phrase in self.stoplist:
            return
        #phrase_1251 = phrase.encode( "cp1251", "replace" )
        phrase_1251 = str(phrase.encode("utf-8", "replace"))
        phash = hash( phrase_1251 )
        changes = [ synonym ] * weight
        if self.synonyms.has_key( phash ):
            self.synonyms[phash].extend( changes )
        else:
            self.synonyms[phash] = changes
            self.actree.enter( phrase_1251 )
                        
    def search( self, text, mindist = 1, gen_template = False ):
        
        self._make()
        matches = 0
        founded = []
        self.founded_sorted_qty = 0
        
        orig_text = text
        text = str(text.encode("utf-8","replace"))
        
        #if self.pb: self.pb.set_text(u"Поиск по словарю")

        fragments = WORDDELIM.split( text )

        current_position = 0
                
        for fragment in fragments:
            if ( len( fragment.strip() ) == 0
                 or fragment[0] == "<" #tags
                 or fragment[:2] == "{{" ): #templates
                current_position += len( fragment )
                continue

            fraglen = len( fragment )
            #text_1251 = fragment.lower().encode( "cp1251", "replace" )
            text_1251 = fragment.lower()

            spam = self.actree.query( text_1251 )

            for match in spam:
                start = match[0][0]
                end = match[0][1]
                
                if ( ( start > 0 and fragment[start - 1].isalnum() ) or
                    ( end < fraglen and fragment[end].isalnum() ) ):
                    continue #not space

                matches += 1
                founded_phrase = fragment[start:end]

                #print founded_phrase

                founded_hash = hash( text_1251[start:end] )
                synonyms = []
                synonyms.append( founded_phrase )
                synonyms.extend( self.synonyms[founded_hash] )
                founded.append( ( start + current_position, end + current_position, synonyms ) )
            current_position += len( fragment )

        debug( "matches %i" % matches )

        if len( founded ) == 0:
            return orig_text

        #if self.pb: self.pb.set_text(u"Сортировка найденого")

        founded.sort( cmp = lambda x, y: cmp( x[0], y[0] ), reverse = True )
        
        egg = []
        text_len = len(text)
        for row in founded:
            if text_len>row[1]+1 and ord(text[row[1]+1])>64:
                continue
            if row[0]>0 and ord(text[row[0]-1])>64:
                continue
            egg.append(row)

        founded = egg

        debug( "matches after spaceless %i" % len( founded ) )

        #print founded

        founded_sorted = []

        if(founded):
            last_founded_sorted = founded[0]
            founded_sorted.append( founded[0] )
                
        for i in range( 1, len( founded ) ):
            if last_founded_sorted[0]>=founded[i][0] and last_founded_sorted[1]<=founded[i][0]:
                continue
            if last_founded_sorted[0]>=founded[i][1] and last_founded_sorted[1]<=founded[i][1]:
                continue
            if last_founded_sorted[0] - founded[i][1] > mindist:
                last_founded_sorted = founded[i]
                founded_sorted.append( founded[i] )

        debug( "matches after mindist sort %i" % len( founded_sorted ) )

        self.founded_sorted_qty = len( founded_sorted )
        
        #if self.pb: self.pb.set_text(u"Обработка текста")
        
        inserted = 0
        new_text_arr = []
        last_tail = len( text )
        for item in founded_sorted:
            tail = text[item[1]:last_tail]
            last_tail = item[0]
            new_text_arr.insert( 0, tail )
            orig_phrase = item[2][0]
            other_phrases = item[2][1:]
            spam = re.sub("[\s\.,]","",orig_phrase) #remove spaces
            
            assert len(spam)>0
            #assert type(spam)==unicode
            spam = spam.decode("utf-8")
            orig_phrase = orig_phrase.decode("utf-8")
            other_phrases = map( lambda item: unicode(item,"utf-8") if type(item)==str else item, other_phrases )
            
            if spam.isupper():
                other_phrases = map( lambda p: p.upper(), other_phrases )
            elif spam.istitle() or spam[0].isupper():
                other_phrases = map( lambda p: p.capitalize(), other_phrases )
            elif spam.islower():
                other_phrases = map( lambda p: p.lower(), other_phrases )
                
            if gen_template:
                all_variants = orig_phrase + u"|" + u"|".join(other_phrases)
                new_text_arr.insert(0, u"[%s]" % all_variants)
            else:
                new_text_arr.insert(0, u"%s" % random.choice(other_phrases))
            
            inserted += 1
        else:
            new_text_arr.insert(0, text[:last_tail])

        for i in range(len(new_text_arr)):
            if type(new_text_arr[i])==str:
                new_text_arr[i] = unicode(new_text_arr[i],"utf-8")
                
        return "".join(new_text_arr)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    '''
    fname, dic = load(u"dict/parttest.csv")
    acd = ACDict()
    for item in dic:
        acd.addPhrase(item[0], item[1], item[2])
    text = autodecode(open(u"in.txt").read(), 2000)
    text = acd.search(text, mindist=1, gen_template=False)
    rc = open(u"out.txt", "wt").write(text.encode("utf-8"))
    print text.encode("utf-8")
    '''
    
    fname, dic = load(ur"d:\work\cm2\src\edit\dict\stroitelstvo-v7.yas")
    import json, codecs
    json.dump(dic, codecs.open("stroyka.json", "wt", "utf-8"), encoding=unicode, ensure_ascii=False, indent=4)
    