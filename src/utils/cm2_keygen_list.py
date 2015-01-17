#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import cPickle
import qthelpers
import datetime

MAILS = 'zeldor@bk.ru elikpro@mail.ru dimmonius-s@yandex.ru m4srom@yandex.ru adprofy@gmail.com niko-faza@yandex.ru'\
    ' ivanissov@mail.ru s_s0k0l0v@mail.ru Castercpa@gmail.com sn2369@gmail.com reg-adv@yandex.ru'\
    ' A-lott@yandex.ru'.split(' ')


TXT = """
Добрый день.
Мы благодарим Вас за покупку Content Monster II TreeEdit

Для начала работы

1. Зайдите в клиентскую зону CM-II TreeEdit
Адрес страницы http://content-monster.com/klientam
Пароль для входа: cm2cli8ts

2. Скачайте свежую версию CM-II TreeEdit

3. Установите (с правами администратора) вашу копию CM-II TreeEdit

4. Запустите CM-II TreeEdit

5. Пройдите в главном меню программы в раздел Помощь - Регистрация и введите ключ


------ Начинать копировать после этой строки ----------------
%s
------ Эту строчку - не копировать --------------------------

Будьте внимательными при копировании ключа!
Ключ является уникальным для вашей копии CM-II TreeEdit
и предназначен для использования на 2 машинах

6. Ваша копия готова к работе!

По всем вопросам пишите на форуме поддержки
http://blap.ru/forum/index.php?board=75.0

Желаем Вам удачи!

С уважением DrMax и sNOa

Тестовую версию плагина парсера rus/articlesbase можно скачать: http://blap.ru/download/36/
Для работы необходимы указать в настройках CM2 свежие прокси и антигейт либо капчабот аккаунт.

"""


def keygen(username):
    params = {}
    params['username'] = username
    params['product'] = "content-monster-2-treeedit"
    params['version'] = "1.0"
    params['date'] = str(datetime.datetime.today())
    params['key'] = qthelpers.gen(params)
    obj = cPickle.dumps(params, cPickle.HIGHEST_PROTOCOL)
    return obj.encode("base64")


with open("25bucks-keys.txt", "wt") as fout:
    for i in MAILS:
        username = "%s-25bucks" % i
        print username
        fout.write("\n\n      ====== %s =======      \n\n" % i)
        fout.write(TXT % keygen(username))
