#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import logging
import requests
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:
    from utils.paths import CONFIGFILE
except ImportError:
    import sys
    sys.path.append('d:/work/cm2/src')
from config_dialog import SECTION_NAME
import shelve


log = logging.getLogger(__name__)


class AntigateError(Exception):
    pass


class Antigate(object):

    """
    >> ag = Antigate('9404cccf08797ec7d76bbe5224f')
    >> float(ag.get_balance()) > -1
    True
    >> th = ag.create_thread(open('/work/cm2/test/captcha.png', 'rb').read())
    >> th.start()
    >> while th.isRunning():
    ...     time.sleep(1)
    ...     log.debug('sleep 1 sec')
    >> if th.result:
    ...     print th.result.lower()
    ... else:
    ...     print th.error
    nxkm
    """

    SOFT_ID = '48'
    URL = "http://antigate.com"

    TIMEOUT = 60
    SLEEPTIME = 10

    def __init__(self, key):
        self.sess = requests.Session()
        self.key = key

    def check_error(self, rc):
        if rc.text.startswith("ERROR_"):
            raise AntigateError(rc.text)

    def get_balance(self):
        params = {
            'key': self.key,
            'action': 'getbalance'
        }
        rc = self.sess.get(self.URL + '/res.php', params=params)
        self.check_error(rc)
        return rc.text

    def _send(self, data, fname="captcha.png"):
        files = {'file': (fname, data)}
        params = {
            'key': self.key,
            'soft_id': self.SOFT_ID,
        }
        rc = self.sess.post(self.URL + "/in.php", data=params, files=files)
        self.check_error(rc)
        try:
            cap_id = rc.text.split("|")[1]
        except IndexError:
            log.exception(rc.text)
        return cap_id

    def _recv(self, cap_id):
        params = {
            'key': self.key,
            'soft_id': self.SOFT_ID,
            'action': 'get',
            'id': cap_id
        }
        rc = self.sess.get(self.URL + "/res.php", params=params)
        self.check_error(rc)
        if rc.text == "CAPCHA_NOT_READY":
            return None
        log.debug('rc %s', rc.text)
        text = rc.text.split("|")[-1]
        return text

    def create_thread(self, data, fname="captcha.png", parent=None):
        return AntigateThread(parent, self, data)


class CaptchaBot(Antigate):

    """
    captchabot with antigate interface

    >> ag = CaptchaBot('04750060896ad6f13b5d3e7a9e')
    >> float(ag.get_balance()) > -1
    True
    >> th = ag.create_thread(open('/work/cm2/test/captcha.png', 'rb').read())
    >> th.start()
    >> while th.isRunning():
    ...     time.sleep(1)
    ...     log.debug('sleep 1 sec')
    >> if th.result:
    ...     print th.result.lower()
    ... else:
    ...     print th.error
    nxkm
    """

    SOFT_ID = '174015'
    URL = 'http://captchabot.com'

class Ripcaptcha(Antigate):

    """
    ripcaptcha with antigate interface

    >>> ag = Ripcaptcha('be91baab890f9154b227c569')
    >>> float(ag.get_balance()) > -1
    True
    >>> th = ag.create_thread(open('/work/cm2/test/captcha.png', 'rb').read())
    >>> th.start()
    >>> while th.isRunning():
    ...     time.sleep(1)
    ...     log.debug('sleep 1 sec')
    >>> if th.result:
    ...     print th.result.lower()
    ... else:
    ...     print th.error
    nxkm
    """

    SOFT_ID = '1315'
    URL = 'http://ripcaptcha.com'


def get_service():
    sett = shelve.open(CONFIGFILE)
    c = sett.get(SECTION_NAME, {})
    service = None
    if c.get('antigate_on', False):
        key = c.get('antigate_key', '')
        if key:
            service = Antigate(key)
    elif c.get('captchabot_on', False):
        key = c.get('captchabot_key', '')
        if key:
            service = CaptchaBot(key)
    sett.close()
    return service


class AntigateThread(QThread):

    def __init__(self, parent, ag, data):
        QThread.__init__(self, parent)
        self.data = data
        self.ag = ag
        self.result = None
        self.error = None
        self.active = True

    def run(self):
        try:
            cap_id = self.ag._send(self.data)
            log.debug("cap_id %s", cap_id)
            t = time.time()
            while time.time() - t < self.ag.TIMEOUT:
                answer = self.ag._recv(cap_id)
                if answer:
                    log.debug("captcha_text %s", answer)
                    self.result = answer
                    break
                if not self.active:
                    raise AntigateError("ERROR_ANTIGATE_STOPPED")
                log.debug("catcha is not ready, sleep %i seconds", self.ag.SLEEPTIME)
                QThread.sleep(self.ag.SLEEPTIME)
            else:
                raise AntigateError("ERROR_ANTIGATE_TIMEOUT")
        except Exception, err:
            log.exception('AntigateThread exception')
            self.error = err

    def shutdown(self):
        self.active = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    import doctest
    doctest.testmod()
