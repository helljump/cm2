#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

import os
import sys
from PyQt4 import QtCore

homepath = unicode(QtCore.QDir.homePath()).encode(sys.getfilesystemencoding())
pluginpath = os.path.join(unicode(QtCore.QDir.homePath()), "treeedit").encode(sys.getfilesystemencoding())
if not os.path.isdir(pluginpath):
    os.mkdir(pluginpath)

CONFIGFILE = homepath + "/treeedit.cfg"
TMP_FILENAME = homepath + "/tmp.prt"
KEY_FILENAME = homepath + "/treeedit.key"
