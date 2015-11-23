import logging
from PyQt4.QtCore import pyqtSlot, pyqtSignal, QObject, QTimer, QSettings
from steam_idle_qt.QSteamWebBrowser import QSteamWebBrowser
from steam_idle.page_parser import SteamBadges

DEFAULT_TIMER = 15*60*1000

class QSteamParser(QObject):
    steamDataReady = pyqtSignal(dict)
    timerStart = pyqtSignal(int)
    timerStop = pyqtSignal()
    timer = None

    def __init__(self, username, password, data_path):
        super(QSteamParser, self).__init__()
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))

        # Setup SteamWebBrowser etc.
        self.logger.debug('Init QSteamWebBrowser')
        swb = QSteamWebBrowser(
                username=username,
                password=password,
                parent=self
        )
        self.logger.debug('Using data path: "%s"', data_path)
        self.sbb = SteamBadges(swb, data_path)

    @property
    def settings(self):
        return QSettings(QSettings.IniFormat, QSettings.UserScope, 'jayme-github', 'SteamIdle')

    @pyqtSlot(int)
    def startTimer(self, interval):
        # Interval should never exceed DEFAULT_TIMER
        newInterval = DEFAULT_TIMER if interval > DEFAULT_TIMER else interval
        self.logger.debug('Requested %fmin timer, setting up timer for %fmin',
            interval/1000/60,
            newInterval/1000/60,
        )
        self.stopTimer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateApps)
        self.timer.start(newInterval)
        self.timerStart.emit(newInterval)

    @pyqtSlot()
    def startDefaultTimer(self):
        self.startTimer(DEFAULT_TIMER)

    @pyqtSlot()
    def stopTimer(self):
        if self.timer:
            self.logger.debug('Stopping timer')
            self.timer.stop()
            self.timer = None
            self.timerStop.emit()

    @pyqtSlot()
    def updateApps(self):
        self.logger.info('Updating apps from steam')
        apps = self.sbb.get_apps()
        self.logger.debug('ParseApps: %d apps', len(apps))
        self.steamDataReady.emit(apps)
