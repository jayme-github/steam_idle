# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'steam_idle_qt/ui/settings.ui'
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
        self.groupBoxSteamAccount = QtGui.QGroupBox(Dialog)
        self.groupBoxSteamAccount.setObjectName(_fromUtf8("groupBoxSteamAccount"))
        self.formLayout = QtGui.QFormLayout(self.groupBoxSteamAccount)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.labelUsername = QtGui.QLabel(self.groupBoxSteamAccount)
        self.labelUsername.setObjectName(_fromUtf8("labelUsername"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.labelUsername)
        self.lineEditUsername = QtGui.QLineEdit(self.groupBoxSteamAccount)
        self.lineEditUsername.setObjectName(_fromUtf8("lineEditUsername"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEditUsername)
        self.labelPassword = QtGui.QLabel(self.groupBoxSteamAccount)
        self.labelPassword.setObjectName(_fromUtf8("labelPassword"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.labelPassword)
        self.lineEditPassword = QtGui.QLineEdit(self.groupBoxSteamAccount)
        self.lineEditPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditPassword.setObjectName(_fromUtf8("lineEditPassword"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEditPassword)
        self.labelStatus_2 = QtGui.QLabel(self.groupBoxSteamAccount)
        self.labelStatus_2.setStyleSheet(_fromUtf8("color: red"))
        self.labelStatus_2.setObjectName(_fromUtf8("labelStatus_2"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.labelStatus_2)
        self.labelStatus = QtGui.QLabel(self.groupBoxSteamAccount)
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.labelStatus)
        self.checkBoxStorePassword = QtGui.QCheckBox(self.groupBoxSteamAccount)
        self.checkBoxStorePassword.setObjectName(_fromUtf8("checkBoxStorePassword"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.checkBoxStorePassword)
        self.verticalLayout.addWidget(self.groupBoxSteamAccount)
        self.groupBoxSteamIdle = QtGui.QGroupBox(Dialog)
        self.groupBoxSteamIdle.setObjectName(_fromUtf8("groupBoxSteamIdle"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBoxSteamIdle)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.labelAutostart = QtGui.QLabel(self.groupBoxSteamIdle)
        self.labelAutostart.setObjectName(_fromUtf8("labelAutostart"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.labelAutostart)
        self.comboBoxAutostart = QtGui.QComboBox(self.groupBoxSteamIdle)
        self.comboBoxAutostart.setObjectName(_fromUtf8("comboBoxAutostart"))
        self.comboBoxAutostart.addItem(_fromUtf8(""))
        self.comboBoxAutostart.setItemText(0, _fromUtf8("None"))
        self.comboBoxAutostart.addItem(_fromUtf8(""))
        self.comboBoxAutostart.addItem(_fromUtf8(""))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.comboBoxAutostart)
        self.labelMultiIdleThreshold = QtGui.QLabel(self.groupBoxSteamIdle)
        self.labelMultiIdleThreshold.setObjectName(_fromUtf8("labelMultiIdleThreshold"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.labelMultiIdleThreshold)
        self.spinBoxMultiIdleThreshold = QtGui.QSpinBox(self.groupBoxSteamIdle)
        self.spinBoxMultiIdleThreshold.setMinimum(2)
        self.spinBoxMultiIdleThreshold.setMaximum(99999999)
        self.spinBoxMultiIdleThreshold.setProperty("value", 2)
        self.spinBoxMultiIdleThreshold.setObjectName(_fromUtf8("spinBoxMultiIdleThreshold"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.spinBoxMultiIdleThreshold)
        self.verticalLayout.addWidget(self.groupBoxSteamIdle)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.labelUsername.setBuddy(self.lineEditUsername)
        self.labelPassword.setBuddy(self.lineEditPassword)
        self.labelAutostart.setBuddy(self.comboBoxAutostart)

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
        self.groupBoxSteamAccount.setTitle(_translate("Dialog", "Steam Account", None))
        self.labelUsername.setText(_translate("Dialog", "Username:", None))
        self.labelPassword.setText(_translate("Dialog", "Password:", None))
        self.labelStatus_2.setText(_translate("Dialog", "Not connected", None))
        self.labelStatus.setText(_translate("Dialog", "Status:", None))
        self.checkBoxStorePassword.setText(_translate("Dialog", "Store password", None))
        self.groupBoxSteamIdle.setTitle(_translate("Dialog", "Steam Idle", None))
        self.labelAutostart.setText(_translate("Dialog", "Idle mode to start at launch:", None))
        self.comboBoxAutostart.setToolTip(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">None</span></p><p>No idle auto start.<br/></p><p><span style=\" font-weight:600;\">Idle</span></p><p>Start sequential Idle of all games.<br/></p><p><span style=\" font-weight:600;\">Multi-Idle</span></p><p>Start to Multi-Idle all games in refund period (playtime under 2 hours) in parallel at program launch. If the number of games is below &quot;Multi-Idle threshold&quot;, normal (sequential) Idle is started instead.</p></body></html>", None))
        self.comboBoxAutostart.setItemText(1, _translate("Dialog", "Idle", None))
        self.comboBoxAutostart.setItemText(2, _translate("Dialog", "Multi-Idle", None))
        self.labelMultiIdleThreshold.setToolTip(_translate("Dialog", "Multi-Idle will not be startet if there are not at least %d games within the refund period.", None))
        self.labelMultiIdleThreshold.setText(_translate("Dialog", "Auto Multi-Idle threshold:", None))
        self.spinBoxMultiIdleThreshold.setToolTip(_translate("Dialog", "Multi-Idle will not be startet if there are not at least %d games within the refund period.", None))

