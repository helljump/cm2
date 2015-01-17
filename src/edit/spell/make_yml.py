#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"
import logging 
import yaml
import os
import codecs

log = logging.getLogger(__name__)

config = {}
lang = 1

for fname in os.listdir("."):
    egg = os.path.splitext(fname)
    if egg[1]==".aff":
        config[u"lang-%i" % lang] = [ fname, "%s.dic" % egg[0] ]
        lang +=1
        
yaml.dump( config, codecs.open("spell.yml","wt","utf-8"), encoding='utf-8', default_flow_style=False )
