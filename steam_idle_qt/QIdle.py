from datetime import datetime, timedelta
from math import ceil
from time import sleep
from steam_idle.page_parser import App, parse_apps_to_idle
from steam_idle.idle import IdleChild, strfsec, calc_delay
from PyQt4.QtCore import pyqtSlot, pyqtSignal, QObject, QTimer

class BaseIdle(QObject):
    finished = pyqtSignal()
    idleTimer = None

    def _stopTimer(self):
        print('_stopTimer called')
        if self.idleTimer:
            print('Stopping timer')
            self.idleTimer.stop()
            self.idleTimer = None

class Idle(BaseIdle):
    appDone = pyqtSignal(App)
    statusUpdate = pyqtSignal(App, int, datetime)
    steamDataReady = pyqtSignal(dict)
    idleChild = None
    app = None

    def _idle(self):
        if self.app.remainingDrops > 0:
            delay = calc_delay(self.app.remainingDrops, self.app.playTime)
            until = datetime.now() + timedelta(seconds=delay)
            print('_idle called: %s has %d remaining drops: Ideling for %s (\'till %s)' % (
                    self.app,
                    self.app.remainingDrops,
                    strfsec(delay),
                    until.strftime('%c')
            ))
            # Setup and start idleChild if not done already
            if self.idleChild == None:
                print('setup a new child')
                self.idleChild = IdleChild(self.app)
                self.idleChild.start()
            else:
                print('child is still running:', self.idleChild)
            # idleChild is setup or still running

            self.statusUpdate.emit(self.app, delay, until)
            self._stopTimer() # Will stop the timer if it exists
            self.idleTimer = QTimer()
            self.idleTimer.timeout.connect(self.doAskForUpdate)
            self.idleTimer.setSingleShot(True)
            self.idleTimer.start(delay*1000)
            print('_idle: timer setup completed...')
        else:
            print('No drops left, stopping idle and emitting appDone signal')
            self._stopIdle()
            # Emit appDone signal, main thead should send next app via doStartIdle or stop via doStopIdle
            self.appDone.emit(self.app)

    def _stopIdle(self):
        ''' Stops idleChild and idleTimer
            does not emit any signals or trigger further action
        '''
        print('_stopIdle called')
        if self.idleChild != None:
            print('Shutting down child')
            self.idleChild.shutdown()
            self.idleChild.join()
            self.idleChild = None
            print('Child shut down')
        self._stopTimer()

    @pyqtSlot(App)
    def doStartIdle(self, app):
        print('doStartIdle(%s)' % app)
        if self.app == None or app.appid != self.app.appid:
            # New/first app, stopIdle first
            self._stopIdle() # this won't do anything on first run
            self.app = app
        # Same app, just continue whith the next timer
        self._idle()

    @pyqtSlot()
    def doAskForUpdate(self):
        apps = parse_apps_to_idle() # Update data from steam (it's okay to block this thread)
        newapp = apps.get(self.app.appid)
        print('updated app: OLD:', self.app, ' NEW:', newapp)
        self.steamDataReady.emit(apps) #Send new steam data to main thread
        self.app = newapp
        self._idle()

    @pyqtSlot()
    def doStopIdle(self):
        ''' Called when idle is forcefully stopped (on stopAction, nextAction or app quit for example)
            emits finish signal that should be connected to thread.quit
        '''
        print('doStopIdle called')
        self._stopIdle()
        print('sending finished signal')
        self.finished.emit() #FIXME: finished signal never reaches the main thread
        print('i should be gone now')

class MultiIdle(BaseIdle):
    statusUpdate = pyqtSignal(int, datetime) # int: number of childs, datetime: end time of next child
    idleChilds = {}

    def _stopChild(self, p):
        p.shutdown()
        p.join()
        del self.idleChilds[p]

    @pyqtSlot(list)
    def doStartMultiIdle(self, apps):
        print('MultiIdle.multiIdle(%s)' %apps)
        for app in apps:
            delay = int((2.0 - app.playTime) * 60 * 60)
            if delay <= 0:
                continue
            endtime = (datetime.now() + timedelta(seconds=delay))
            p = IdleChild(app)
            # Start the (idle) process
            p.start()
            self.idleChilds[p] = endtime
        self._idle()

    @pyqtSlot()
    def _idle(self):
        print('MultiIdle.multiIdle: Running with %d childs' % len(self.idleChilds))
        # Now wait for the idleChilds to finish, idleChilds sorted by endtime
        try:
            p, endtime = sorted(self.idleChilds.items(), key=lambda x: x[1])[0]
        except IndexError:
            # No childs left, all done
            self.finished.emit()
        else:
            self.statusUpdate(len(self.idleChilds), endtime)

            now = datetime.now()
            if endtime < now:
                print(p, 'endtime (%s) is in the past, shutting down' % (endtime,))
                self._stopChild(p)
            diff = int(ceil((endtime - now).total_seconds()))
            if diff <= 0:
                print(p, 'diff (%s) is below 0, shutting down' % (diff,))
                self._stopChild(p)
            print('Sleeping for %s till %s' %(
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
        for p in list(self.idleChilds.keys()):
            self._stopChild(p)
        self.finished.emit()
