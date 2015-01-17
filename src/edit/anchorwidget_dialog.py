# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'anchorwidget_dialog.ui'
#
# Created: Sat Mar 02 17:06:27 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(249, 118)
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.perarticle_rb = QtGui.QRadioButton(Dialog)
        self.perarticle_rb.setChecked(True)
        self.perarticle_rb.setObjectName(_fromUtf8("perarticle_rb"))
        self.gridLayout.addWidget(self.perarticle_rb, 1, 0, 1, 1)
        self.perchars_rb = QtGui.QRadioButton(Dialog)
        self.perchars_rb.setObjectName(_fromUtf8("perchars_rb"))
        self.gridLayout.addWidget(self.perchars_rb, 2, 0, 1, 1)
        self.perarticle_sb = QtGui.QSpinBox(Dialog)
        self.perarticle_sb.setObjectName(_fromUtf8("perarticle_sb"))
        self.gridLayout.addWidget(self.perarticle_sb, 1, 1, 1, 1)
        self.perchars_sb = QtGui.QSpinBox(Dialog)
        self.perchars_sb.setEnabled(False)
        self.perchars_sb.setObjectName(_fromUtf8("perchars_sb"))
        self.gridLayout.addWidget(self.perchars_sb, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.perarticle_rb, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.perarticle_sb.setEnabled)
        QtCore.QObject.connect(self.perarticle_rb, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.perchars_sb.setDisabled)
        QtCore.QObject.connect(self.perchars_rb, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.perchars_sb.setEnabled)
        QtCore.QObject.connect(self.perchars_rb, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.perarticle_sb.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Вставка ссылок", None, QtGui.QApplication.UnicodeUTF8))
        self.perarticle_rb.setText(QtGui.QApplication.translate("Dialog", "Ссылок на статью", None, QtGui.QApplication.UnicodeUTF8))
        self.perchars_rb.setText(QtGui.QApplication.translate("Dialog", "Ссылок на 1000 символов", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Вставка ссылок в выделенные статьи.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

