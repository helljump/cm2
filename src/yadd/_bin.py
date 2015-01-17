#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup
import py2exe #@UnusedImport
import sys, time

sys.path.append(r"d:\work\cm2\src")

reload(sys)
if hasattr(sys, "setdefaultencoding"): sys.setdefaultencoding("utf-8")

if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

datafiles = [("imageformats", [ r"c:\Python26\Lib\site-packages\PyQt4\plugins\imageformats\qgif4.dll",
                                r"c:\Python26\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll",
                                r"c:\Python26\Lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll" ]),
             ("", [r"yadd.ico"])
            ]
includes = ["sip", "xml.etree.ElementTree", "dbhash"]
excludes = ["doctest", "pdb", "difflib",
            '_pybsddb', '_scproxy', 'bsddb3.dbutils', 'cjkcodecs.aliases', 'iconv_codec' ]
    
setup(options={"py2exe": {
    "includes": includes,
    "excludes": excludes,
    "bundle_files": 3,
    "optimize": 2,
    "compressed": True,
    "ascii": True,
    "dist_dir": "build\\release",
    "dll_excludes": ["w9xpopen.exe"],
    "packages": ["encodings"]}},
    data_files=datafiles,
    zipfile=None,
    windows=[{
        "script": "yadd.py",
        "icon_resources": [(1, "yadd.ico")]
    }],
    name="Yadd",
    version="1.2.0.%s" % time.strftime("%m%d")
)
