#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from engine.browser import BrowserError

class AddUrlError(BrowserError): pass
class AlreadyInIndex(BrowserError): pass

class Code(object): (DONE, ALREADYININDEX, WRONGCAPTCHA, NOTADDED, BANNED) = range(5)  

class AddUrlResult(object):
    def __init__(self, code):
        self.code = code
        self.cap_id = -1