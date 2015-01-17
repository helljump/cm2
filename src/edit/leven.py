#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from logging import debug
import re
import hashlib

from utils.tidy import html_tags_re, overspaces

from Levenshtein import ratio

def _recurse(item):
    sublist = []
    for subitem in item.children:
        if len(subitem.text) > 0:
            sublist.append(subitem)
        spam = _recurse(subitem)
        sublist.extend(spam)
    return sublist

def flatter(root):
    flatlist = _recurse(root)
    debug("flatter size: %i", len(flatlist))
    return flatlist
    
only_words = re.compile("[\W\d]+")

def clean(text):
    text = html_tags_re.sub("", text)
    text = text.lower()
    text = only_words.sub("", text)
    return text

def calc_ratio(flatlist):
    curr = 0
    for item1 in flatlist:
        for item2 in flatlist:
            if item1 is item2:
                continue
            if hasattr(item1, "padla") or hasattr(item2, "padla"):
                continue
            spam1 = clean(item1.text)
            spam2 = clean(item2.text)
            egg = ratio(spam1, spam2)
            if egg > 0.90:
                print "\n%0.3f: %s" % (egg, item1.title.encode("cp866", "replace"))
                print "       %s" % item2.title.encode("cp866", "replace")
                item2.padla = True
        curr += 1
        print curr,

class Unic(object):
    notwords = re.compile("\W{1,}", re.I | re.U | re.S | re.M)
    def __init__(self, article, words=6):
        self.article = article
        self.calcmd5(words)
    def calcmd5(self, words):
        self.md5set = set()
        text = html_tags_re.sub(" ", self.article)
        text = self.notwords.sub(" ", text)
        egg = overspaces.split(text)
        while egg:
            spam = " ".join(egg[:words])
            egg = egg[1:]
            if not spam.strip():
                continue
            m = hashlib.md5(spam.encode("utf-8", "replace"))
            self.md5set.add(m.digest())
    def __and__(self, other):
        return self.md5set & other.md5set
    def __len__(self):
        return len(self.md5set)
    def clear(self):
        self.md5set.clear()

def get_matched(tree, match_percent):
    pass

def main():
    import cPickle
    tree = cPickle.load(open("autoload.prt", "rb"))
    flatlist = flatter(tree)
    
    #matched_articles = get_matches(flatlist, 0.8)
    uniclist = [Unic(article, 5) for article in flatlist]
    for item1 in uniclist:
        for item2 in uniclist:
            if item1 is item2:
                continue
            if not item1.md5set or not item2.md5set:
                continue
            egg = item1 & item2
            matches = len(egg)
            if not matches:
                continue
            maxlen = max([len(item1), len(item2)])
            percent = 1.0 / maxlen * matches
            if percent > 0.8:
                print "percent matches %0.3f" % percent
                print item1.article.title.encode("cp866", "replace")
                print item2.article.title.encode("cp866", "replace")
                item2.clear()

if __name__ == "__main__":
    a = u"sdc pobi bnsdcub iqw cdvqw scdouqyewg fp;wgeyfbdgiu2ywevdiuwq dhjv  ku vwdicu w vdi wi ciw udcvi"
    b = u"sdc pobi bnsdcub iqw cdvqw scdouqyewg fp;wgeyfbdgiuywevdiuwq dhjv  ku vwdicu w vdi ciw udcvi"
    
    c = Unic(a) & Unic(b)
    print c
    print len(c)
    