#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snoa"

from SimpleXMLRPCServer import SimpleXMLRPCServer
import logging

log = logging.getLogger(__name__)

def new_article(parent, title, text, tags, pubdate):
    log.debug("""NEW ARTICLE
    title:   %s
    parent:  %s
    textlen: %i
    tags:    %i
    pubdate: %s
    """, title, parent, len(text), len(tags), pubdate)
    return True

def check_connection():
    return True

server = SimpleXMLRPCServer(("localhost", 8000))
log.debug("Listening on port 8000...")
server.register_function(check_connection)
server.register_function(new_article)
server.serve_forever()
