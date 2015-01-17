#!/usr/bin/env python
# -*- coding: UTF-8 -*-

''' Работа с antigate.com '''

import time

import httplib, urllib, logging

def main():
	# тестим
	key= '11111111111111111111111111111'
	fn= 'captcha.jpg'
	
	# отправляем капчу
	cap_id= send_cap(key, fn)
	if not cap_id:
		print 'Не отправилось'
		return
		
	# получаем результат
	status, text= get_cap_text(key, cap_id) #@UnusedVariable
	print text
	


def get_cap_text(key, cap_id):
	''' Ожидаем и получаем текст капчи '''

	logging.info('--- Get captcha text')
	time.sleep(5)
	
	# получаем результат
	res_url= 'http://antigate.com/res.php'
	res_url+= "?" + urllib.urlencode({'key': key, 'action': 'get', 'id': cap_id})
	while 1:
		res= urllib.urlopen(res_url).read()
		if res == 'CAPCHA_NOT_READY':
			time.sleep(1)
			continue
		break
	
	res= res.split('|')
	if len(res) == 2:
		return tuple(res)
	else:
		return ('ERROR', res[0])
	


def send_cap(key, fn):
	''' Отправляем капчу на anti-capcha.com
		Вход:
			key	- ключ на антикапче
			fn		- файл с капчей
		Выход:
			id капчи	- в случае успеха
			False	- неудача
	'''
	logging.info('--- Send captcha')
	
	
	data = open(fn, 'rb').read()

	# разделитель для данных
	boundary= '----------OmNaOmNaOmNamo'

	# тело HTTP-запроса
	body = '''--%s
Content-Disposition: form-data; name="method"

post
--%s
Content-Disposition: form-data; name="key"

%s
--%s
Content-Disposition: form-data; name="file"; filename="capcha.jpg"
Content-Type: image/pjpeg

%s
--%s--

''' % (boundary, boundary, key, boundary, data, boundary)

	# заголовки HTTP-запроса
	headers = {'Content-type' : 'multipart/form-data; boundary=%s' % boundary}
	# подключение к HTTP-серверу
	h = httplib.HTTPConnection('antigate.com')
	# посылка запроса
	h.request("POST", "/in.php", body, headers)
	# получение и анализ ответа HTTP-сервера
	resp = h.getresponse()
	data = resp.read()
	h.close()
	if resp.status == 200:
		cap_id= int(data.split('|')[1])
		return cap_id
	else:
		logging.error('Captcha not send: %s %s' % (resp.status, resp.reason))
		return False

if __name__ == "__main__":
	main()