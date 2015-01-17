#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = 'helljump'

import logging
import grab

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


g = grab.Grab()

g.setup(log_dir='dump', debug_post=True,
    cookies={'csrftoken': '37TbBF80twC21SzbiLlZxMuLLbxMGFEa',
             'ACSID': 'AJKiYcFQWyFzJSSSJ3-TQ5f7TwgNQdMqg-Ov-iFeKYVCLf3QLKb8_jVfhzp6g2eEVEntQ8YV-yqWuIZjj5w1bbnSB2RB1zboVg1JVwTIUkB77zIWTlHc8QYX2fPx3m-KeCMOSfASDEAk0d5CnOdXV9bHfUYOrpkmYaSugjGWvhq1Z8-KLP8_asKcJNz1gWCKj20s0tBqusVW7EUVigxjJakrroQcJvZ7yqtE7lFCbln-BavM1CI4j243M7gfj8YWMngVyEygkIq6PZDDz6Msedeg9cnpWOg8r7X-s-rjDLWsU-jPydswvKkA5m1OlRrDv_R5Uq48OGWcp8zjv9_1M33op9HXIbswu7TW5On-9Zc_TtXZT6YhsHFedyh5ACnoIqVhJCx4nzNFOZzaE3o8D7qYws1jzhBDl3IXRRjc5logS4t-J6CR3Taq2nkCi1Z70R93x4_Fmknh98Z-82szOrjr2Jp4kTXqhwP29NncRo7vnHK6x2MdbGIhfeFYovTSp2UU4XznLo3DQaXMOkJA8l8nGVaT33iydJ7eVyyk8YLaCeVAXGe4tXsGWsOCLuJR8pIq2L764xIK'})

g.go('http://www.ingress.com/intel?ll=52.610912,39.591563&z=13')

g.setup(post='{"wd6yraf81bt8ocmt":["13_3964_2129","13_3964_2128","13_3963_2129","13_3965_2129"],"9ii571tgmncqmhce":"w226xg14997h0hoq","tt68wpncsrwm7vxn":"d6180e16ff30ce578d04d3d9f4bccbdb2fc05110","19nreawb47x5a4wu":93,"xoa39f1ge0qy2uim":-90000000,"s8d1s6ypvqhc1c9w":-180000000,"fdwasnkqc3tw3min":90000000,"0eudfw1vuc0mgfqh":180000000}')

g.go('http://www.ingress.com/r/w226xg14997h0hoq')
