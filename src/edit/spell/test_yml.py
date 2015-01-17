#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import logging 
log = logging.getLogger(__name__)

import yaml
import codecs
        
config = yaml.load(codecs.open("spell.yml","r","utf-8"))

for item in config.items():
    print item[0], ":", item[1]
