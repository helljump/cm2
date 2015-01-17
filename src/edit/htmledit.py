#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

from PyQt4 import QtGui, Qsci

class HtmlEdit(Qsci.QsciScintilla):

    def __init__(self, *args):
        Qsci.QsciScintilla.__init__(self, *args)
        font=QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(9)
        
        """
        lxr=Qsci.QsciLexerHTML()
        lxr.setDefaultFont(font)
        lxr.setFont(font)
        
        self.setLexer(lxr)
        """
        
        self.setUtf8(True)
        self.setFont(font)
        self.setMarginsFont(font)
        #self.setEdgeMode(Qsci.QsciScintilla.EdgeLine)
        #self.setEdgeColumn(80)
        #self.setEdgeColor(QtGui.QColor("#FFe0e0"))
        self.setBraceMatching(Qsci.QsciScintilla.SloppyBraceMatch)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#e0ffe0"))
        #self.setFolding(Qsci.QsciScintilla.BoxedFoldStyle)
        self.setWrapMode( Qsci.QsciScintilla.WrapWord ) #Qsci.QsciScintilla.WrapNone
    
        #delkey = QtGui.QShortcut(QtGui.QKeySequence("Delete"), self, 
        #    context=QtCore.Qt.WidgetShortcut)
        #delkey.activated.connect(self.delete_right_char)

        #def delete_right_char(self):
        #    print "delete"
