#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys, os, re, logging, urllib
import mechanize

b = mechanize.Browser()
b.open("http://www.ucoz.ru/main/?a=reg")
open("dump.html","wb").write( b.response().read() )
