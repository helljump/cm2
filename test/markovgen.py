#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from collections import defaultdict
from random import choice
 
class TextGenerator(object):
 
    def __init__(self):
        self._data = defaultdict(list)
 
    def train(self, file):
        words = [None, None]
        for line in open(file):
            for word in line.split():
                words[0], words[1] = words[1], word
                if words[0]:
                    self._data[words[0]].append(words[1])
 
    def gentext(self, num_words):
        text = []
        text.append(choice(self._data.keys()).title())
        while len(text) < num_words:
            if self._data.has_key(text[-1]):
                text.append(choice(self._data[text[-1]]))
            else:
                text.append(choice(self._data.keys()))
        return ' '.join(text) + '.'
 
if __name__ == '__main__':
    textgen = TextGenerator()
    textgen.train('markovgen.txt')
    print textgen.gentext(100).decode("utf8", "ignore")
