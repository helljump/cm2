#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging 
__author__ = "snöa"

log = logging.getLogger(__name__)

tags = [
    ("Bold","<b>%(text)s</b>"),
    ("Italic","<i>%(text)s</i>"),
    ("Underline","<u>%(text)s</u>"),
    ("Strong","<strong>%(text)s</strong>"),
    ("Emphasis","<em>%(text)s</em>"),
    (),
    ("Link","<a href=\"\" title=\"\">%(text)s</a>"),
    ("Image","<img src=\"\" alt=\"\" title=\"\">%(text)s</img>"),
    (),
    ("Unordered List","<ul>%(text)s</ul>"),
    ("List element","<li>%(text)s</li>"),
    ("Paragraph","<p>%(text)s</p>"),
    ("Break line","%(text)s<br/>"),
    ("Quote","<quote>%(text)s</quote>"),
    ("Blockquote","<blockquote>%(text)s</blockquote>"),
]

def main():
    for title in tags:
        print title,

if __name__ == "__main__":
    main()
