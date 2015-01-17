#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging
#from pymorphy import get_morph
#from pymorphy_speedups import setup_psyco
import pymorphy2
import time
import cPickle
import os

log = logging.getLogger(__name__)

#setup_psyco()


class ThesException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        tt = time.time() - t
        rc = u"Время выполнения функции %s: %f" % (f.__name__, tt)
        log.debug("%s", rc)
        return res
    return tmp


class Thesaurus(object):

    morph_dir = "morph"
    morph2_dir = "morph2"

    def __init__(self, lang='ru'):
        egg = os.path.join(Thesaurus.morph_dir, lang)
        log.debug("load thesaurus")
        self.th = cPickle.load(open(os.path.join(egg, "th.pkl"), "rb"))
        log.debug("load morph shelves")
        #self.morph = get_morph(egg, backend="shelve")
        self.morph = pymorphy2.MorphAnalyzer(Thesaurus.morph2_dir)

    def inflect_list(self, words, info, limit=100):
        rc = []
        for w in list(words)[:limit]:
            egg = w.split(" ")
            if len(egg) > 1:
                #log.debug("multi word inflect: %s", w)
                spam = []
                for ww in egg:
                    norm = self.morph.parse(ww)
                    if norm:
                        morph = norm[0].inflect(info.grammemes)
                        if morph and morph.word:
                            spam.append(morph.word)
                rc.append(" ".join(spam))
            else:
                norm = self.morph.parse(w)
                if norm:
                    morph = norm[0].inflect(info.grammemes)
                    if morph and morph.word:
                        #log.debug('word [%s]', morph.word)
                        rc.append(morph.word)
        return rc

    def change_case(self, word, example):
        if example.istitle():
            return word.capitalize()
        elif example.isupper():
            return word.upper()
        elif example.islower():
            return word.lower()
        else:
            return word

    def get_syno(self, word):
        assert type(word) == type(u"")
        #egg = self.morph.get_graminfo(word.upper())
        egg = self.morph.parse(word.upper())
        if not egg:
            return {}
            # raise ThesException(u"Не удалось получить грамматическую информацию")
        #src_info = egg[0]['info']
        src_info = egg[0].tag
        log.debug(u"graminfo: %s", src_info)
        wrd = egg[0].normal_form.upper()
        assert type(word) is unicode
        egg = {}
        #for wrd in src_words:
        #log.debug(u"norm word: %s", wrd)
        rc = self.th.get(hash(wrd), {})
        for k, v in rc.items():
            # log.debug(u"inflect: %s %s", k, v)
            tmp = set()
            for row in self.inflect_list(v, src_info):
                if not row:
                    continue
                tmp.add(self.change_case(row, word))
            egg[k] = sorted(list(tmp))
        for t, w in egg.items():
            if len(w) > 0:
                return egg
        return {}


def main():
    thes = Thesaurus("ru")
    for word in u"Доброго".split(" "):
        rc = thes.get_syno(word)
        for k, v in rc.items():
            if not v:
                continue
            print "-", k
            print "--", ", ".join(v)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        main()
    except ThesException, er:
        print er.value
