#! /usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

import sys
from cx_Freeze import setup, Executable

import updater
from time import gmtime, strftime

egg = "%i.%i.%i.%s"
subver = int(strftime("%m%d", gmtime()))
egg %= tuple(updater.__version__ + [subver])

path = "c:/Python26/Lib/site-packages/requests-1.0.3-py2.6.egg/requests/packages"
sys.path.insert(0, path)

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includeFiles = [
    ('c:/Python26/Lib/site-packages/spynner-2.4-py2.6.egg/spynner/javascript', "spynner/javascript")
]

includes = ["dbhash", "pymorphy", "Levenshtein", "pyDes", "lxml._elementpath", "BeautifulSoup"]

includes += ["edit.thesaurusdialog", "urllib", "utils", "yazzy.yazzydialog", "zipfile",
    "engine.browser", "scripts.searchengine", "Queue", "UserString", "PyQt4.QtNetwork", "csv",
    "jinja2", "jinja2.debug", "jinja2.utils", "jinja2.ext", "yaml", "PyQt4.uic",
    "xml.etree.ElementTree", "requests", "unicodecsv", 'spynner', 'cssselect',
    'pymorphy2_dicts', 'pymorphy2', 'dawg', 'antigate',
    'PIL.Image', 'PIL.PngImagePlugin', 'PIL.JpegImagePlugin', 'PIL.GifImagePlugin',
     'tesseract',
     ]

excludes = ["cjkcodecs.aliases", "dbm", "iconv_codec", "_pybsddb", "bsddb3.dbutils", "simplejson._speedups"]

#excludes += [, "jinja2.utils.pretty", "jinja2.utils.markupsafe",
#    "jinja2._debugsupport", "jinja2.debugrenderer", "jinja2._markupsafe._speedups",
#    "__pypy__", "markupsafe", "pretty"]

excludes += ["Crypto.Cipher.AES", "M2Crypto", "cdb", "cryptlib_py",
    "gdata.Crypto.PublicKey._fastmath", "gmpy", "google.appengine.ext", "i18n",
    "jarray", "java", "javax.xml.parsers", "mx.Tidy", "pytc",
    "win32api", "win32prng",
    "mod_python.util", "mx.TextTools",
    "genshi._speedups"]

excludes += [
    "agent",  # imported from webstemmer.htmldom
    "elementtree",  # imported from atom
    "google.appengine.api",  # imported from gdata.alt.app_engine
    "test.test_support",  # imported from UserString
    "tidy",  # imported from feedparser
    "urllib.parse",  # imported from lxml.html
    "urllib.request",  # imported from lxml.html
]

buildOptions = dict(
    includes=includes,
    excludes=excludes,
    optimize=2,
    copy_dependent_files=True,
    create_shared_zip=True,
    silent=True,
    #include_files=includeFiles,
)

mainfile = Executable(
    "start.py",
    base=base,
    icon="../../dist/cm2.ico",
    targetName="cm2.exe"
    #version = egg
)

setup(
    name="cm2te",
    version=egg,
    options=dict(build_exe=buildOptions),
    description="Content Monster 2 TreeEdit",
    executables=[mainfile],
)
