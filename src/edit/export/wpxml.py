#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from lxml import etree
import html5lib

from pytils.translit import slugify
from datetime import datetime 
from logging import debug, exception
from utils.article import Article
import traceback

from PyQt4 import QtCore
from PyQt4.QtCore import QThread

"""
<wp:wxr_version>1.1</wp:wxr_version>
<wp:author>
    <wp:author_id>1</wp:author_id>
    <wp:author_login>admin</wp:author_login>
    <wp:author_email>ad@min.ru</wp:author_email>
    <wp:author_display_name><![CDATA[admin]]></wp:author_display_name>
    <wp:author_first_name><![CDATA[]]></wp:author_first_name>
    <wp:author_last_name><![CDATA[]]></wp:author_last_name>
</wp:author>
"""

dirty_patch = {
    "http://wordpress.org/export/1.1/excerpt/":"http://wordpress.org/export/1.0/excerpt/",
    "http://wordpress.org/export/1.1/":"http://wordpress.org/export/1.0/"
}

nsmap = {
    "excerpt":"http://wordpress.org/export/1.0/excerpt/",
    "content":"http://purl.org/rss/1.0/modules/content/",
    "wfw":"http://wellformedweb.org/CommentAPI/",
    "dc":"http://purl.org/dc/elements/1.1/",
    "wp":"http://wordpress.org/export/1.0/"
}

class IntroMode(object): EXCERPT, MORETAG = range(2)

