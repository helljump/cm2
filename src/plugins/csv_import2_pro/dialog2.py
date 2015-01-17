# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog2.ui'
#
# Created: Mon Jan 14 14:31:46 2013
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
        Dialog.resize(888, 685)
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
        self.ignorefirst_cb.setChecked(False)
        self.ignorefirst_cb.setObjectName(_fromUtf8("ignorefirst_cb"))
        self.gridLayout.addWidget(self.ignorefirst_cb, 1, 5, 1, 4)
        self.allowcat_cb = QtGui.QCheckBox(self.groupBox)
        self.allowcat_cb.setChecked(False)
        self.allowcat_cb.setObjectName(_fromUtf8("allowcat_cb"))
        self.gridLayout.addWidget(self.allowcat_cb, 1, 9, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)
        self.title_le = QtGui.QLineEdit(self.groupBox_2)
        self.title_le.setObjectName(_fromUtf8("title_le"))
        self.gridLayout_4.addWidget(self.title_le, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_4.addWidget(self.label_6, 0, 2, 1, 1)
        self.tags_le = QtGui.QLineEdit(self.groupBox_2)
        self.tags_le.setText(_fromUtf8(""))
        self.tags_le.setObjectName(_fromUtf8("tags_le"))
        self.gridLayout_4.addWidget(self.tags_le, 0, 3, 1, 1)
        self.splitter = QtGui.QSplitter(self.groupBox_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.frame = QtGui.QFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_3 = QtGui.QGridLayout(self.frame)
        self.gridLayout_3.setMargin(4)
        self.gridLayout_3.setSpacing(3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_7 = QtGui.QLabel(self.frame)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_3.addWidget(self.label_7, 0, 0, 1, 1)
        self.text_le = QtGui.QPlainTextEdit(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.text_le.sizePolicy().hasHeightForWidth())
        self.text_le.setSizePolicy(sizePolicy)
        self.text_le.setObjectName(_fromUtf8("text_le"))
        self.gridLayout_3.addWidget(self.text_le, 1, 0, 1, 1)
        self.frame_2 = QtGui.QFrame(self.splitter)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout_5 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_5.setMargin(4)
        self.gridLayout_5.setSpacing(3)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_8 = QtGui.QLabel(self.frame_2)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_5.addWidget(self.label_8, 0, 0, 1, 1)
        self.intro_le = QtGui.QPlainTextEdit(self.frame_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.intro_le.sizePolicy().hasHeightForWidth())
        self.intro_le.setSizePolicy(sizePolicy)
        self.intro_le.setObjectName(_fromUtf8("intro_le"))
        self.gridLayout_5.addWidget(self.intro_le, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.splitter, 1, 0, 1, 4)
        self.label_9 = QtGui.QLabel(self.groupBox_2)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_4.addWidget(self.label_9, 2, 0, 1, 1)
        self.cattitle_le = QtGui.QLineEdit(self.groupBox_2)
        self.cattitle_le.setObjectName(_fromUtf8("cattitle_le"))
        self.gridLayout_4.addWidget(self.cattitle_le, 3, 0, 1, 4)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.allowcat_cb, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cattitle_le.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Генератор Магазинов 2", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Файл", None, QtGui.QApplication.UnicodeUTF8))
        self.fname_le.setText(QtGui.QApplication.translate("Dialog", "plugins/youtube_pro/base.csv", None, QtGui.QApplication.UnicodeUTF8))
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
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Шаблоны", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Заголовок", None, QtGui.QApplication.UnicodeUTF8))
        self.title_le.setText(QtGui.QApplication.translate("Dialog", "{{ data.1 }} : {{ data.8 }}", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Теги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Dialog", "Текст", None, QtGui.QApplication.UnicodeUTF8))
        self.text_le.setPlainText(QtGui.QApplication.translate("Dialog", "<object width=\"700\" height=\"394\"><param name=\"movie\" value=\"http://www.youtube.com/v/{{ data.0 }}?version=3&amp;hl=ru_RU&amp;rel=0\"></param><param name=\"allowFullScreen\" value=\"true\"></param><param name=\"allowscriptaccess\" value=\"always\"></param><embed src=\"http://www.youtube.com/v/{{ data.0 }}?version=3&amp;hl=ru_RU&amp;rel=0\" type=\"application/x-shockwave-flash\" width=\"700\" height=\"394\" allowscriptaccess=\"always\" allowfullscreen=\"true\"></embed></object>\n"
"<table border=\"0\">\n"
"<tr>\n"
"<td width=\"250\">\n"
"{{ choice([\"Дата публикации\",\"Дата\"]) }}: {{ data.3 }}<br>\n"
"{{ choice([\"Рейтинг\",\"Оценка\"]) }}: {{ data.4 }} {{ choice([\"\",\"баллов\",\"*\",\"звезд\"]) }}\n"
"Длительность:{% set egg = randint(1,2) %}{% if egg==1 -%}{{ data.6 }} секунд{% else -%}{%- set spam = data.6|int -%}{%- set m = spam//60 -%}{%- set s = spam%60 -%}{{ m }}:{{ \"%02i\"|format(s) }}{% endif -%}<br>\n"
"Количество просмотров: {{ data.7 }}\n"
"</td>\n"
"<td>\n"
"<h2>{{ data.1 }}</h2>\n"
"{{ data.2 }}\n"
"</td>\n"
"</tr>\n"
"</table>\n"
"{{ choice([\"Вы хотели узнать\",\"Вы, наверное, всегда хотели узнать\",\"Хотите узнать\",\"А Вы знали\",\"А Вы хотели б узнать\",\"Знаете ли ВЫ\",\"Сегодня многие хотят узнать\",\"В интернете сейчас популярна тема\",\"Хотели бы Вы узнать\",\"Среди пользователей сайта популярна тема\",\"Наши пользователи часто спрашивают\",\"Пользователи сайта часто спрашивают\",\"Наши посетители часто задают вопрос\"]) }} \"{{ data.8 }}\" {{ choice([\":\",\"-\"]) }} {{ choice([\"смотрите\",\"посмотрите\",\"поглядите\",\"мы представляем\",\"мы выложили\",\"мы опубликовали\",\"мы добавили\",\"мы разместили\",\"поэтому мы выложили\",\"сегодня мы разместили\",\"сегодня мы опубликовали\",\"мы предлагаем Вам посмотреть\",\"мы предлагаем изучить\"]) }} {{ choice([\"новый\",\"свежий\",\"интересный\",\"забавный\",\"\",\"\"]) }} {{[choice([\"он лайн\",\"онлайн\",\"он-лайн\",\"online\",\"\"]),choice([\"видео\",\"\"]),\"ролик\"]|shuffle|join(\" \")}} \"{{ data.1 }}\".\n"
"{%- set spam2 = data.4|int -%}\n"
"{%- set m2 = spam2//1 -%}\n"
"В {{choice([\"популярном\",\"интересном\",\"пользующемся популярностью\",\"\"])}} {{choice([\"ролике\",\"видео\",\"онлайн видео\",\"видео онлайн\"])}} с {{ choice([\"рейтингом\",\"оценкой\"]) }} {{ choice([\"более чем\",\"больше чем\"]) }} {{ m2|in_words }} {{ choice([\"балла\",\"звезды\",\"*\"]) }} вы {{ choice([\"узнаете\",\"поймете\"]) }} {{ data.8 }}.\n"
"<h3>Комментарии</h3>\n"
"<ul>\n"
"{% set comments = data[9:] %}\n"
"{% for c in comments|shuffle -%}\n"
"  {% if c %}\n"
"    <li>{{ c|yasyn(\"internal\", 3) }}</li>\n"
"  {% endif %}\n"
"{%- endfor %}\n"
"</ul>\n"
"", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Dialog", "Вступление", None, QtGui.QApplication.UnicodeUTF8))
        self.intro_le.setPlainText(QtGui.QApplication.translate("Dialog", "<img src=\"{{ data.5 }}\" alt=\"{{ data.1 }}\" width=\"245\" height=\"183\"/><br>\n"
"Длительность:{% set egg = randint(1,2) %}{% if egg==1 -%}{{ data.6 }} секунд{% else -%}{%- set spam = data.6|int -%}{%- set m = spam//60 -%}{%- set s = spam%60 -%}{{ m }}:{{ \"%02i\"|format(s) }}{% endif -%} <br>\n"
"Количество просмотров: {{ data.7 }}<br>\n"
"{{ choice([\"Рейтинг\",\"Оценка\"]) }}: {{ data.4 }} {{ choice([\"\",\"баллов\",\"*\",\"звезд\"]) }}\n"
"", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Dialog", "Категория", None, QtGui.QApplication.UnicodeUTF8))
        self.cattitle_le.setText(QtGui.QApplication.translate("Dialog", "{{ data.0 }}", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

