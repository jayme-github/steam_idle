# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
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
        Dialog.resize(400, 300)
        Dialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.lineEditUsername = QtGui.QLineEdit(self.groupBox)
        self.lineEditUsername.setObjectName(_fromUtf8("lineEditUsername"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEditUsername)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.lineEditPassword = QtGui.QLineEdit(self.groupBox)
        self.lineEditPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditPassword.setObjectName(_fromUtf8("lineEditPassword"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEditPassword)
        self.labelStatus = QtGui.QLabel(self.groupBox)
        self.labelStatus.setStyleSheet(_fromUtf8("color: red"))
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.labelStatus)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.checkBoxStorePassword = QtGui.QCheckBox(self.groupBox)
        self.checkBoxStorePassword.setObjectName(_fromUtf8("checkBoxStorePassword"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.checkBoxStorePassword)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.comboBoxAutostart = QtGui.QComboBox(self.groupBox_2)
        self.comboBoxAutostart.setObjectName(_fromUtf8("comboBoxAutostart"))
        self.comboBoxAutostart.addItem(_fromUtf8(""))
        self.comboBoxAutostart.setItemText(0, _fromUtf8("None"))
        self.comboBoxAutostart.addItem(_fromUtf8(""))
        self.comboBoxAutostart.addItem(_fromUtf8(""))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.comboBoxAutostart)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.lineEditUsername)
        self.label_2.setBuddy(self.lineEditPassword)
        self.label_3.setBuddy(self.comboBoxAutostart)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.lineEditUsername, self.lineEditPassword)
        Dialog.setTabOrder(self.lineEditPassword, self.checkBoxStorePassword)
        Dialog.setTabOrder(self.checkBoxStorePassword, self.comboBoxAutostart)
        Dialog.setTabOrder(self.comboBoxAutostart, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Settings", None))
        self.groupBox.setTitle(_translate("Dialog", "Steam Account", None))
        self.label.setText(_translate("Dialog", "Username:", None))
        self.label_2.setText(_translate("Dialog", "Password:", None))
        self.labelStatus.setText(_translate("Dialog", "Not connected", None))
        self.label_4.setText(_translate("Dialog", "Status:", None))
        self.checkBoxStorePassword.setText(_translate("Dialog", "Store password", None))
        self.groupBox_2.setTitle(_translate("Dialog", "Steam Idle", None))
        self.label_3.setText(_translate("Dialog", "Idle mode to start at launch:", None))
        self.comboBoxAutostart.setItemText(1, _translate("Dialog", "Idle", None))
        self.comboBoxAutostart.setItemText(2, _translate("Dialog", "Multi Idle", None))

