#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

#TODO: добавить к читателю работу с прогрессбаром

from lxml import etree
from pytils.translit import slugify
from datetime import datetime 
from logging import debug
from utils.article import Article

nsmap = {
    "excerpt":"http://wordpress.org/export/1.0/excerpt/",
    "content":"http://purl.org/rss/1.0/modules/content/",
    "wfw":"http://wellformedweb.org/CommentAPI/",
    "dc":"http://purl.org/dc/elements/1.1/",
    "wp":"http://wordpress.org/export/1.0/"
}

class WPXMLWriter(object):
    """
    writer = WPXMLWriter()
    writer.add_category(u"SEO дайджест","")
    writer.add_category(u"SEO subдайджест",u"SEO дайджест 1")
    writer.add_tag(u"5000$")
    writer.write("test.xml")
    """

    def __init__(self, progressbar=None):
        xmlns = [ "xmlns:%s=\"%s\"" % (k,v) for k,v in nsmap.items() ]
        header = "<rss version=\"2.0\" " + " ".join(xmlns) + "/>"
        self.root = etree.XML(header)
        self.channel = etree.SubElement(self.root,"channel")
        etree.SubElement(self.channel, "generator").text = "promidol treeedit 0.1"
        self.pb = progressbar
        self._id = 0

    @property
    def id(self):
        self._id+=1
        return self._id

    def add_category(self, element, parent):
        title = element.title
        category = etree.SubElement(self.channel, "{%(wp)s}category" % nsmap)
        etree.SubElement(category, "{%(wp)s}category_nicename" % nsmap).text = slugify(title)
        etree.SubElement(category, "{%(wp)s}category_parent" % nsmap).text = parent
        etree.SubElement(category, "{%(wp)s}cat_name" % nsmap).text = etree.CDATA(title)

    def add_tag(self, title):
        tag = etree.SubElement(self.channel, "{%(wp)s}tag" % nsmap)
        etree.SubElement(tag, "{%(wp)s}tag_slug" % nsmap).text = slugify(title)
        etree.SubElement(tag, "{%(wp)s}tag_name" % nsmap).text = etree.CDATA(title)

    def add_post(self, element, parent):
        item = etree.SubElement(self.channel, "item")
        etree.SubElement(item, "title").text = element.title
        id = self.id
        if type(parent)==type(u""):
            etree.SubElement(item, "{%(wp)s}post_parent" % nsmap).text = "0"
        else:
            etree.SubElement(item, "{%(wp)s}post_parent" % nsmap).text = str(parent)
        etree.SubElement(item, "{%(wp)s}post_id" % nsmap).text = str(id)
        etree.SubElement(item, "{%(wp)s}status" % nsmap).text = "publish"
        etree.SubElement(item, "{%(wp)s}post_type" % nsmap).text = "post"
        etree.SubElement(item, "{%(wp)s}post_name" % nsmap).text = slugify(element.title)
        etree.SubElement(item, "{%(wp)s}post_date" % nsmap).text = element.date.strftime("%Y-%m-%d %H:%M:%S")
        etree.SubElement(item, "category").text = etree.CDATA(parent)
        etree.SubElement(item, "category", domain="category", 
            nicename=slugify(parent) ).text = etree.CDATA(parent)
        etree.SubElement(item, "{%(content)s}encoded" % nsmap).text = etree.CDATA(element.text)
        for tag in element.tags:
            etree.SubElement(item, "category", domain="tag").text = etree.CDATA(tag)
            etree.SubElement(item, "category", domain="tag", nicename=slugify(tag)).text = etree.CDATA(tag)
            self.add_tag(tag)
        return id

    def __str__(self):
        return etree.tostring(self.root, pretty_print=True)
        
    def write(self, fout):
        tree = etree.ElementTree(self.root)
        tree.write( open(fout,"wt"), encoding="UTF-8", xml_declaration=True, pretty_print=True)

import cPickle
tree = cPickle.load(open("wpxml.prt","rb"))
writer = WPXMLWriter()

def recurse_tree(tree, parent=u""):
    for item in tree.get_children():
        if not type(parent)!=type(0) and not item.text.strip():
            writer.add_category(item, parent)
            recurse_tree(item, item.title)
        else:
            id = writer.add_post(item, parent)
            recurse_tree(item, id)

recurse_tree(tree)
writer.write("test.xml")

class WPXMLReader(object):
    """
    reader = WPXMLReader('sireniru.2010-04-20.xml')
    import cPickle
    cPickle.dump(reader.make_tree(), open("wpxml.prt","wb"), cPickle.HIGHEST_PROTOCOL )
    """
    def __init__(self, finp, progressbar=None):
        self.tree = etree.parse(finp)
        self.get_cats()
        self.get_posts()
        debug("cats: %i" % len(self.cats))
        debug("posts: %i" % len(self.posts))

    def get_cats(self):
        self.cats = {}
        for item in self.tree.iterfind("channel/{%(wp)s}category" % nsmap):
            parent = item.find("{%(wp)s}category_parent" % nsmap).text
            title = item.find("{%(wp)s}cat_name" % nsmap).text
            self.cats[title] = { "parent":parent }

    def get_posts(self):
        self.posts = {}
        for item in self.tree.iterfind("channel/item"):
            post_type = item.find("{%(wp)s}post_type" % nsmap).text
            if post_type == "post":
                title = item.find('title').text.strip()
                dateegg = item.find("{%(wp)s}post_date" % nsmap).text
                post_date = datetime.strptime(dateegg,"%Y-%m-%d %H:%M:%S")
                post_id = int(item.find("{%(wp)s}post_id" % nsmap).text)
                text = item.find("{%(content)s}encoded" % nsmap).text
                parent = int(item.find("{%(wp)s}post_parent" % nsmap).text)            
                categg = item.findall("category[@nicename][@domain]")
                tags = []
                categories = []
                for cat in categg:
                    if cat.attrib["domain"]=="tag":
                        tags.append(cat.text)
                    if cat.attrib["domain"]=="category":
                        categories.append(cat.text)
                post = {"parent_id":parent,
                    "title":title,
                    "date":post_date,
                    "text":text,
                    "tags":tags,
                    "categories":categories}
                self.posts[post_id] = post

    def get_post_by_category(self, category):
        rc = []
        for k,v in self.posts.items():
            if category in v["categories"]:
                rc.append(k)
        return rc

    def get_post_by_parentid(self, parent_id):
        rc = []
        for k,v in self.posts.items():
            if parent_id == v["parent_id"]:
                rc.append(k)
        return rc

    def add_subarts(self, parent, parent_id ):
        if type(parent_id) == type(u"") :
            idlist = self.get_post_by_category(parent_id)
        else:
            idlist = self.get_post_by_parentid(parent_id)
        for post_id in idlist:
            post = self.posts[post_id]
            catart = Article( post['title'], post['text'], post['tags'], post['date'] )
            catart.id = post_id
            parent.add_child(catart)
            self.add_subarts(catart, post_id)

    def add_subcats(self, parent, title=None ):
        for k,v in self.cats.items():
            if v['parent']==title:
                article = Article( k, u"" )
                self.add_subarts(article, k)                    
                parent.add_child(article)
                self.add_subcats(article, k)

    def make_tree(self):
        root = Article()
        self.add_subcats(root)
        return root

