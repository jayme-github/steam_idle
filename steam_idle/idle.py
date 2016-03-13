import sys
import os
import multiprocessing
import setproctitle
from datetime import timedelta
from time import sleep
from steam_idle import steam_api

strfsec = lambda seconds: str(timedelta(seconds=seconds))
def r_sleep(sec):
    ''' Sleep sec seconds and return seconds slept '''
    sleep(sec)
    return sec

class IdleChild(multiprocessing.Process):
    def __init__(self, app):
        super(IdleChild, self).__init__()
        self.app = app
        self.name += '-[%s]' % self.app.name.encode('utf-8') if self.app.name else str(self.app.appid)

    def run(self):
        setproctitle.setproctitle(self.name)
        os.environ['SteamAppId'] = str(self.app.appid)
        self.redirect_streams()
        try:
            steam_api.SteamAPI_Init()
            self.restore_streams()
        except:
            self.restore_streams()
            p = multiprocessing.current_process()
            print('%s(%d): Couldn\'t initialize Steam API' % (p.name, p.pid))
            sys.stdout.flush()
            return

        while True:
            sleep(1)

    def redirect_streams(self):
        # redirect stdout and stderr of steam api
        devnull = os.open(os.devnull, 777)
        self.old_stdout = os.dup(1)
        self.old_stderr = os.dup(2)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)

    def restore_streams(self):
        # restore stdout and stderr
        os.dup2(self.old_stdout, 1)
        os.dup2(self.old_stderr, 2)

sameDelay = 0
lastDelay = 5
def calc_delay(remainingDrops):
    ''' Calculate the idle delay
        Minimum play time for cards to drop is ~20min again. Except for accounts
        that requested a refund?

        Re-check every 15 mintes if there are more than 1 card drops remaining.
        If only one drop remains, check every 5 minutes
    '''
    global sameDelay, lastDelay

    # Reset lastDelay for new appids
    if remainingDrops > 1:
        lastDelay = 5
        sameDelay = 0

    if remainingDrops > 2:
        return 15 * 60 # Check every 15 minutes
    elif remainingDrops == 2:
        return 10 * 60 # Check every 10 minutes
    else:
        # decrease delay by one minute every two calls
        if lastDelay > 1:
            if sameDelay == 2:
                sameDelay = 0
                lastDelay -= 1
            sameDelay += 1
        return lastDelay * 60 # Check every 5 minutes
