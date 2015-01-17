# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created: Sun Dec 09 21:14:36 2012
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
        Dialog.resize(831, 636)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.fname_le = QtGui.QLineEdit(self.groupBox)
        self.fname_le.setReadOnly(True)
        self.fname_le.setObjectName(_fromUtf8("fname_le"))
        self.gridLayout.addWidget(self.fname_le, 0, 1, 1, 5)
        self.selectfile_bp = QtGui.QPushButton(self.groupBox)
        self.selectfile_bp.setMaximumSize(QtCore.QSize(24, 16777215))
        self.selectfile_bp.setObjectName(_fromUtf8("selectfile_bp"))
        self.gridLayout.addWidget(self.selectfile_bp, 0, 6, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 7, 1, 1)
        self.encoding_cb = QtGui.QComboBox(self.groupBox)
        self.encoding_cb.setObjectName(_fromUtf8("encoding_cb"))
        self.encoding_cb.addItem(_fromUtf8(""))
        self.encoding_cb.addItem(_fromUtf8(""))
        self.encoding_cb.addItem(_fromUtf8(""))
        self.encoding_cb.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.encoding_cb, 0, 8, 1, 2)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 2)
        self.fielddelim_le = QtGui.QLineEdit(self.groupBox)
        self.fielddelim_le.setObjectName(_fromUtf8("fielddelim_le"))
        self.gridLayout.addWidget(self.fielddelim_le, 1, 2, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 3, 1, 1)
        self.textdelim_le = QtGui.QLineEdit(self.groupBox)
        self.textdelim_le.setObjectName(_fromUtf8("textdelim_le"))
        self.gridLayout.addWidget(self.textdelim_le, 1, 4, 1, 1)
        self.ignorefirst_cb = QtGui.QCheckBox(self.groupBox)
        self.ignorefirst_cb.setChecked(True)
        self.ignorefirst_cb.setObjectName(_fromUtf8("ignorefirst_cb"))
        self.gridLayout.addWidget(self.ignorefirst_cb, 1, 5, 1, 4)
        self.allowcat_cb = QtGui.QCheckBox(self.groupBox)
        self.allowcat_cb.setChecked(True)
        self.allowcat_cb.setObjectName(_fromUtf8("allowcat_cb"))
        self.gridLayout.addWidget(self.allowcat_cb, 1, 9, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.dicts_lw = QtGui.QListWidget(self.groupBox_3)
        self.dicts_lw.setAlternatingRowColors(True)
        self.dicts_lw.setObjectName(_fromUtf8("dicts_lw"))
        self.gridLayout_4.addWidget(self.dicts_lw, 0, 0, 1, 1)
        self.inwords_cb = QtGui.QCheckBox(self.groupBox_3)
        self.inwords_cb.setObjectName(_fromUtf8("inwords_cb"))
        self.gridLayout_4.addWidget(self.inwords_cb, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_3, 2, 0, 1, 2)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.title_le = QtGui.QLineEdit(self.groupBox_2)
        self.title_le.setObjectName(_fromUtf8("title_le"))
        self.gridLayout_3.addWidget(self.title_le, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 0, 2, 1, 1)
        self.tags_le = QtGui.QLineEdit(self.groupBox_2)
        self.tags_le.setText(_fromUtf8(""))
        self.tags_le.setObjectName(_fromUtf8("tags_le"))
        self.gridLayout_3.addWidget(self.tags_le, 0, 3, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_3.addWidget(self.label_7, 1, 0, 1, 1)
        self.text_le = QtGui.QPlainTextEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.text_le.sizePolicy().hasHeightForWidth())
        self.text_le.setSizePolicy(sizePolicy)
        self.text_le.setObjectName(_fromUtf8("text_le"))
        self.gridLayout_3.addWidget(self.text_le, 4, 0, 1, 4)
        self.label_8 = QtGui.QLabel(self.groupBox_2)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 5, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.groupBox_2)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_3.addWidget(self.label_9, 7, 0, 1, 1)
        self.intro_le = QtGui.QPlainTextEdit(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.intro_le.sizePolicy().hasHeightForWidth())
        self.intro_le.setSizePolicy(sizePolicy)
        self.intro_le.setObjectName(_fromUtf8("intro_le"))
        self.gridLayout_3.addWidget(self.intro_le, 6, 0, 1, 4)
        self.cattitle_le = QtGui.QLineEdit(self.groupBox_2)
        self.cattitle_le.setObjectName(_fromUtf8("cattitle_le"))
        self.gridLayout_3.addWidget(self.cattitle_le, 8, 0, 1, 4)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.allowcat_cb, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cattitle_le.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "CSV Генератор", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Файл", None, QtGui.QApplication.UnicodeUTF8))
        self.fname_le.setText(QtGui.QApplication.translate("Dialog", "plugins/csv_import_pro/base.csv", None, QtGui.QApplication.UnicodeUTF8))
        self.selectfile_bp.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Кодировка", None, QtGui.QApplication.UnicodeUTF8))
        self.encoding_cb.setItemText(0, QtGui.QApplication.translate("Dialog", "Автоопределение", None, QtGui.QApplication.UnicodeUTF8))
        self.encoding_cb.setItemText(1, QtGui.QApplication.translate("Dialog", "UTF-8", None, QtGui.QApplication.UnicodeUTF8))
        self.encoding_cb.setItemText(2, QtGui.QApplication.translate("Dialog", "Windows-1251", None, QtGui.QApplication.UnicodeUTF8))
        self.encoding_cb.setItemText(3, QtGui.QApplication.translate("Dialog", "ASCII", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Разделитель полей", None, QtGui.QApplication.UnicodeUTF8))
        self.fielddelim_le.setText(QtGui.QApplication.translate("Dialog", ";", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Разделитель текста", None, QtGui.QApplication.UnicodeUTF8))
        self.textdelim_le.setText(QtGui.QApplication.translate("Dialog", "\"", None, QtGui.QApplication.UnicodeUTF8))
        self.ignorefirst_cb.setText(QtGui.QApplication.translate("Dialog", "Игнорировать первую строку", None, QtGui.QApplication.UnicodeUTF8))
        self.allowcat_cb.setText(QtGui.QApplication.translate("Dialog", "Один столбец - категория", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Dialog", "Словари", None, QtGui.QApplication.UnicodeUTF8))
        self.inwords_cb.setText(QtGui.QApplication.translate("Dialog", "Записывать прописью числа отсутствующие в словаре", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Шаблоны", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Заголовок", None, QtGui.QApplication.UnicodeUTF8))
        self.title_le.setText(QtGui.QApplication.translate("Dialog", "{$1}", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Теги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Текст", None, QtGui.QApplication.UnicodeUTF8))
        self.text_le.setPlainText(QtGui.QApplication.translate("Dialog", "<img src=\"/images/{$3}\" align=\"left\">\n"
"<table>\n"
"<tr><td>Цена({$р.|руб.|рублей}):</td><td>{$2}</td></tr>\n"
"<tr><td>Сезонность:</td><td>{$4}</td></tr>\n"
"<tr><td>Дополнительная информация:</td><td>{$5}</td></tr>\n"
"<tr><td>Индекс максимальной скорости:</td><td>{$6}</td></tr>\n"
"<tr><td>Технология RunFlat:</td><td>{$7}</td></tr>\n"
"<tr><td>Способ герметизации:</td><td>{$8}</td></tr>\n"
"<tr><td>Диаметр:</td><td>{$9}</td></tr>\n"
"<tr><td>Высота профиля:</td><td>{$10}</td></tr>\n"
"<tr><td>Шипы:</td><td>{$11}</td></tr>\n"
"<tr><td>Индекс нагрузки:</td><td>{$12}</td></tr>\n"
"<tr><td>Максимальная нагрузка (на одну шину):</td><td>{$13}</td></tr>\n"
"<tr><td>Тип автомобиля:</td><td>{$14}</td></tr>\n"
"<tr><td>Конструкция:</td><td>{$15}</td></tr>\n"
"<tr><td>Ширина профиля:</td><td>{$16}</td></tr>\n"
"</table>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Dialog", "Вступление", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Dialog", "Категория", None, QtGui.QApplication.UnicodeUTF8))
        self.intro_le.setPlainText(QtGui.QApplication.translate("Dialog", "<img src=\"/images/{$3}\" align=\"left\">{$Стоимость|Цена|Стоимость на текущий момент|Сезонная цена} {$2}({$р.|руб.|рублей}). Диаметры {$шины|шин} {$9} при {$высоте профиля|профиле} {$10}. Наличие шипов: {$11}. {$Шина предназначена для автомобилей|Назначение - автомобиль} типа \"{$14}\".\n"
"", None, QtGui.QApplication.UnicodeUTF8))
        self.cattitle_le.setText(QtGui.QApplication.translate("Dialog", "{$1}", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

