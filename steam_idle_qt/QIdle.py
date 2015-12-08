import logging
from datetime import datetime, timedelta
from time import sleep
from steam_idle.page_parser import App
from steam_idle.idle import IdleChild, strfsec, calc_delay
from PyQt4.QtCore import pyqtSlot, pyqtSignal, QObject

class BaseIdle(QObject):
    finished = pyqtSignal()
    appDone = pyqtSignal(App)
    statusUpdate = pyqtSignal(str)
    updateSteamParserTimer = pyqtSignal(int)

    def __init__(self):
        super(BaseIdle, self).__init__()
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))

class Idle(BaseIdle):
    idleChild = None
    app = None

    def _idle(self):
        if self.app.remainingDrops > 0:
            delay = calc_delay(self.app.remainingDrops)
            until = datetime.now() + timedelta(seconds=delay)

            self.logger.info('_idle called: %s has %d remaining drops: Ideling for %s (\'till %s)',
                    self.app,
                    self.app.remainingDrops,
                    strfsec(delay),
                    until.strftime('%c')
            )
            # Setup and start idleChild if not done already
            if self.idleChild == None:
                self.logger.debug('setup a new child')
                self.idleChild = IdleChild(self.app)
                self.idleChild.start()
            else:
                self.logger.debug('child is still running: %s', self.idleChild)
            # idleChild is setup or still running

            # Setup QStremParser timer with new delay*1000
            self.updateSteamParserTimer.emit(delay*1000)
            # Send status update
            self.statusUpdate.emit('Ideling "{}" for {} (\'till {})'.format(
                self.app.name,
                strfsec(delay),
                until.strftime('%c'),
            ))
        else:
            self.logger.info('No drops left, stopping idle and emitting appDone signal')
            self._stopIdle()
            # Emit appDone signal, main thead should send next app via doStartIdle or stop via doStopIdle
            self.appDone.emit(self.app)

    def _stopIdle(self):
        ''' Stops idleChild
            does not emit any signals or trigger further action
        '''
        self.logger.debug('_stopIdle called')
        if self.idleChild != None:
            self.logger.debug('Terminating child')
            self.idleChild.terminate()
            self.idleChild.join()
            self.idleChild = None
            self.logger.debug('Child terminated')

    @pyqtSlot(App)
    def doStartIdle(self, app):
        self.logger.debug('doStartIdle(%s)', app)
        if self.app == None or app.appid != self.app.appid:
            # New/first app, stopIdle first
            self._stopIdle() # this won't do anything on first run
            self.app = app
        # Same app, just continue
        self._idle()

    @pyqtSlot(dict)
    def on_steamDataReady(self, apps):
        ''' Called whenever new steam data arrives '''
        if self.app is None:
            # No idle child running, ignore signal
            return
        self.logger.debug('on_steamDataReady with %d apps as parameter', len(apps))
        newapp = apps.get(self.app.appid)
        if newapp:
            self.logger.debug('updated app: OLD: %s', self.app)
            self.logger.debug('updated app: NEW: %s', newapp)
            self.app = newapp
            self._idle()
        else:
            self.logger.error('appid %d not found in badged', self.app.appid)
            # TODO: Maybe better to raise error to main thread than just continue with next app?
            self._stopIdle()
            self.appDone.emit(self.app)

    @pyqtSlot()
    def doStopIdle(self):
        ''' Called when idle is forcefully stopped (on stopAction, nextAction or app quit for example)
            emits finish signal that should be connected to thread.quit
        '''
        self.logger.debug('doStopIdle called')
        self._stopIdle()
        self.logger.debug('sending finished signal')
        self.finished.emit()


class MultiIdle(BaseIdle):
    allDone = pyqtSignal()
    # Format {<appid>: (<IdleChild instance>, endtime), ...}
    idleChilds = {}

    @pyqtSlot(list)
    def doStartIdle(self, apps):
        self.logger.info('MultiIdle.multiIdle(%s)', apps)
        minimumDelay = None
        for app in apps:
            delay = int((2.0 - app.playTime) * 60 * 60)
            if delay <= 0 or app.remainingDrops == 0:
                # App has > 2h playtime
                continue
            # Human readable time
            endtime = (datetime.now() + timedelta(seconds=delay))
            # How long 'till the next app reaches 2h playtime?
            if minimumDelay is None or delay < minimumDelay:
                minimumDelay = delay

            self.statusUpdate.emit('Launching Idle child {} of {}'.format(
                len(self.idleChilds) + 1, len(apps)
            ))

            p = IdleChild(app)
            # Start the (idle) process
            p.start()
            self.idleChilds[app.appid] = (p, endtime)
            self.logger.debug('doStartIdle: started %s', p)
            if len(self.idleChilds) < len(apps):
                # Steam client will crash if childs spawn too fast
                sleep(0.25)

        # All childs spawned
        self.statusUpdate.emit('Multi-Idling {} apps'.format(len(self.idleChilds)))

        # Start SteamParser timer with the minimum delay
        self.updateSteamParserTimer.emit(minimumDelay*1000)

    @pyqtSlot(dict)
    def on_steamDataReady(self, apps):
        ''' Called whenever new steam data arrives '''
        if len(self.idleChilds) < 1:
            # No idle child running, ignore signal
            return
        self.logger.debug('on_steamDataReady with %d apps as parameter', len(apps))
        for appid in list(self.idleChilds):
            newapp = apps.get(appid)
            if newapp:
                self.logger.debug('updated app: OLD: %s', self.idleChilds[appid][0].app)
                self.logger.debug('updated app: NEW: %s', newapp)
                if newapp.playTime >= 2.0 or newapp.remainingDrops < 1:
                    self.logger.debug('%s has reached 2h playtime or has no drops remaining', newapp)
                    # Stop this child
                    self._stopChild(appid)
                    self.appDone.emit(newapp)
            else:
                self.logger.error('appid %d not found in badged', appid)
                # TODO: Maybe better to raise error to main thread than just continue with next app?
                self._stopChild(appid)
                self.appDone.emit(newapp)

    @pyqtSlot()
    def doStopIdle(self):
        self.logger.debug('doStopIdle called')
        for appid, _ in sorted(self.idleChilds.items(), key=lambda x: x[1][1], reverse=True):
            self._stopChild(appid)
        self.finished.emit()

    def _stopChild(self, appid):
        p = self.idleChilds.get(appid)[0]
        self.logger.debug('MultiIdle._stopChild(%s)', p)
        p.terminate()
        self.logger.debug('MultiIdle._stopChild(%s) child terminated', p)
        p.join()
        self.logger.debug('MultiIdle._stopChild(%s) joined thead', p)
        del self.idleChilds[appid]
        self.logger.debug('MultiIdle._stopChild(%s) DONE', p)
        self.statusUpdate.emit('Multi-Idling {} apps'.format(len(self.idleChilds)))
