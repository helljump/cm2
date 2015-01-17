# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CONFIG~1.UI'
#
# Created: Wed Jun 12 16:34:31 2013
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
        Dialog.resize(456, 270)
        self.gridLayout_4 = QtGui.QGridLayout(Dialog)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.autosavetimeout_sb = QtGui.QSpinBox(self.groupBox)
        self.autosavetimeout_sb.setMinimum(1)
        self.autosavetimeout_sb.setMaximum(60)
        self.autosavetimeout_sb.setProperty("value", 5)
        self.autosavetimeout_sb.setObjectName(_fromUtf8("autosavetimeout_sb"))
        self.gridLayout.addWidget(self.autosavetimeout_sb, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.connecttimeout_sb = QtGui.QSpinBox(self.groupBox_2)
        self.connecttimeout_sb.setMinimum(10)
        self.connecttimeout_sb.setMaximum(300)
        self.connecttimeout_sb.setProperty("value", 30)
        self.connecttimeout_sb.setObjectName(_fromUtf8("connecttimeout_sb"))
        self.gridLayout_2.addWidget(self.connecttimeout_sb, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.proxy_leb = LineEditButton(self.groupBox_2)
        self.proxy_leb.setObjectName(_fromUtf8("proxy_leb"))
        self.gridLayout_2.addWidget(self.proxy_leb, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.antigate_rb = QtGui.QRadioButton(self.groupBox_3)
        self.antigate_rb.setObjectName(_fromUtf8("antigate_rb"))
        self.gridLayout_3.addWidget(self.antigate_rb, 0, 0, 1, 1)
        self.antigate_le = QtGui.QLineEdit(self.groupBox_3)
        self.antigate_le.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.antigate_le.setObjectName(_fromUtf8("antigate_le"))
        self.gridLayout_3.addWidget(self.antigate_le, 0, 1, 1, 1)
        self.captchabot_rb = QtGui.QRadioButton(self.groupBox_3)
        self.captchabot_rb.setObjectName(_fromUtf8("captchabot_rb"))
        self.gridLayout_3.addWidget(self.captchabot_rb, 1, 0, 1, 1)
        self.captchabot_le = QtGui.QLineEdit(self.groupBox_3)
        self.captchabot_le.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.captchabot_le.setObjectName(_fromUtf8("captchabot_le"))
        self.gridLayout_3.addWidget(self.captchabot_le, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_4.addWidget(self.buttonBox, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.antigate_rb, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.antigate_le.setEnabled)
        QtCore.QObject.connect(self.captchabot_rb, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.captchabot_le.setEnabled)
        QtCore.QObject.connect(self.antigate_rb, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.captchabot_le.setDisabled)
        QtCore.QObject.connect(self.captchabot_rb, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.antigate_le.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Редактор", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Период автосохранения", None, QtGui.QApplication.UnicodeUTF8))
        self.autosavetimeout_sb.setSuffix(QtGui.QApplication.translate("Dialog", " минут", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Сеть", None, QtGui.QApplication.UnicodeUTF8))
        self.connecttimeout_sb.setSuffix(QtGui.QApplication.translate("Dialog", " секунд", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Таймаут сетевых операций", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Список прокси", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Dialog", "Капча", None, QtGui.QApplication.UnicodeUTF8))
        self.antigate_rb.setText(QtGui.QApplication.translate("Dialog", "Antigate", None, QtGui.QApplication.UnicodeUTF8))
        self.antigate_le.setPlaceholderText(QtGui.QApplication.translate("Dialog", "ключ", None, QtGui.QApplication.UnicodeUTF8))
        self.captchabot_rb.setText(QtGui.QApplication.translate("Dialog", "CaptchaBot", None, QtGui.QApplication.UnicodeUTF8))
        self.captchabot_le.setPlaceholderText(QtGui.QApplication.translate("Dialog", "ключ", None, QtGui.QApplication.UnicodeUTF8))

from lineeditbutton import LineEditButton

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

