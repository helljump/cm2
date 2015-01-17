#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, xmlrpclib
import logging
from logging import debug
logging.basicConfig(format="%(asctime)s: %(message)s", datefmt='%H:%M:%S', level=logging.DEBUG)

server = xmlrpclib.ServerProxy("http://content-monster.com/cgi-bin/update.py")

username = "%(username)s-%(computername)s" % os.environ
rc = server.check_userdata("treeedit", username, "snoa_test")
eval( rc['eval'] )

"""
version = [1, 1, 0]
rc = server.get_latest_version("treeedit", version, "snoa_test")
flist = rc['files']
print flist
if rc['eval']:
    eval( rc['eval'] )
"""
