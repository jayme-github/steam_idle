import os
import stat
from steamweb import SteamWebBrowser

from PyQt4.QtCore import QObject, QSettings, QDir
from PyQt4.QtGui import QInputDialog, QLineEdit
from .ui.captchadialog import CaptchaDialog

class QSteamWebBrowser(SteamWebBrowser, QObject):
    name = 'SteamIdle'
    def __init__(self, username, password, parent=None):
        self.parent = parent
        QObject.__init__(self, self.parent)
        # Set appdata path, this will end up in something like ~/.config/jayme-github/SteamIdle/
        self._appdata_path = os.path.join(
            os.path.dirname(QDir.toNativeSeparators(self.settings.fileName())),
            'SteamIdle'
        )
        for p in (os.path.dirname(QDir.toNativeSeparators(self.settings.fileName())), self._appdata_path):
            if not os.path.isdir(p):
                os.mkdir(p, stat.S_IRWXU)
        self.logger.debug('_appdata_path: "%s"', self._appdata_path)
        SteamWebBrowser.__init__(self, username=username, password=password)

    @property
    def settings(self):
        return QSettings(QSettings.IniFormat, QSettings.UserScope, 'jayme-github', 'SteamIdle')

    def _handle_captcha(self, captcha_data, message=''):
        ''' Called when a captcha must be solved
        Writes the image to a temporary file and asks the user to enter the code.

        Args:
            captcha_data: Bytestring of the PNG captcha image.
            message: Optional. A message from Steam service.

        Returns:
            A string containing the solved captcha code.
        '''
        self.logger.debug('_handle_captcha(%s)', message)
        captchaDialog = CaptchaDialog(image_data=captcha_data, parent=self.parent)
        captchaDialog.exec_()
        return captchaDialog.lineEditCaptchaText.text()

    def _handle_emailauth(self, maildomain='', message=''):
        ''' Called when SteamGuard requires authentication via e-mail.
        Asks the user to enter the code.

        Args:
            maildomain: Optional. The mail domain of the e-mail address the SteamGuard
                code is send to.
            message: Optional. A message from Steam service.

        Returns:
            A string containing the code.
        '''
        self.logger.debug('_handle_emailauth(%s)', message)
        emailauth, ok = QInputDialog.getText(
            self.parent,
            self.trUtf8('SteamGuard'),
            self.trUtf8('SteamGuard requires email authentication.<br/><br/>Please enter the code sent to your mail account at "%s":' % maildomain),
            QLineEdit.Normal)
        if ok:
            emailauth.upper()
            return emailauth

    def _handle_twofactor(self, message=''):
        ''' Called when SteamGuard requires two-factor authentication..
        Asks the user to enter the code.

        Args:
            message: Optional. A message from Steam service.

        Returns:
            A string containing the code.
        '''
        self.logger.debug('_handle_twofactor(%s)', message)
        twofactorcode, ok = QInputDialog.getText(
            self.parent,
            self.trUtf8('SteamGuard'),
            self.trUtf8('SteamGuard requires mobile authentication.<br/><br/>Please enter the code sent to your phone:'),
            QLineEdit.Normal)
        if ok:
            twofactorcode.upper()
            return twofactorcode
