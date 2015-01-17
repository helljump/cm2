#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import random
from pytils.translit import slugify
from nicepass import nicepass
import logging

name_list = [unicode(item.strip()) for item in open("names.txt").readlines()]

class Profile(object):
    def __init__(self, delim="."):
        self.name = random.choice(name_list)
        self.sname = slugify(self.name)
        self.surname = random.choice(name_list)+"ов"
        self.ssurname = slugify(self.surname)
        self.username = slugify( self.name ) + delim + slugify( self.surname )
        self.year = random.randint(1970, 1990)
        self.month = random.randint(1, 11)
        self.day = random.randint(1, 28)
        self._pass = nicepass(7,2)

    def __repr__(self):
        return "Profile [" + self.name + "|" + self.surname + "|" + self.username +  "|" + self._pass + "]"

    def __str__(self):
        return "Profile [" + self.name + "|" + self.surname + "|" + self.username +  "|" + self._pass + "]"
        
    def write(self, fp):
        logging.debug("write profile %s" % self)
        fp.write("%s\n" % self)

if __name__ == "__main__":
    prof = Profile()
    print "%s" % prof
    prof.write( open("profile.txt","a+t") )
