import logging
from datetime import datetime, timedelta
from math import ceil
from time import sleep
from steam_idle.page_parser import App
from steam_idle.idle import IdleChild, strfsec, calc_delay
from PyQt4.QtCore import pyqtSlot, pyqtSignal, QObject, QTimer

class BaseIdle(QObject):
    finished = pyqtSignal()
    appDone = pyqtSignal(App)
    statusUpdate = pyqtSignal(str)
    idleTimer = None

    def __init__(self):
        super(BaseIdle, self).__init__()
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))

    def _stopTimer(self):
        if self.idleTimer:
            self.logger.debug('Stopping timer')
            self.idleTimer.stop()
            self.idleTimer = None

class Idle(BaseIdle):
    steamDataReady = pyqtSignal(dict)
    idleChild = None
    app = None

    def __init__(self, sbb):
        super(Idle, self).__init__()
        self.sbb = sbb

    def _idle(self):
        if self.app.remainingDrops > 0:
            delay = calc_delay(self.app.remainingDrops, self.app.playTime)
            until = datetime.now() + timedelta(seconds=delay)
            self.logger.info('_idle called: %s has %d remaining drops: Ideling for %s (\'till %s)' % (
                    self.app,
                    self.app.remainingDrops,
                    strfsec(delay),
                    until.strftime('%c')
            ))
            # Setup and start idleChild if not done already
            if self.idleChild == None:
                self.logger.debug('setup a new child')
                self.idleChild = IdleChild(self.app)
                self.idleChild.start()
            else:
                self.logger.debug('child is still running: %s' %self.idleChild)
            # idleChild is setup or still running

            self.statusUpdate.emit('Ideling "{}" for {} (\'till {})'.format(
                self.app.name,
                strfsec(delay),
                until.strftime('%c'),
            ))
            self._stopTimer() # Will stop the timer if it exists
            self.idleTimer = QTimer()
            self.idleTimer.timeout.connect(self.doAskForUpdate)
            self.idleTimer.setSingleShot(True)
            self.idleTimer.start(delay*1000)
            self.logger.debug('_idle: timer setup completed...')
        else:
            self.logger.info('No drops left, stopping idle and emitting appDone signal')
            self._stopIdle()
            # Emit appDone signal, main thead should send next app via doStartIdle or stop via doStopIdle
            self.appDone.emit(self.app)

    def _stopIdle(self):
        ''' Stops idleChild and idleTimer
            does not emit any signals or trigger further action
        '''
        self.logger.debug('_stopIdle called')
        if self.idleChild != None:
            self.logger.debug('Terminating child')
            self.idleChild.terminate()
            self.idleChild.join()
            self.idleChild = None
            self.logger.debug('Child terminated')
        self._stopTimer()

    @pyqtSlot(App)
    def doStartIdle(self, app):
        self.logger.debug('doStartIdle(%s)' % app)
        if self.app == None or app.appid != self.app.appid:
            # New/first app, stopIdle first
            self._stopIdle() # this won't do anything on first run
            self.app = app
        # Same app, just continue whith the next timer
        self._idle()

    @pyqtSlot()
    def doAskForUpdate(self):
        apps = self.sbb.get_apps() # Update data from steam (it's okay to block this thread)
        newapp = apps.get(self.app.appid)
        if newapp:
            self.logger.debug('updated app: OLD: %s NEW: %s' %(self.app, newapp))
            self.steamDataReady.emit(apps) #Send new steam data to main thread
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
    idleChilds = {}

    def _stopChild(self, p):
        self.logger.debug('MultiIdle._stopChild(%s)'%p)
        p.terminate()
        self.logger.debug('MultiIdle._stopChild(%s) child terminated'%p)
        p.join()
        self.logger.debug('MultiIdle._stopChild(%s) joined thead'%p)
        del self.idleChilds[p]
        self.logger.debug('MultiIdle._stopChild(%s) DONE'%p)

    @pyqtSlot(list)
    def doStartIdle(self, apps):
        self.logger.info('MultiIdle.multiIdle(%s)' %apps)
        for app in apps:
            delay = int((2.0 - app.playTime) * 60 * 60)
            if delay <= 0:
                continue
            endtime = (datetime.now() + timedelta(seconds=delay))
            self.statusUpdate.emit('Launching IdleChild {} of {}'.format(len(self.idleChilds) + 1, len(apps)))
            p = IdleChild(app)
            # Start the (idle) process
            p.start()
            self.idleChilds[p] = endtime
            self.logger.debug('doStartIdle: started %s' %p)
            if len(self.idleChilds) < len(apps):
                # Steam client will crash if childs spawn too fast
                sleep(0.25)
        self._idle()

    @pyqtSlot()
    def _idle(self):
        self.logger.info('MultiIdle._idle: Running with %d childs' % len(self.idleChilds))
        # Now wait for the idleChilds to finish, idleChilds sorted by endtime
        try:
            p, endtime = sorted(self.idleChilds.items(), key=lambda x: x[1])[0]
        except IndexError:
            # No childs left, all done
            self._stopTimer()
            self.allDone.emit()
            self.finished.emit()
        else:
            self.statusUpdate.emit('Multi-Idle {} games, next update at {}'.format(
                len(self.idleChilds),
                endtime.strftime('%c'),
            ))

            now = datetime.now()
            diff = int(ceil((endtime - now).total_seconds()))
            if endtime < now:
                self.logger.debug(p, 'endtime (%s) is in the past, shutting down' % (endtime,))
                self.appDone.emit(p.app)
                self._stopChild(p)
                self._idle()
            elif diff <= 0:
                self.logger.debug(p, 'diff (%s) is below 0, shutting down' % (diff,))
                self.appDone.emit(p.app)
                self._stopChild(p)
                self._idle()
            else:
                self.logger.debug('Sleeping for %s till %s' %(
                    strfsec(diff),
                    (now + timedelta(seconds=diff)).strftime('%c')
                ))
                self._stopTimer() # Will stop the timer if it exists
                self.idleTimer = QTimer()
                self.idleTimer.timeout.connect(self._idle)
                self.idleTimer.setSingleShot(True)
                self.idleTimer.start(diff*1000)

    @pyqtSlot()
    def doStopIdle(self):
        self.logger.debug('doStopIdle called')
        for p, _ in sorted(self.idleChilds.items(), key=lambda x: x[1], reverse=True):
            self._stopChild(p)
        self._stopTimer()
        self.finished.emit()
