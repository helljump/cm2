#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import cPickle
import qthelpers
import datetime
from binascii import a2b_base64


TXT = """

Добрый день.
Мы благодарим Вас за покупку Content Monster II TreeEdit, CMS Cadaver и Генератора Магазинов Pro

--- Content Monster 2 ---
Для начала работы

1. Зайдите в клиентскую зону CM-II TreeEdit
Адрес страницы http://content-monster.com/klientam
Пароль для входа: cm2cli8ts

2. Скачайте последнюю версию CM-II TreeEdit

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

--- Генератор магазинов ---

Для получения плагина:

1. Пройдите в клиентскую зону Content Monster II
http://content-monster.com/klientam

2. Скачайте дистрибутив из раздела ПЛАТНЫЕ ПЛАГИНЫ

3. Распакуйте архив с паролем
fe7xdEwo73vb#dx

4. Запустите инсталлятор и установите плагин

5. Ознакомтесь с документацией на плагин
http://content-monster.com/rasshireniya/generator-magazinov-pro

5.1 Экспериментальная версия генератора магазинов 2
Документация: http://blap.ru/exchange/shopgen2.pdf
Ссылка: http://content-monster.com/download/csv_import2_pro-2.2-cm2plugin-install.exe

По всем вопросам пишите на форуме поддержки
http://blap.ru/forum/index.php?topic=1015.0

--- Кадавр ---

1. Пройдите в клиентскую зону CMS
http://content-monster.com/cms-kadavr/klientskaya-zona-kadavr-cms
Для входа используйте пароль: CM2CMSTREE

2. Скачайте дистрибутив CMS из клиентской зоны

3. Ознакомьтесь с документацией по использованию
http://content-monster.com/doc-cadaver/

4. Посмотрите видео демонстрацию
http://blap.ru/exchange/demo/cadavre.html

По всем вопросам пишите на форуме поддержки
http://blap.ru/forum/index.php?topic=953.0

Желаем Вам удачи!

С уважением DrMax и sNOa
"""


def keygen(username):
    params = {}
    params['username']=username
    params['product']="content-monster-2-treeedit"
    params['version']="1.0"
    params['date']=str(datetime.datetime.today())
    params['key']=qthelpers.gen(params)
    obj = cPickle.dumps(params, cPickle.HIGHEST_PROTOCOL)
    return obj.encode("base64")


for i in range(30, 40):
    fout = open("keys/key%02i.txt" % i, "wt")
    username = "sklad092013-key%02i" % i
    print username
    fout.write(TXT % keygen(username))
