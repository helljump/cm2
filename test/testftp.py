#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from ftplib import FTP
ftp = FTP("ftp.narod.ru", "anuytka1666", "dfk6i4fgmh")
ftp.login()
print ftp.retrlines('LIST')
#print ftp.storbinary('STOR proxy.txt', open('proxy.txt', 'rb') )
ftp.quit()
