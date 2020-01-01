# -*- coding: utf-8 -*-
# Copyright 2019-2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Support: https://github.com/lovac42/Blitzkrieg


# Form implementation generated from reading ui file 'finder.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from anki.lang import _
# from PyQt4 import QtCore, QtGui as QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(410, 80)
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(-20, 0, 421, 81))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.btn_exactly = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.btn_exactly.setObjectName("btn_exactly")
        self.gridLayout.addWidget(self.btn_exactly, 2, 2, 1, 1)
        self.btn_endswith = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.btn_endswith.setObjectName("btn_endswith")
        self.gridLayout.addWidget(self.btn_endswith, 2, 3, 1, 1)
        self.btn_startswith = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.btn_startswith.setObjectName("btn_startswith")
        self.gridLayout.addWidget(self.btn_startswith, 1, 3, 1, 1)
        self.btn_contains = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.btn_contains.setChecked(True)
        self.btn_contains.setObjectName("btn_contains")
        self.gridLayout.addWidget(self.btn_contains, 1, 2, 1, 1)
        self.cb_case = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.cb_case.setEnabled(True)
        self.cb_case.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.cb_case.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.cb_case.setObjectName("cb_case")
        self.gridLayout.addWidget(self.cb_case, 1, 1, 1, 1)
        self.input = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.input.setObjectName("input")
        self.gridLayout.addWidget(self.input, 0, 1, 1, 4)
        self.btn_find = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_find.setObjectName("btn_find")
        self.gridLayout.addWidget(self.btn_find, 2, 4, 1, 1)
        self.btn_regexp = QtWidgets.QRadioButton(self.gridLayoutWidget)
        self.btn_regexp.setObjectName("btn_regexp")
        self.gridLayout.addWidget(self.btn_regexp, 2, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.btn_find.clicked.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_("Sidebar Item Finder"))
        self.label.setText(_("Search:  "))
        self.btn_exactly.setText(_("Exactly"))
        self.btn_endswith.setText(_("EndsWith"))
        self.btn_startswith.setText(_("StartsWith"))
        self.btn_contains.setText(_("Contains"))
        self.cb_case.setText(_("Case Sensitive"))
        self.btn_find.setText(_("Find"))
        self.btn_regexp.setText(_("RegExp"))


