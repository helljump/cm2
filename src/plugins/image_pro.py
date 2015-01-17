# -*- coding: UTF-8 -*-

import sys

try:
    from plugtypes import IProcessPlugin
except ImportError:
    IProcessPlugin = object
    sys.path.append("d:/work/cm2/src")
    
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from utils.qthelpers import MyProgressDialog, MyPath
import re
import os
from pytils.translit import slugify
import shutil
import html5lib
import lxml.etree as ET
from utils.formlayout import fedit
from Queue import Queue, Empty
import functools
from utils.paths import pluginpath
import pickle


class PatchThread(QThread):
    
    task_progress = pyqtSignal(int)
    task_success = pyqtSignal(int)
    task_error = pyqtSignal(QString)

    def __init__(self, queue, parent=None):
        QThread.__init__(self, parent)
        self.queue = queue
        self.active = True
        
    def run(self):
        cnt = 0
        while self.active:
            try:
                task = self.queue.get_nowait()
                if task == "STOP":
                    self.task_success.emit(cnt)
                    return
                task()
                self.task_progress.emit(cnt)
                cnt += 1
            except RuntimeError, err:
                log.exception("patch thread")
                if self.active:
                    self.task_error.emit(unicode(err))
                return
            except Empty:
                pass
            QThread.usleep(100)
        log.debug("patch aborted")
        
    def die(self):
        self.active = False
        self.wait(100)

        
class ImagePro(IProcessPlugin):

    SETTINGS = os.path.join(pluginpath, os.path.basename(__file__) + ".pkl")
    
    def run(self, items, parent):
    
        if os.path.isfile(ImagePro.SETTINGS):
            settings = pickle.load(open(ImagePro.SETTINGS, "rt"))
        else:
            settings = [True, ".", True, True]
    
        datalist = [
            (u"Переименовывать изображения", settings[0]),
            (u"Каталог изображений:", settings[1]), 
            (u"Добавлять alt", settings[2]),
            (u"Делать ссылкой", settings[3]),
        ]
        
        rc = fedit(datalist, title=u"Правка изображений", parent=parent)
        if not rc:
            return
        rename, path, alt, link = rc
        
        settings = [rename, path, alt, link]
        pickle.dump(settings, open(ImagePro.SETTINGS, "wb"))
   
        parser = html5lib.HTMLParser(html5lib.getTreeBuilder('lxml'), namespaceHTMLElements=False)     
        configured = functools.partial(patch, parser, rename, path, alt, link)

        pd = MyProgressDialog(u"Обработка изображений", u"Формирование очереди", u"Отмена",
                0, len(items), parent=parent)
        pd.show()

        q = Queue()
        for item in items:
            task = functools.partial(configured, item.article)
            q.put(task)
        q.put("STOP")
        
        th = PatchThread(q, parent)
        
        def success(cnt):
            pd.setValue(cnt)
            QMessageBox.information(parent, u"Обработка изображений", u"Обработано %i статей." % cnt)
        
        def progress(cnt):
            if not pd.wasCanceled():
                pd.setValue(cnt)
        
        def error(msg):
            pd.close()
            QMessageBox.critical(parent, self.tr("Обработка изображений"), msg)
        
        def abort():
            th.die()

        pd.setLabelText(u"Обрабатываем статьи...")
        pd.canceled.connect(abort)
        th.task_success.connect(success)
        th.task_progress.connect(progress)
        th.task_error.connect(error)
        th.start()
        
        
def patch(parser, rename, path, alt, link, article):
    
    article.text = _patch(parser, rename, path, alt, link, article, article.text)
    if hasattr(article, "intro"):
        article.intro = _patch(parser, rename, path, alt, link, article, article.intro)

        
def _patch(parser, rename, path, alt, link, article, text):

    tree = parser.parse(text)
    
    for img in tree.xpath("//img"):
    
        #if alt and img.attrib.get("alt","")=="":
        if alt:
            img.attrib["alt"] = article.title

        if rename:
            pth, nme = os.path.split(img.attrib["src"])
            fnm, ext = os.path.splitext(nme)
            if pth.strip():
                sep = "/"
            else:
                sep = ""
            newname = "%s%s" % (slugify(article.title), ext)
            newfullname = "%s%s%s" % (pth, sep, newname)
            img.attrib["src"] = newfullname
            if os.path.isfile(os.path.join(path, nme)):
                os.rename(os.path.join(path, nme), os.path.join(path, newname))

        if link:
            prnt = img.getparent()
            if prnt.tag == "a":
                prnt.attrib["href"] = img.attrib["src"]
            else:
                a = ET.SubElement(prnt, "a")
                a.attrib["href"] = img.attrib["src"]
                a.tail = img.tail
                a.append(img)
                img.tail = ""
        
    text = ET.tostring(tree.find("body"), encoding=unicode)
    return text[6:-7] #strip body tag

        
TEST = u"""<img src="zlo1.jpg">Бутоны тёмные, каштаново-лиловые; цветки: темно-сиревато-лиловые с&nbsp;серебристым оттенком, крупные, махровые-из двух-трёх тесно сдвинутых венчиков, ароматные; нижние лепестки овальные, слегка приподнятые, верхние мельче и&nbsp;светлее. Метёлки широко-пирамидальные, крупные, рыхлые. Один из&nbsp;позднецветущих сортов со&nbsp;своеобразной окраской.

[gallery link="file" columns="4"] 
<img src="zlo2.jpg">
"""
   
if __name__ == "__main__":
    parser = html5lib.HTMLParser(html5lib.getTreeBuilder('lxml'), namespaceHTMLElements=False)
    t = parser.parse(TEST)
    for img in t.xpath("//img"):
        #print ET.tostring(img)
        #print img.getnext()
        prnt = img.getparent()
        if prnt.tag != "a":
            a = ET.SubElement(prnt, "a")
            a.attrib["href"] = img.attrib["src"]
            a.tail = img.tail
            a.append(img)
            img.tail = ""
    text = ET.tostring(t.find("body"), encoding=unicode)
    print text[6:-7]
    
