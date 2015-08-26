import sys
import os
import multiprocessing
from time import sleep
from steam_idle import steam_api

class IdleChild(multiprocessing.Process):
    def __init__(self, appid):
        super(IdleChild, self).__init__()
        self.appid = int(appid)
        self.name += '-[%s]' % str(self.appid)
        self.exit = multiprocessing.Event()

    def run(self):
        os.environ['SteamAppId'] = str(self.appid)
        p = multiprocessing.current_process()
        me = '%s(%d):' % (p.name, p.pid)

        #self.redirect_streams()
        try:
            steam_api.SteamAPI_Init()
            #self.restore_streams()
        except:
            #self.restore_streams()
            print(me, "Couldn't initialize Steam API")
            sys.stdout.flush()
            return

        print(me, 'Ideling appid %d' % (self.appid,))
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
