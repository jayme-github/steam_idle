# -*- coding: utf-8 -*-

"""
Module implementing SettingsDialog.
"""
import logging
from PyQt4.QtCore import pyqtSlot, QSettings
from PyQt4.QtGui import QDialog

from .Ui_settings import Ui_Dialog, _translate

class SettingsDialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))
        self.setupUi(self)
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

    def writeSettings(self):
        settings = self.settings
        settings.setValue('steam/username', self.lineEditUsername.text())
        if self.checkBoxStorePassword.isChecked():
            settings.setValue('steam/password', self.lineEditPassword.text())
        settings.setValue('steam/storepassword', self.checkBoxStorePassword.isChecked())
        settings.setValue('autostart', self.comboBoxAutostart.currentText())

    def setConnectedStatus(self, status):
        if status == True:
            self.labelStatus.setStyleSheet('color: green')
            self.labelStatus.setText(_translate('Dialog', 'Connected', None))
        else:
            self.labelStatus.setStyleSheet('color: red')
            self.labelStatus.setText(_translate('Dialog', 'Not connected', None))

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

        if self.checkSteamCredentials():
            self.writeSettings()
            super().accept()
#
#    @pyqtSlot()
#    def on_buttonBox_accepted(self):
#        pass

#    @pyqtSlot()
#    def on_buttonBox_rejected(self):
#        """
#        Slot documentation goes here.
#        """
#        # TODO: not implemented yet
#        raise NotImplementedError

    def checkSteamCredentials(self):
        if self.lineEditUsername.text() and self.lineEditPassword.text():
            self.logger.info('Try to connect to steam')
            # TODO: implement credential check
            self.setConnectedStatus(True)
            return True
        self.setConnectedStatus(False)
        return False

    @pyqtSlot()
    def on_lineEditUsername_lostFocus(self):
        if self.lineEditUsername.text():
            self.lineEditUsername.setStyleSheet('')
            self.checkSteamCredentials()
        else:
            self.lineEditUsername.setStyleSheet('QLineEdit { background-color: #f6989d }')

    @pyqtSlot()
    def on_lineEditPassword_lostFocus(self):
        if self.lineEditPassword.text():
            self.lineEditPassword.setStyleSheet('')
            self.checkSteamCredentials()
        else:
            self.lineEditPassword.setStyleSheet('QLineEdit { background-color: #f6989d }')


