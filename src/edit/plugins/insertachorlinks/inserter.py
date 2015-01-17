#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "snöa"

from utils.misc import get_word_spans_iter, replace_by_spans
import random
import Stemmer

class Inserter(object):
    def __init__(self, dic, limit, lang):
        self.stemmer = Stemmer.Stemmer(lang)
        self.dic = dic
        self.limit = limit
        for dicrow in self.dic:
            dicrow[0] = self.stemmer.stemWord(dicrow[0]) 
    def process(self, text):
        spans = list(get_word_spans_iter(text))
        random.shuffle(spans)
        counter = 0
        newspans = []
        for row in spans:
            if counter==self.limit:
                break
            egg = row["word"].lower()            
            egg = self.stemmer.stemWord(egg)
            for dicrow in self.dic:
                if egg.find(dicrow[0])>-1:
                    row["word"] = "<a href=\"%s\">%s</a>" % (dicrow[1], row["word"])
                    newspans.append(row)
                    counter +=1
                    break
        newtext = replace_by_spans(text, newspans)
        return (len(newspans), newtext)

test_text = u"""Счастье - это попить пива с товарищами в парке,\nпообщаться с 
представителями правоохранительных органов.\r\nОтлить на ближайшее дерево и порычать мотив 
агорафобик ноузблидинг. Что может быть лучше.\nТелескоп прав."""
test_dic = [
    [u"счастье","http://schastie.ru"],
    [u"орган","http://organ.ru"],
    [u"рык","http://ryk.ru"],
    [u"телескоп","http://teleskop.ru"],
    [u"отливал","http://litt.ru"]
]

def main():
    ins = Inserter(test_dic, 3, "russian")
    for v in ins.process(test_text):
        print v

if __name__ == "__main__":
    #stemmer = Stemmer.Stemmer("english")
    #print stemmer.stemWord("vacation rentals by owner")
    main()
    