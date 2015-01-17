#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import os
import re
import random
import time
import functools
import logging

log = logging.getLogger(__name__)

WORDDELIM = re.compile("(</{0,1}[^>]*?>|[\w]+|\r\n)", re.M | re.U | re.I)


def get_dir_content( srcpath, exts ):
    return [ fname for fname in os.listdir(srcpath) 
        if os.path.splitext(fname.lower())[-1] in exts 
            and os.path.isfile( os.path.join(srcpath,fname) ) ]

def iget_dir_content( srcpath, exts ):
    return ( fname for fname in os.listdir(srcpath) 
        if os.path.splitext(fname.lower())[-1] in exts 
            and os.path.isfile( os.path.join(srcpath,fname) ) )

def get_word_spans_iter(text, minsize=2):
    """
    получает список словарей {word, spans, line} из текста
    пропуская пунктуацию и html теги
    """
    assert(type(text)==type(u""))
    #text = text.replace("\r\n","  ")
    #text = text.replace("\r"," ")
    #text = text.replace("\n"," ")
    current_line = 0
    offset = 0
    for item in WORDDELIM.finditer(text):
        egg = item.group(1)
        if len(egg.strip())==0:
            current_line += 1
            #offset -= len()
            #print repr("%s" % egg)
        if egg and len(egg.strip())>minsize and egg[0]!="<":
            #yield({"word":egg.lower(), "spans":item.span()}) # нахуя lower() ???
            #span = map(lambda x: x+new_line_offset, )
            yield({"word":egg, 
                "spans":item.span(), 
                "line":current_line})
        #elif egg[0]!="<":
        #    new_line_offset += len(egg)
    
def get_random_spans(text, qty):
    '''
    text = codecs.open(r"d:\work\wptr\html\content_goo.htm","rt","cp1251","ignore").read()
    spans = get_random_spans(text, 15)
    '''
    egg = list(get_word_spans_iter(text))
    random.shuffle(egg)
    #print "----------", qty
    egg = egg[:qty]
    #egg.sort(cmp = lambda x,y: cmp(x["spans"][0], y["spans"][0]), reverse=True)
    return egg
    
def replace_by_spans(text, spans_list):
    """
    меняет слова в тексте по spans списку.
    т.е. сначала обрабатываем полученный список spans из get_word_spans_iter.
    удаляем ненужные словари. и меняем меняем word в нужных.
    а потом просто обрабатываем.
    
    text = codecs.open(r"d:\work\wptr\html\content_goo.htm","rt","cp1251","ignore").read()
    spans = get_random_spans(text, 15)
    for item in spans:
        print "[%s]%s" % (item["word"].encode('cp866','ignore'), item["spans"])
        item["word"] = "[[[%s]]]" % item["word"]
    text = replace_by_spans(text, spans)
    with codecs.open(r"text.htm","wt","cp1251","ignore") as fout:
        fout.write(text)
    """
    spans_list.sort(cmp = lambda x,y: cmp(x["spans"][0], y["spans"][0]), reverse=True)
    egg = []
    remain = len(text)
    for spans in spans_list:
        end = spans["spans"][1]
        egg.insert(0,text[end:remain])
        egg.insert(0,spans["word"])
        remain = spans["spans"][0]
    else:
        egg.insert(0,text[0:remain])
    return "".join(egg)


def timing(func):
    def wrapper(*args, **argd):
        start_time = time.time()
        func(*args, **argd)
        log.debug("function: %s used %.2f seconds", func.__name__, time.time()-start_time )
    functools.update_wrapper(wrapper, func)
    return wrapper  

if __name__ == "__main__":
    print [w for w in get_word_spans_iter(u"123,456 789.10!", 1)]
