import logging
from PyQt4.QtCore import pyqtSlot, pyqtSignal, QObject, QTimer, QSettings
from steam_idle_qt.QSteamWebBrowser import QSteamWebBrowser
from steam_idle.page_parser import SteamBadges

MAX_TIMER = 15*60*1000

class QSteamParser(QObject):
    steamDataReady = pyqtSignal(dict)
    timerStart = pyqtSignal(int)
    timerStop = pyqtSignal()
    timerTimeout = pyqtSignal(int)
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
        # Interval should never exceed MAX_TIMER
        newInterval = MAX_TIMER if interval > MAX_TIMER else interval
        self.logger.debug('Requested %dmsec timer, setting up timer for %dmsec',
            interval,
            newInterval,
        )
        self.stopTimer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_timeout)
        self.timer.start(newInterval)
        self.timerStart.emit(newInterval)

    @pyqtSlot()
    def startDefaultTimer(self):
        self.startTimer(MAX_TIMER)

    @pyqtSlot()
    def stopTimer(self):
        if self.timer:
            self.logger.debug('Stopping timer')
            self.timer.stop()
            self.timer = None
            self.timerStop.emit()

    @pyqtSlot()
    def on_timer_timeout(self):
        self.logger.debug(self.timer.interval())
        self.timerTimeout.emit(self.timer.interval())
        self.updateApps()

    @pyqtSlot()
    def updateApps(self):
        self.logger.info('Updating apps from steam')
        apps = self.sbb.get_apps()
        self.logger.debug('ParseApps: %d apps', len(apps))
        self.steamDataReady.emit(apps)
