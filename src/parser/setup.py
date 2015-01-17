#! /usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import sys
from cx_Freeze import setup, Executable

from time import gmtime, strftime

egg = "2.2.0.%i" % int(strftime("%m%d", gmtime()))

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    #base = "Console"

includes = ["sip", "xml.etree.ElementTree", "dbhash", "utils"]

excludes = ["doctest", "pdb", "difflib", "dbm", "test.test_support",
            '_pybsddb', '_scproxy', 'bsddb3.dbutils', 'cjkcodecs.aliases', 'iconv_codec' ]

#? dbm imported from whichdb
#? test.test_support imported from UserString

buildOptions = dict(
    includes = includes,
    excludes = excludes,
    optimize = 2,
    copy_dependent_files = True,
    create_shared_zip = True,
)

mainfile = Executable(
    "uberparser.py", 
    base = base,
    icon = "uberparser.ico",
)

setup(
    name = "cm2up2",
    version = egg,
    options = dict(build_exe = buildOptions),
    description = "Content Monster 2 Uberparser 2",
    executables = [ mainfile ],
)
