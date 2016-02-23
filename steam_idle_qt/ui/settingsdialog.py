# -*- coding: utf-8 -*-

"""
Module implementing SettingsDialog.
"""
import logging
from PyQt4.QtCore import pyqtSlot, QSettings
from PyQt4.QtGui import QDialog, QDialogButtonBox

from .Ui_settings import Ui_Dialog, _translate
from steam_idle_qt.QSteamWebBrowser import QSteamWebBrowser
from steamweb.steamwebbrowser import IncorrectLoginError

class SettingsDialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        super(SettingsDialog, self).__init__(parent)
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.credentialsOK = False
        self.readSettings()

    @property
    def settings(self):
        return QSettings(QSettings.IniFormat, QSettings.UserScope, 'jayme-github', 'SteamIdle')

    def readSettings(self):
        settings = self.settings
        self.lineEditUsername.setText(settings.value('steam/username', ''))
        self.lineEditPassword.setText(settings.value('steam/password', ''))
        self.checkBoxStorePassword.setChecked(settings.value('steam/storepassword', False, type=bool))
        self.comboBoxAutostart.setCurrentIndex(
            self.comboBoxAutostart.findText(settings.value('autostart', 'None'))
        )
        self.spinBoxMultiIdleThreshold.setValue(settings.value('multiidlethreshold', 2, type=int))
        self.spinBoxMaxRefreshTime.setValue(settings.value('maxrefreshtime', 15, type=int))
        # Check credentials if we know username and password
        self.checkSteamCredentials(lazy=True)

    def writeSettings(self):
        settings = self.settings
        settings.setValue('steam/username', self.lineEditUsername.text())
        if self.checkBoxStorePassword.isChecked():
            # Store password in config
            # FIXME: use keystore
            settings.setValue('steam/password', self.lineEditPassword.text())
        else:
            # Store password in mainwindow variable
            self.parent._steamPassword = self.lineEditPassword.text()
        settings.setValue('steam/storepassword', self.checkBoxStorePassword.isChecked())
        settings.setValue('autostart', self.comboBoxAutostart.currentText())
        settings.setValue('multiidlethreshold', self.spinBoxMultiIdleThreshold.value())
        settings.setValue('maxrefreshtime', self.spinBoxMaxRefreshTime.value())

    def setGreenMsg(self, msg):
        self.labelStatus_2.setStyleSheet('color: green')
        self.logger.debug('setGreenMsg(%s)', msg)
        self.labelStatus_2.setText(msg)

    def setRedMsg(self, msg):
        self.labelStatus_2.setStyleSheet('color: red')
        self.logger.debug('setRedMsg(%s)', msg)
        self.labelStatus_2.setText(msg)

    def setConnectedStatus(self, status):
        if status == True:
            self.setGreenMsg(_translate('Dialog', 'Connected', None))
        else:
            self.setRedMsg(_translate('Dialog', 'Not connected', None))

    def accept(self):
        self.logger.debug('acceppt slot')
        if not self.lineEditUsername.text():
            # hint missing username
            self.lineEditUsername.setStyleSheet('QLineEdit { background-color: #f6989d }')
            return
        self.lineEditUsername.setStyleSheet('')
        if not self.lineEditPassword.text():
            # hint missing password
            self.lineEditPassword.setStyleSheet('QLineEdit { background-color: #f6989d }')
            return
        self.lineEditPassword.setStyleSheet('')

        if self.credentialsOK or self.checkSteamCredentials():
            self.writeSettings()
            super().accept()
        else:
            self.logger.debug('credential check failed...don\'t accept dialog')

    def checkSteamCredentials(self, lazy=False):
        username = self.lineEditUsername.text()
        password = self.lineEditPassword.text()
        self.credentialsOK = False
        if username and password:
            self.logger.info('Try to login with username: "%s"', username)
            swb = QSteamWebBrowser(
                    username=username,
                    password=password,
                    parent=self
            )
            if lazy and swb.logged_in():
                self.logger.info('Looks like we already have a cookie for account "%s"', username)
                self.credentialsOK = True
                self.setGreenMsg(_translate('Dialog', 'Connected (SteamID %s)' % swb.steamid, None))
            else:
                try:
                    steamid = swb.login()
                    if steamid:
                        self.credentialsOK = True
                        self.setGreenMsg(_translate('Dialog', 'Connected (SteamID %s)' % steamid, None))
                except IncorrectLoginError:
                    self.logger.exception('IncorrectLogin')
                    self.setRedMsg(_translate('Dialog', 'Incorrect login', None))
                    self.credentialsOK = False
        else:
            self.setConnectedStatus(self.credentialsOK)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.credentialsOK)
        return self.credentialsOK

    @pyqtSlot()
    def on_lineEditUsername_editingFinished(self):
        if self.lineEditUsername.text():
            self.lineEditUsername.setStyleSheet('')
            #self.checkSteamCredentials()
        else:
            self.lineEditUsername.setStyleSheet('QLineEdit { background-color: #f6989d }')

    @pyqtSlot()
    def on_lineEditPassword_editingFinished(self):
        if self.lineEditPassword.text():
            self.lineEditPassword.setStyleSheet('')
            #self.checkSteamCredentials()
        else:
            self.lineEditPassword.setStyleSheet('QLineEdit { background-color: #f6989d }')

    @pyqtSlot('QString')
    def on_lineEditUsername_textEdited(self, text):
        self.credentialsOK = False
        self.setConnectedStatus(self.credentialsOK)
        if self.lineEditUsername.text() and self.lineEditPassword.text():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    @pyqtSlot('QString')
    def on_lineEditPassword_textEdited(self, text):
        self.credentialsOK = False
        self.setConnectedStatus(self.credentialsOK)
        if self.lineEditUsername.text() and self.lineEditPassword.text():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