class Export(QThread):
    def __init__(self, tree, fname, mode=IntroMode.EXCERPT, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.tree = tree
        self.fname = unicode(fname)
        self.progressdialog = progressdialog
        self.error = None
        self.mode = mode
        
    def run(self):
        try:
            writer = WPXMLWriter(self.tree, self.progressdialog, self.mode)
            writer.ptype = self.ptype
            writer.write(self.fname)
        except:
            exception("export error")
            self.error = traceback.format_exc()
        
    def stop(self):
        debug("terminate")
        self.terminate()
        debug("wait")
        self.wait()

class WPXMLWriter(object):
    """
    import cPickle
    tree = cPickle.load(open("wpxml.prt","rb"))
    writer = WPXMLWriter(tree)
    writer.write("test.xml")
    """

    def __init__(self, tree, progressbar=None, mode=IntroMode.EXCERPT):
        xmlns = [ "xmlns:%s=\"%s\"" % (k, v) for k, v in nsmap.items() ]
        header = "<rss version=\"2.0\" " + " ".join(xmlns) + "/>"
        self.root = etree.XML(header)
        self.channel = etree.SubElement(self.root, "channel")
        etree.SubElement(self.channel, "generator").text = "Promidol TreeEdit"        
        self.mode = mode
        
        #3.1 importer
        etree.SubElement(self.channel, "{%(wp)s}wxr_version" % nsmap).text = "1.1"
        author = etree.SubElement(self.channel, "{%(wp)s}author" % nsmap)
        etree.SubElement(author, "{%(wp)s}author_id" % nsmap).text = "1"
        etree.SubElement(author, "{%(wp)s}author_login" % nsmap).text = "admin"
        etree.SubElement(author, "{%(wp)s}author_email" % nsmap).text = "ad@min.ru"
        etree.SubElement(author, "{%(wp)s}author_display_name" % nsmap).text = etree.CDATA("admin")
        etree.SubElement(author, "{%(wp)s}author_first_name" % nsmap).text = etree.CDATA("")
        etree.SubElement(author, "{%(wp)s}author_last_name" % nsmap).text = etree.CDATA("")
        
        self.pd = progressbar
        self._id = 0
        self.tree = tree

    @property
    def id(self):
        self._id += 1
        return self._id

    def add_category(self, element, parent):
        title = element.title
        if self.pd: self.pd.set_text(u"Добавление категории %s" % title)
        category = etree.SubElement(self.channel, "{%(wp)s}category" % nsmap)
        etree.SubElement(category, "{%(wp)s}category_nicename" % nsmap).text = slugify(title)
        etree.SubElement(category, "{%(wp)s}category_parent" % nsmap).text = parent
        etree.SubElement(category, "{%(wp)s}cat_name" % nsmap).text = etree.CDATA(title)
        if element.text:
            etree.SubElement(category,
                "{%(wp)s}category_description" % nsmap).text = etree.CDATA(element.text)

    def add_tag(self, title):
        if self.pd: self.pd.set_text(u"Добавление метки %s" % title)
        tag = etree.SubElement(self.channel, "{%(wp)s}tag" % nsmap)
        etree.SubElement(tag, "{%(wp)s}tag_slug" % nsmap).text = slugify(title)
        etree.SubElement(tag, "{%(wp)s}tag_name" % nsmap).text = etree.CDATA(title)

    def add_post(self, element, parent):
        item = etree.SubElement(self.channel, "item")
        if self.pd: self.pd.set_text(u"Добавление статьи %s" % element.title)
        etree.SubElement(item, "title").text = element.title
        id = self.id
        if type(parent) == type(u""):
            etree.SubElement(item, "{%(wp)s}post_parent" % nsmap).text = "0"
        else:
            etree.SubElement(item, "{%(wp)s}post_parent" % nsmap).text = str(parent)
        etree.SubElement(item, "{%(wp)s}post_id" % nsmap).text = str(id)
        etree.SubElement(item, "{%(wp)s}status" % nsmap).text = "publish"
        etree.SubElement(item, "{%(wp)s}post_type" % nsmap).text = self.ptype
        etree.SubElement(item, "{%(wp)s}post_name" % nsmap).text = slugify(element.title)
        etree.SubElement(item, "{%(wp)s}post_date" % nsmap).text = element.date.strftime("%Y-%m-%d %H:%M:%S")
        etree.SubElement(item, "category").text = etree.CDATA(parent)
        etree.SubElement(item, "category", domain="category",
            nicename=slugify(parent)).text = etree.CDATA(parent)
        
        egg_intro = getattr(element, "intro", u"")
        if self.mode == IntroMode.EXCERPT:
            etree.SubElement(item, "{%(excerpt)s}encoded" % nsmap).text = etree.CDATA(egg_intro)
            etree.SubElement(item, "{%(content)s}encoded" % nsmap).text = etree.CDATA(element.text)            
        elif self.mode == IntroMode.MORETAG:
            etree.SubElement(item, "{%(excerpt)s}encoded" % nsmap).text = etree.CDATA(u"")
            if egg_intro:
                etree.SubElement(item, "{%(content)s}encoded" % nsmap).text = etree.CDATA("%s\n<!--more-->\n%s" % (egg_intro, element.text))
            else:
                etree.SubElement(item, "{%(content)s}encoded" % nsmap).text = etree.CDATA(element.text)
        
        for tag in element.tags:
            etree.SubElement(item, "category", domain="tag").text = etree.CDATA(tag)
            etree.SubElement(item, "category", domain="tag", nicename=slugify(tag)).text = etree.CDATA(tag)
            self.add_tag(tag)            
            
        """
        <wp:postmeta>
            <wp:meta_key>myfield1</wp:meta_key>
            <wp:meta_value>myvalue1</wp:meta_value>
        </wp:postmeta>
        """
        if hasattr(element, "meta"):
            for k,v in element.meta.items():
                meta = etree.SubElement(item, "{%(wp)s}postmeta" % nsmap)
                etree.SubElement(meta, "{%(wp)s}meta_key" % nsmap).text = k
                etree.SubElement(meta, "{%(wp)s}meta_value" % nsmap).text = v
        return id

    def __str__(self):
        return etree.tostring(self.root, pretty_print=True)
        
    def write(self, fout):
        self.make_tree()
        if self.pd: self.pd.set_text(u"Запись файла")
        tree = etree.ElementTree(self.root)
        tree.write(open(fout, "wt"), encoding="UTF-8", xml_declaration=True,
            pretty_print=True)

    def make_tree(self):
        deep = 0 #@UnusedVariable
        def recurse_tree(tree, parent=u"", deep=0):
            for item in tree.get_children():
                if not deep or item.get_children():
                    #print "%s c:%s" % ("-"*deep, slugify(item.title))
                    self.add_category(item, parent)
                    recurse_tree(item, item.title, deep + 1)
                else:
                    #print "%s a:%s" % ("-"*deep, slugify(item.title))
                    id = self.add_post(item, parent)
                    recurse_tree(item, id, deep + 1)
        recurse_tree(self.tree)

class Import(QThread):    
    def __init__(self, fname, progressdialog=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.fname = unicode(fname)
        self.pd = progressdialog
        self.result = None
        
    def run(self):
        try:
            reader = WPXMLReader(self.fname, self.pd)
            self.result = reader.make_tree()
        except:
            exception("import error")
            self.error = traceback.format_exc()
        
    def stop(self):
        debug("terminate")
        self.terminate()
        debug("wait")
        self.wait()

class SimpleReader(object):
    def __init__(self, finp, progressbar=None):
        self.pd = progressbar
        data = open(finp, "rb").read()
        #tree = html5lib.parse(data, treebuilder="lxml",  namespaceHTMLElements=False)
        
        from html5lib import treewalkers
        walker = treewalkers.getTreeWalker("dom")
        stream = walker(data)
        for o in stream:
            print o
        #self.categories = self._get_cats(tree)
        
    def _get_cats(self, tree):
        print tree.xpath("channel/category")
        
class WPXMLReader(object):
    """
    reader = WPXMLReader('sireniru.2010-04-20.xml')
    import cPickle
    cPickle.dump(reader.make_tree(), open("wpxml.prt","wb"), cPickle.HIGHEST_PROTOCOL )
    """
    def __init__(self, finp, progressbar=None):
        self.pd = progressbar
        #self.tree = etree.parse(finp)
        egg = open(finp, "rb").read()
        
        for k,w in dirty_patch.items():
            egg = egg.replace(k,w)
        
        if egg.find('http://wordpress.org/export/1.0/excerpt/') == -1:
            debug("patching xml - add excerpt namespace")
            egg = egg.replace(
                '<rss version="2.0"',
                '''<rss version="2.0"
                xmlns:excerpt="http://wordpress.org/export/1.0/excerpt/"
                ''')
        
        self.tree = etree.fromstring(egg)
        self.get_cats()
        self.get_posts()
        debug("cats: %i" % len(self.cats))
        debug("posts: %i" % len(self.posts))

    def get_cats(self):
        if self.pd: self.pd.set_text(u"Формирование списка категорий")
        self.cats = {}
        for item in self.tree.iterfind("channel/{%(wp)s}category" % nsmap):
            parent = item.find("{%(wp)s}category_parent" % nsmap).text
            title = item.find("{%(wp)s}cat_name" % nsmap).text
            self.cats[title] = { "parent":parent }

    def get_posts(self):
        if self.pd: self.pd.set_text(u"Формирование списка страниц")
        self.posts = {}
        for item in self.tree.iterfind("channel/item"):
            debug("title %s" % item.find("title").text)
            try:
                post_type = item.find("{%(wp)s}post_type" % nsmap).text
            except AttributeError:
                post_type = "post"
            if post_type == "post":
                egg = item.find("title")
                if egg.text is None:
                    title = u"Без имени"
                else:
                    title = egg.text.strip()
                try:
                    dateegg = item.find("{%(wp)s}post_date" % nsmap).text
                    post_date = datetime.strptime(dateegg, "%Y-%m-%d %H:%M:%S")
                except (ValueError, AttributeError):
                    post_date = datetime.now()
                
                #post_id = 1
                #if item.find("{%(wp)s}post_id" % nsmap):
                post_id = int(item.find("{%(wp)s}post_id" % nsmap).text)
                
                text = item.find("{%(content)s}encoded" % nsmap).text
                
                egg = item.find("{%(excerpt)s}encoded" % nsmap)
                if egg is None:
                    excerpt = None
                else:
                    excerpt = egg.text
                
                #postparent_tag = item.find("{%(wp)s}post_parent" % nsmap)
                #if postparent_tag:
                parent = int(item.find("{%(wp)s}post_parent" % nsmap).text)
                #else:
                #    parent = 0
                                
                categg = item.findall("category[@nicename][@domain]")
                tags = []
                categories = []
                for cat in categg:
                    if cat.attrib["domain"] == "tag":
                        tags.append(cat.text)
                    if cat.attrib["domain"] == "category":
                        categories.append(cat.text)
                post = {"parent_id":parent,
                    "title":title,
                    "date":post_date,
                    "text":text,
                    "tags":tags,
                    "categories":categories}
                if excerpt:
                    #debug("add post intro")
                    post["intro"] = excerpt
                self.posts[post_id] = post

    def get_post_by_category(self, category):
        rc = []
        for k, v in self.posts.items():
            if category in v["categories"]:
                rc.append(k)
        return rc

    def get_post_by_parentid(self, parent_id):
        rc = []
        for k, v in self.posts.items():
            if parent_id == v["parent_id"]:
                rc.append(k)
        return rc

    def add_subarts(self, parent, parent_id):
        if self.pd: self.pd.set_text(u"Добавление страниц")
        if type(parent_id) == type(u"") :
            idlist = self.get_post_by_category(parent_id)
        else:
            idlist = self.get_post_by_parentid(parent_id)
        for post_id in idlist:
            post = self.posts[post_id]
            catart = Article(post['title'], post['text'], post['tags'], post['date'])
            if post.has_key('intro'):
                #debug("add article intro")
                catart.intro = post['intro']
            catart.id = post_id
            parent.add_child(catart)
            self.add_subarts(catart, post_id)

    def add_subcats(self, parent, title=None):
        if self.pd: self.pd.set_text(u"Добавление категорий")
        for k, v in self.cats.items():
            if v['parent'] == title:
                article = Article(k, u"")
                self.add_subarts(article, k)                    
                parent.add_child(article)
                self.add_subcats(article, k)

    def make_tree(self):
        root = Article()
        self.add_subcats(root)
        return root

def print_tree(root):
    for item in root.children:
        if hasattr(item, 'intro'):
            print "%s(%i)" % (item.title, len(item.children))

if __name__ == "__main__":
    #import cPickle
    #tree = cPickle.load(open("d:\work\promidol\src\edit\wpxmlerror.prt", "rb"))
    #writer = WPXMLWriter(tree)
    #writer.write("wpxmlerror.xml")
    reader = SimpleReader('d:/work/cm2/test/sireniru.2010-04-20.xml')
    #import cPickle
    #cPickle.dump(reader.make_tree(), open("wpxml.prt","wb"), cPickle.HIGHEST_PROTOCOL )
