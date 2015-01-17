#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from distutils.core import setup
import py2exe
import sys


if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")


setup(
    version = "1.0.0",
    description = "getting fingerprint data",
    name = "getfingerprint",
    options = {"py2exe": {"compressed": 1,
                          "includes": ["sip"],
                          "optimize": 2,
                          "dist_dir": "release",
                          "ascii": 1,
                          "bundle_files": 1,
                          "packages": ["encodings"]
    }},
    zipfile = None,
    console = ['getfingerprint.py'],
    )
