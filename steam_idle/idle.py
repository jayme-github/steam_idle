import sys
import os
import multiprocessing
from datetime import datetime, timedelta
from math import ceil
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
        self.name += '-[%s]' % str(self.app.name)
        self.exit = multiprocessing.Event()

    def run(self):
        os.environ['SteamAppId'] = str(self.app.appid)
        p = multiprocessing.current_process()
        me = '%s(%d):' % (p.name, p.pid)

        #self.redirect_streams()
        try:
            steam_api.SteamAPI_Init()
            pass
            #self.restore_streams()
        except:
            #self.restore_streams()
            print(me, "Couldn't initialize Steam API")
            sys.stdout.flush()
            return

        print(me, 'Ideling appid %d' % (self.app.appid,))
        sys.stdout.flush()

        while not self.exit.is_set():
            sleep(1)

        print(me, 'shutting down')
        sys.stdout.flush()

        # Shutsdown steam api
        steam_api.SteamAPI_Shutdown()

    def shutdown(self):
        self.exit.set()

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
def calc_delay(remainingDrops, playTime):
    ''' Calculate the idle delay
        Minimum play time for cards to drop is 2 hours.
        Re-check every 15 mintes if there are more than 1 card drops remaining.
        If only one drop remains, check every 5 minutes
    '''
    global sameDelay, lastDelay
    baseDelay = int((2.0 - playTime) * 60 * 60)
    if baseDelay < 0:
        baseDelay = 0

    # Reset lastDelay for new appids
    if remainingDrops > 1:
        lastDelay = 5
        sameDelay = 0

    if remainingDrops > 2:
        return baseDelay + (15 * 60) # Check every 15 minutes
    elif remainingDrops == 2:
        return baseDelay + (10 * 60) # Check every 10 minutes
    else:
        # decrease delay by one minute every two calls
        if lastDelay > 1:
            if sameDelay == 2:
                sameDelay = 0
                lastDelay -= 1
            sameDelay += 1
        return baseDelay + (lastDelay * 60) # Check every 5 minutes


def multiIdle(apps):
    # Idle all apps with playTime < 2h in parallel
    processes = []
    for appid, remainingDrops, playTime in [x for x in apps if x[2] < 2.0]:
        delay = int((2.0 - playTime) * 60 * 60)
        endtime = (datetime.now() + timedelta(seconds=delay))
        p = IdleChild(appid)
        p.start()
        processes.append((endtime, p))

    #FIXME Should be ordered, shortest idle first
    for endtime, p in processes:
        now = datetime.now()
        if endtime < now:
            print(p, 'endtime (%s) is in the past, shutting down' % (endtime,))
            p.shutdown()
            p.join()
            continue
        diff = int(ceil((endtime - now).total_seconds()))
        if diff <= 0:
            print(p, 'diff (%s) is below 0, shutting down' % (diff,))
            p.shutdown()
            p.join()
            continue
        print('Sleeping for %s till %s' %(
            strfsec(diff),
            (datetime.now() + timedelta(seconds=diff)).strftime('%c')
        ))
        sleep(diff)
        p.shutdown()
        p.join()
