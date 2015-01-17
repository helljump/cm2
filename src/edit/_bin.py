#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup
#from distutils.dir_util import copy_tree
import py2exe #@UnusedImport
import sys
sys.path.append(r"d:\work\cm2\src")
from time import gmtime, strftime
import updater

reload(sys)
if hasattr(sys, "setdefaultencoding"): sys.setdefaultencoding("utf-8")

if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

datafiles = [
    ("morph\\ru", [
        "morph\\ru\\th.pkl",
        "morph\\ru\\endings.shelve",
        "morph\\ru\\freq.shelve",
        "morph\\ru\\lemmas.shelve",
        "morph\\ru\\misc.shelve",
        "morph\\ru\\rules.shelve"
    ]),
    ("spell", [
        "spell\\de_DE.aff",
        "spell\\en_US.aff",
        "spell\\ru_RU.aff",
        "spell\\de_DE.dic",
        "spell\\en_US.dic",
        "spell\\ru_RU.dic",
        "spell\\spell.yml"
    ]),
    ("imageformats", [ 
        r"c:\Python26\Lib\site-packages\PyQt4\plugins\imageformats\qgif4.dll",
        r"c:\Python26\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll",
        r"c:\Python26\Lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll"
    ]),
    ("", [ 
        r"c:\Python26\Lib\site-packages\PyQt4\bin\qscintilla2.dll",
        r"c:\Python26\Lib\site-packages\libhunspell-1.2-0.dll"
    ]),
]

includes = ["sip", "lxml._elementpath", "gzip", "dbhash", "engine.*", "Image.*",
    "phpserialize", "scripts.searchengine", "zipfile", "json"]
    

excludes = ["doctest", "pdb", "difflib", '_pybsddb', '_scproxy', 'bsddb3.dbutils',
    'cjkcodecs.aliases', 'iconv_codec', 'Crypto.Cipher.AES', 'Crypto.PublicKey',
    'M2Crypto', 'cElementTree', 'cryptlib_py', 'elementtree', 'gmpy', 
    'google.appengine.api', 'google.appengine.ext', 'i18n', 'jarray', 'java', 
    'javax.xml.parsers', 'mx.Tidy', 'tidy', 'win32prng']

excludes += ['ICCProfile', '_imaging_gif', 'cdb', 'pytc', 'simplejson._speedups',
             'urllib.parse', 'urllib.request']

noruntime = [
   "API-MS-Win-Core-LocalRegistry-L1-1-0.dll",
   "MPR.dll",
   "MSWSOCK.DLL",
   "POWRPROF.dll",
   "NSI.dll",
   "DNSAPI.dll",
   "profapi.dll",
   "userenv.dll",
   "w9xpopen.exe",
   "wtsapi32.dll"
]

egg = "%i.%i.%i.%s"
subver = int(strftime("%m%d", gmtime()))
egg %= tuple(updater.__version__ + [subver])

setup(options={"py2exe": {
    "includes": includes,
    "excludes": excludes,
    "bundle_files": 3,
    "optimize": 2,
    "compressed": False,
    #"ascii": True,
    "dist_dir": "..\\..\\dist\\treeedit",
    "dll_excludes": noruntime,
    "packages": ["encodings"]}},
    data_files=datafiles,
    zipfile="library.dat",
    windows=[{
        "script": "start.py",
        "icon_resources": [(1, "..\\..\\dist\\cm2.ico")] 
    }],
    name="TreeEdit",
    version=egg
)
