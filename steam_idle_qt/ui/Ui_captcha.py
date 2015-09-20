# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'captcha.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(214, 121)
        Dialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.labelCaptchaImage = QtGui.QLabel(Dialog)
        self.labelCaptchaImage.setMinimumSize(QtCore.QSize(206, 40))
        self.labelCaptchaImage.setBaseSize(QtCore.QSize(206, 40))
        self.labelCaptchaImage.setText(_fromUtf8(""))
        self.labelCaptchaImage.setObjectName(_fromUtf8("labelCaptchaImage"))
        self.verticalLayout.addWidget(self.labelCaptchaImage)
        self.lineEditCaptchaText = QtGui.QLineEdit(Dialog)
        self.lineEditCaptchaText.setObjectName(_fromUtf8("lineEditCaptchaText"))
        self.verticalLayout.addWidget(self.lineEditCaptchaText)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "SteamGuard", None))
        self.label.setText(_translate("Dialog", "Please enter thre code below:", None))

