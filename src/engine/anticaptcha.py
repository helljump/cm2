#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@author: snoa
"""

from PyQt4 import QtCore, QtGui
from browser import Browser, FormMethod
from urlparse import urlparse
from logging import debug, error
import time

antigate_url = "http://antigate.com"
programkey = '48'#eJwzsQAAAKIAbQ=='.decode("base64").decode("zip")

class CaptchaError(Exception): pass
class WrongKey(CaptchaError): pass
class WrongText(CaptchaError): pass

class Command(object): (TEXT, IMAGE, STOP) = range(3)

class AntiCaptcha_Dialog(QtGui.QDialog):
    '''Отображает картинку из image_data и поле ввода
    '''
    def __init__(self, image_data, parent=None):
        QtGui.QWidget.__init__(self, parent)        
        self.setWindowTitle(self.tr("Anticaptcha"))
        self.resize(400, 300)
        gridLayout = QtGui.QGridLayout(self)
        graphicsView = QtGui.QGraphicsView(self)
        gridLayout.addWidget(graphicsView, 0, 0, 1, 2)
        self.lineEdit = QtGui.QLineEdit(self)
        gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        gridLayout.addWidget(buttonBox, 2, 1, 1, 1)
        label = QtGui.QLabel(self.tr("Captcha text"), self)
        gridLayout.addWidget(label, 1, 0, 1, 1)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject) 
        scene = QtGui.QGraphicsScene()
        img = QtGui.QPixmap()
        img.loadFromData(image_data)
        scene.addPixmap(img)
        graphicsView.setScene(scene)
        self.lineEdit.setFocus()
        self.setResult(0)

    def accept(self):
        self.setResult(1)
        self.hide()
        
    def reject(self):
        self.setResult(0)
        self.hide()

    def get_text(self):
        return unicode(self.lineEdit.text())

def _get_aswer_from_antigate(data, userkey):
    """
    Получение текста с изображения через антигейт
    
    @param data: данные изображения
    @return: текст на изображении
    """
    cap_id = -1
    br = Browser()
    br.method = FormMethod.MULTIPART
    br.set_param("key", userkey)
    br.set_param("soft_id", programkey)
    br.set_file("captcha.jpg", data)
    br.open(antigate_url + "/in.php")
    if br.response.code == 200:
        if br.source == "ERROR_WRONG_USER_KEY":
            raise WrongKey()
        try:
            cap_id = int(br.source.split('|')[1])
            debug("cap_id [%i]" % cap_id)
        except:
            error("antigate response [%s]" % br.source)
    else:
        raise CaptchaError("Captcha not send [%s]" % br.response.code)
    time.sleep(5)
    while 1:
        br = Browser()
        br.method = FormMethod.GET
        br.set_param("key", userkey)
        br.set_param("action", "get")
        br.set_param("id", cap_id)    
        br.open(antigate_url + "/res.php")
        if br.source == 'CAPCHA_NOT_READY':
            debug("captcha not ready")
            time.sleep(1)
            continue
        break
    res = br.source.split('|')
    if len(res) == 2 and res[0] == "OK":
        debug("Captcha text status[%s] text[%s]" % (res[0], res[1]))
        return (res[1], cap_id)
    else:
        raise CaptchaError("Captcha getting error [%s]" % res[0])

def get_answer(data, queue=None, userkey="", imagequery_queue=None):
    """получение текста изображения
    если ключ задан - вызываем антигейт, иначе вызываем диалог
    
    @param data: данные изображения
    @param queue: очередь для запрашивания ответа на картинку
    @param userkey: антигейт ключ
    @return: текст
    """
    
    if userkey == "":
        if queue is None:
            raise CaptchaError("no key and no pipe")
        debug("put image in queue")
        imagequery_queue.put((Command.IMAGE, data), True)
        
        debug("getting image from queue")
        rc = queue.get(True)
        debug("got image from queue")
        if rc[0] == Command.TEXT:
            return (rc[1], -1)
        raise CaptchaError("no result from captcha dialog")
    else:
        return _get_aswer_from_antigate(data, userkey)

def get_recaptcha_answer(browser, recaptcha_url, pipe=None, userkey="", imagequery_queue=None):
    '''Получение ответа на recaptcha
    
    @param browser: созданный браузер
    @param recaptcha_url: ссылка на рекапчу(из iframe) recaptcha_url
        recaptcha_url = soup.find("iframe", attrs={"src":re.compile("api\.recaptcha\.net")})["src"]
    
    @return: возвращаем распознаный текст'''
    
    parsed = urlparse(recaptcha_url)
    browser.method = browser.FormMethod.POST
    soup = browser.open(recaptcha_url)
    browser.dump()
    recaptcha_image_url = soup.find("img", attrs={"id":"recaptcha_image"})["src"]
    debug("recaptcha img url %s", recaptcha_image_url)
    data = browser.get_data("%s://%s%s" % (parsed.scheme, parsed.netloc, recaptcha_image_url))
    captcha_text = get_answer(data, pipe, userkey, imagequery_queue)
    browser.set_param("recaptcha_response_field", captcha_text)
    browser.set_param("submit", "Im a Human")
    soup = browser.open(recaptcha_url)
    recaptcha_code = soup.find("textarea").contents[0].strip()
    debug("recaptcha code %s" % recaptcha_code)
    browser.set_param("recaptcha_response_field", "manual_challenge")
    return recaptcha_code

def get_antigate_balance(userkey):
    '''
    userkey = "9404cccf08797ec7d76bbe5224f"
    print get_antigate_balance(userkey)
    '''
    br = Browser()
    #time.sleep(10)
    br.method = FormMethod.GET
    br.set_param("key", userkey)
    br.set_param("action", "getbalance")
    br.open(antigate_url + "/res.php")
    if br.source == "ERROR_WRONG_USER_KEY":
        raise WrongKey("captcha key baaad")
    return br.source

#http://antigate.com/res.php?key=08797ec7d76bbe5224f&action=reportbad&id=CAPCHA_ID_HERE
def report_wrong_captcha(userkey, cap_id):
    br = Browser()
    br.method = FormMethod.GET
    br.set_param("key", userkey)
    br.set_param("action", "reportbad")
    br.set_param("id", cap_id)
    br.open(antigate_url + "/res.php")

if __name__ == '__main__':
    '''
    import sys
    app = QtGui.QApplication(sys.argv)
    data = open(r"d:\work\promidol\test\captcha.jpg", "rb").read()
    text = get_answer(data,userkey="404cccf08797ec7d76bbe5224f")
    print text
    '''
    #userkey =  "9404cccf08797ec7d76bbe5224f"
    #print get_antigate_balance(userkey)
    pass
