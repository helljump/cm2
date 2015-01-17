#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import shelve
#import atexit
#atexit.register()

registry = None

def open():
    registry = shelve.open("registry.db") #@UnusedVariable

def close():
    registry.close()
    
def set( key, val):
    registry[key] = val

def get( key, default=None ):
    return registry.get( key, default )

def clear( key ):
    del registry[key]
