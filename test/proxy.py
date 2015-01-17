#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import random

proxy_list = [item.strip() for item in open("proxylist.txt").readlines()]

def get_random():
    return random.choice(proxy_list)
