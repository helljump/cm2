#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup
import py2exe #@UnusedImport
import sys, time

reload(sys)
if hasattr(sys, "setdefaultencoding"): sys.setdefaultencoding("utf-8")

if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

datafiles = []
includes = ["sip", "xml.etree.ElementTree", "dbhash"]
excludes = ["doctest", "pdb", "unittest", "difflib" ]
    
setup(options={"py2exe": {
    "includes": includes,
    "excludes": excludes,
    "bundle_files": 3,
    "optimize": 0,
    "compressed": False,
    "ascii": True,
    "dist_dir": "release",
    "dll_excludes": ["w9xpopen.exe"],
    "packages": ["encodings"]}},
    data_files=datafiles,
    zipfile=None,
    windows=[{"script": "proxyform.py"}],
    name="proxyform",
    version="1.0.0.%s" % time.strftime("%m%d")
)
