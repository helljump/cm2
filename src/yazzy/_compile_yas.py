#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from yasyn2 import load, save

fname, dic = load( u"fullthematik.csv" )
save( "fullthematik.yas", u"Мегабаза", dic )
