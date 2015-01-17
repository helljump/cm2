#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import logging
import requests
from data import key
import time


log = logging.getLogger(__name__)


class SkipException(Exception):
    pass


class YouTube(object):

    URL = "https://gdata.youtube.com/feeds/api/videos"
    PAGE = 10

    def __init__(self, queries, amount=1000, apikey="", stopwords = [],
            minlen = 10, timeq=""):
        self.queries = queries
        self.timeq = timeq
        self.results = 0
        self.query = None
        self.amount = amount
        self.stopwords = stopwords
        self.minlen = minlen
        self.headers = {"X-GData-Key": "key=" + key}
        if len(apikey) > 0:
            self.headers["X-GData-Key"] = "key=" + apikey

    def _get(self, url, **kwargs):
        c = 5
        while c>0:
            rc = requests.get(url, **kwargs)
            if rc.status_code == 200:
                return rc
            c -= 1
            time.sleep(1)
        raise SkipException("Too many errors")

    def get_items(self):
        for query in self.queries:
            if len(query.strip())==0:
                continue
            assert isinstance(query, unicode)
            self.query = query
            start_index = 1
            params = {"q": query, "max-results": YouTube.PAGE, "v": "2", "alt": "jsonc",
                "time": self.timeq}
            amount = self.amount
            try:
                while amount:
                    params["start-index"] = start_index  # индекс видео, не страницы!
                    rc = self._get(YouTube.URL, params=params, headers=self.headers, verify=False)
                    if rc.status_code != 200:
                        raise Exception(str(rc))
                    egg = rc.json()
                    #print egg
                    if "error" in egg:
                        raise Exception(egg["error"]["message"])
                    data = egg["data"]
                    self.results = int(data["totalItems"])
                    #print "results", self.results
                    if "items" not in data:
                        break
                    for item in data["items"]:
                        if self._swmatch(item["title"]) or self._swmatch(item["description"]):
                            continue
                        item["query"] = query
                        yield(item)
                        amount -= 1
                        if not amount:
                            break
                    start_index = int(data["startIndex"]) + YouTube.PAGE
                    if start_index > self.results:
                        break
            except SkipException, err:
                pass

    def _swmatch(self, text, minlen=1):
        text = text.lower()
        for word in self.stopwords:
            if text and word and text.find(word)!=-1:
                #print ">>>", word.encode("UTF-8")
                return True
        if len(text) < minlen:
            return True
        return False

    def get_comments(self, yid):
        url = YouTube.URL + "/" + yid + "/comments"
        #print "-->", url
        params = {"v": "2", "alt": "json"}
        rc = self._get(url, params=params, headers=self.headers, verify=False)
        if rc.status_code != 200:
            raise Exception(str(rc))
        egg = rc.json()
        if "error" in egg:
            raise Exception(egg["error"]["message"])
        if "entry" not in egg["feed"]:
            return []
        spam = [entry for entry in egg["feed"]["entry"]
            if not self._swmatch(entry["content"]["$t"], self.minlen)]
        return spam


def main():
    import shelve, json, codecs

    db = shelve.open("test.shelve")

    yt = YouTube([u"как играть на гитаре",], 30)
    try:
        for item in yt.get_items():
            print item["id"], item["title"].encode("utf-8")
            item["comments"] = yt.get_comments(item["id"])
            json.dump(item["comments"], codecs.open("comment.json", "w", "UTF-8"),
                indent=4, encoding="UTF-8", ensure_ascii=False)
            db[str(item["id"])] = item
            db.sync()
    finally:
        db.close()


if __name__ == '__main__':
    main()
