#!/usr/bin/env python
#-*- coding: UTF-8 -*-

__author__ = "helljump"

from PyQt4 import QtCore, QtGui
#import lineeditbutton_rc

class LineEditButton(QtGui.QWidget):

    __pyqtSignals__ = ("clicked(bool)",)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.button = QtGui.QPushButton(parent=self)
        self.button.setText("...")
        self.button.setFlat(True)
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.clicked.connect(self.clicked)

        self.edit = QtGui.QLineEdit(self)

        layout.addWidget(self.edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def placeholderText(self):
        return self.edit.placeholderText()

    def setPlaceholderText(self, text):
        self.edit.setPlaceholderText(text)

    placeholderText = QtCore.pyqtProperty("QString", placeholderText, setPlaceholderText)

    def text(self):
        return self.edit.text()

    def setText(self, text):
        self.edit.setText(text)

    text = QtCore.pyqtProperty("QString", text, setText)

    def icon(self):
        return self.button.icon()

    def setIcon(self, icon):
        self.button.setText("")
        self.button.setIcon(icon)

    icon = QtCore.pyqtProperty("QIcon", icon, setIcon)


if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    w = LineEditButton()
    w.show()
    sys.exit(app.exec_())
