#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import logging

import os
from codecs import open as copen
from random import choice, randint, shuffle
from jinja2 import Environment, evalcontextfilter, Markup, escape
from yazzy import yasyn2
from yazzy.yasyn2 import ACDict
from json import load as jload
from pytils import numeral
import re
from itertools import cycle

log = logging.getLogger(__name__)

yasyn_cache = {}
dcache = {}
fromdir_cache = None


#json_dir, fname = os.path.split(__file__)
#json_dir = os.path.join(json_dir, "json")
json_dir = os.path.join(*__file__.split(os.path.sep)[-3:-1])

#yasyn_dir, fname = os.path.split(yasyn2.__file__)
#yasyn_dir = os.path.join(yasyn_dir, "dict")
yasyn_dir = "dict"

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


class JinjaException(Exception):
    pass


@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def my_shuffle(arr):
    shuffle(arr)
    return arr


def from_dir(dirname, emptystop=False):
    global fromdir_cache
    if fromdir_cache is None:
        log.debug('read dir')
        egg = [os.path.join(dirname, fname) for fname in os.listdir(dirname) if fname.endswith('.txt')]
        shuffle(egg)
        if emptystop:
            fromdir_cache = iter(egg)
        else:
            fromdir_cache = cycle(egg)
    try:
        nextname = fromdir_cache.next()
        data = copen(nextname, 'rt', 'UTF-8').read()
        return data
    except StopIteration:
        raise JinjaException()


def yasyn(value, dictname="internal", distant=0, template=False):
    if dictname not in yasyn_cache:
        print "load", dictname
        if dictname == "internal":
            from yazzy.fullthematik import internal_db
            d = yasyn2.load_py(internal_db)
        else:
            f, d = yasyn2.load(os.path.join(yasyn_dir, dictname))
        acd = ACDict()
        for item in d:
            if len(item) == 3:
                acd.addPhrase(item[0], item[1], item[2])
        yasyn_cache[dictname] = acd
    return yasyn_cache[dictname].search(value, distant, template)


def _format(s, v):
    try:
        s = s % v
    except TypeError:  # no params
        pass
    return s


def by_dict(value, dictname):
    try:
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            pass
    if dictname not in dcache:
        dcache[dictname] = jload(copen(os.path.join(json_dir, dictname), "rt", "utf-8", "replace"))
    rc = value
    for k, v in dcache[dictname].iteritems():
        if k.find("..") != -1:  # num range
            r1, r2 = [float(i) for i in k.split("..")]
            if value >= r1 and value <= r2:
                rc = _format(choice(v), value)
                break
        else:
            if type(value) == int:
                try:
                    k = int(k)
                except ValueError:
                    pass
            elif type(value) == float:
                try:
                    k = float(k)
                except (UnicodeEncodeError, ValueError):
                    pass
            if value == k:
                rc = _format(choice(v), value)
                break
    return rc


def my_inwords(v):
    try:
        v = int(v)
    except ValueError:
        try:
            v = float(v)
        except ValueError:
            pass
    return numeral.in_words(v)


def get_env():
    env = Environment(extensions=["jinja2.ext.loopcontrols"])

    env.filters["by_dict"] = by_dict
    env.filters["in_words"] = my_inwords
    env.filters["yasyn"] = yasyn
    env.filters["nl2br"] = nl2br
    env.filters["shuffle"] = my_shuffle

    env.globals["from_dir"] = from_dir
    env.globals["choice"] = choice
    env.globals["randint"] = randint

    return env

if __name__ == "__main__":
    print get_env()
