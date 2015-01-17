#!/usr/bin/env python 
#-*- coding: UTF-8 -*-

__author__ = "helljump"

import sys
import StringIO
from PyQt4 import QtGui, uic, QtCore
from plugtypes import IUtilitePlugin
    

def nicepass(alpha=6, numeric=2):
    """
    returns a human-readble password (say rol86din instead of 
    a difficult to remember K8Yn9muL ) 
    """
    import string
    import random
    vowels = ['a', 'e', 'i', 'o', 'u']
    consonants = [a for a in string.ascii_lowercase if a not in vowels]
    digits = string.digits
    
    ####utility functions
    def a_part(slen):
        ret = ''
        for i in range(slen):			
            if i % 2 == 0:
                randid = random.randint(0, 20) #number of consonants
                ret += consonants[randid]
            else:
                randid = random.randint(0, 4) #number of vowels
                ret += vowels[randid]
        return ret
    
    def n_part(slen):
        ret = ''
        for i in range(slen): #@UnusedVariable
            randid = random.randint(0, 9) #number of digits
            ret += digits[randid]
        return ret
        
    #### 	
    fpl = alpha / 2		
    if alpha % 2 :
        fpl = int(alpha / 2) + 1 					
    lpl = alpha - fpl	
    
    start = a_part(fpl)
    mid = n_part(numeric)
    end = a_part(lpl)
    
    return "%s%s%s" % (start, mid, end)

ui = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Dialog</class>
 <widget class="QDialog" name="Dialog">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>380</width>
    <height>485</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Генератор паролей</string>
  </property>
  <layout class="QGridLayout" name="gridLayout">
   <item row="0" column="6">
    <widget class="QPushButton" name="pushButton">
     <property name="text">
      <string>Генерировать</string>
     </property>
    </widget>
   </item>
   <item row="0" column="1">
    <widget class="QSpinBox" name="chars_sbox">
     <property name="minimum">
      <number>6</number>
     </property>
     <property name="maximum">
      <number>12</number>
     </property>
    </widget>
   </item>
   <item row="0" column="0">
    <widget class="QLabel" name="label">
     <property name="text">
      <string>Символов</string>
     </property>
    </widget>
   </item>
   <item row="0" column="2">
    <widget class="QLabel" name="label_2">
     <property name="text">
      <string>Цифр</string>
     </property>
    </widget>
   </item>
   <item row="0" column="3">
    <widget class="QSpinBox" name="nums_sbox">
     <property name="minimum">
      <number>2</number>
     </property>
     <property name="maximum">
      <number>4</number>
     </property>
     <property name="value">
      <number>2</number>
     </property>
    </widget>
   </item>
   <item row="0" column="4">
    <widget class="QLabel" name="label_3">
     <property name="text">
      <string>Паролей</string>
     </property>
    </widget>
   </item>
   <item row="0" column="5">
    <widget class="QSpinBox" name="cnt_sbox">
     <property name="minimum">
      <number>10</number>
     </property>
    </widget>
   </item>
   <item row="1" column="0" colspan="7">
    <widget class="QPlainTextEdit" name="plainTextEdit"/>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
"""


class PwdDialog(QtGui.QDialog):
    def __init__(self, *args):
        super(PwdDialog, self).__init__(*args)
        uic.loadUi(StringIO.StringIO(ui), self)

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        chars = self.chars_sbox.value()
        nums = self.nums_sbox.value()
        cnt = self.cnt_sbox.value()
        for i in range(cnt):
            egg = nicepass(chars, nums)
            self.plainTextEdit.appendPlainText(egg)

            
class Plugin(IUtilitePlugin):    
    def run(self, parent):
        dlg = PwdDialog(parent)
        dlg.exec_()
