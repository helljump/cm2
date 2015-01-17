#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import os
import pyDes
import pickle
import socket
import logging


logging.basicConfig(level=logging.DEBUG)


with open('fp.bin', 'wb') as fout:
    hh = 'savuyg9734gf;sd81g30f8g1[;4444444gahjldsfg9714pfgwhgd;lkfhv'
    des = pyDes.des(hh[5:13], padmode=pyDes.PAD_PKCS5)
    params = {}
    try:
        keyfile = os.path.expanduser('~/treeedit.key')
        if os.path.isfile(keyfile):
            egg = open(keyfile, 'rb').read().decode("base64")
            params = pickle.loads(egg)
        else:
            params = {'product': 'no key file'}
    except Exception, err:
        logging.exception('get key')
        params['product'] = err
    params['system'] = "%s-%s" % (os.environ['username'], os.environ['computername'])
    try:
        params['updateserveraccess'] = socket.getaddrinfo('rpc.content-monster.com', 80)
    except socket.error:
        params['updateserveraccess'] = 'no access'
    spam = pickle.dumps(params)
    e = des.encrypt(spam)
    fout.write(e)
