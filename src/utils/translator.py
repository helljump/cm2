#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from PyQt4 import QtCore

class Translator( QtCore.QTranslator ):
    def __init__( self, parent, lang ):
        QtCore.QTranslator.__init__( self, parent )
        self.load( lang )
    def translate( self, context, sourceText, hmm = None ):
        res = QtCore.QTranslator.translate( self, context, sourceText )
        if len( res ) == 0:
            res = QtCore.QString( unicode(sourceText, "utf-8") )
        return res
