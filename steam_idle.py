#!/usr/bin/env python

import os
import re
import sys
import argparse
import atexit
from time import sleep
from ctypes import CDLL
import multiprocessing
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from math import ceil
from steamweb import SteamWebBrowser

BLACKLIST = (368020, 335590)
MAX_IDLE = 5 * 60 * 60 # Maximum idle time (avoid infinite loop)

re_Drops = re.compile(ur'(\d+) card drop(?:s\b|\b) remaining')
re_AppId = re.compile(ur'card_drop_info_gamebadge_(\d+)_')
re_PlayTime = re.compile(ur'(\d+\.\d) hrs on record')

swb = SteamWebBrowser()
if not swb.logged_in():
    swb.login()

class Idle(multiprocessing.Process):
    def __init__(self, appid):
        super(Idle, self).__init__()
        self.appid = int(appid)
        self.name += '-[%s]' % str(self.appid)
        self.exit = multiprocessing.Event()

    def run(self):
        os.environ["SteamAppId"] = str(self.appid)
        p = multiprocessing.current_process()
        me = '%s(%d):' % (p.name, p.pid)
        
        # redirect stdout and stderr from steam api
        devnull = os.open(os.devnull, 777)
        self.old_stderr = os.dup(2)
        self.old_stdout = os.dup(1)
        os.dup2(devnull, 2)
        os.dup2(devnull, 1)
        steam_api = CDLL('/usr/local/lib/libsteam_api64.so')
        try:
            steam_api.SteamAPI_Init()
        except:
            print me, "Couldn't initialize Steam API" 
            sys.stdout.flush()
            return

        print me, 'Ideling appid %d' % (self.appid,)
        sys.stdout.flush()

        while not self.exit.is_set():
            sys.stdout.flush()
            sleep(1)
        
        print me, 'shutting down'
        sys.stdout.flush()

        # Shutsdown steam api
        steam_api.SteamAPI_Shutdown()
        # restore stdout and stderr
        os.dup2(self.old_stderr, 2)
        os.dup2(self.old_stdout, 1)

    def shutdown(self):
        self.exit.set()

def r_sleep(sec):
    ''' Sleep sec seconds and return seconds slept '''
    sleep(sec)
    return sec

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
    
    if remainingDrops > 1:
        # reset lastDelay for new appids
        lastDelay = 5
        sameDelay = 0
        return baseDelay + (15 * 60) # Check every 15 minutes
    else:
        # decrease delay by one minute every two calls
        if lastDelay > 1:
            if sameDelay == 2:
                sameDelay = 0
                lastDelay -= 1
            sameDelay += 1
        return baseDelay + (lastDelay * 60) # Check every 5 minutes

def strfsec(seconds):
    return str(timedelta(seconds=seconds))

def parse_badge(badge):
    try:
        # Parse AppId
        drop_info = badge.find('div', {'class': 'card_drop_info_dialog'}).attrs.get('id')
        appid = int(re_AppId.match(drop_info).groups()[0])
    except:
        return (None, None, None)
    if appid in BLACKLIST:
        return (None, None, None)

    try:
        # Parse remaining drops (will raise if there are none)
        progress = badge.find('span', {'class': 'progress_info_bold'}).get_text()
        remainingDrops = int(re_Drops.match(progress).groups()[0])
    except:
        remainingDrops = 0

    try:
        # Parse play time
        playTime = float(re_PlayTime.search(badge.get_text()).groups()[0])
    except:
        playTime = 0.0
    return (appid, remainingDrops, playTime)

def parse_badges_page():
    parsed_badges = []
    currentPage = 1
    badgePages = 1

    while currentPage <= badgePages:
        r = swb.get('https://steamcommunity.com/my/badges', params={'p': currentPage})
        soup = BeautifulSoup(r.content, 'html.parser')
        if currentPage == 1:
            try:
                badgePages = int(soup.find_all('a', {'class': 'pagelink'})[-1].get_text())
            except:
                pass

        for b in soup.find_all('div', {'class': 'badge_title_stats'}):
            pbadge  = parse_badge(b)
            if all(e != None for e in pbadge) and pbadge[1] > 0:
                parsed_badges.append(pbadge)

        currentPage += 1

    return sorted(parsed_badges, key=lambda x: x[2], reverse=True)


def main_idle(badges):
    global args

    # Just to make sure it's ordered
    badges = sorted(badges, key=lambda x: x[2], reverse=True)

    if not args.skip_multi:
        # Idle all apps with playTime < 2h in parallel
        processes = []
        for appid, remainingDrops, playTime in filter(lambda x: x[2] < 2.0, badges):
            delay = int((2.0 - playTime) * 60 * 60)
            endtime = (datetime.now() + timedelta(seconds=delay))
            p = Idle(appid)
            p.start()
            processes.append((endtime, p))

        # should be ordered, shortest idle first
        # TODO output and testing
        print processes
        for endtime, p in processes:
            now = datetime.now()
            if endtime < now:
                print p, 'endtime (%s) is in the past, shutting down' % (endtime,)
                p.shutdown()
                p.join()
                continue
            diff = int(ceil((endtime - now).total_seconds()))
            if diff <= 0:
                print p, 'diff (%s) is below 0, shutting down' % (diff,)
                p.shutdown()
                p.join()
                continue
            print p, 'Sleeping for %s till %s' %(
                strfsec(diff),
                (datetime.now() + timedelta(seconds=diff)).strftime('%c')
            )
            sleep(diff)
            print p, 'Woke up, shutting down'
            p.shutdown()
            p.join()

    # All apps should be out of refund time, (playTime >= 2h), idle one by one
    new_badges = [] # new apps added douring idle
    for appid, remainingDrops, playTime in badges:
        idletime = 0
        p = Idle(appid)
        p.start()
        while remainingDrops > 0:
            delay = calc_delay(remainingDrops, playTime)
            print '%d has %d remaining drops: Ideling for %s (\'till %s)' % (
                    appid,
                    remainingDrops,
                    strfsec(delay),
                    (datetime.now() + timedelta(seconds=delay)).strftime('%c')
            )
            idletime += r_sleep(delay)
            if idletime >= MAX_IDLE:
                break

            # Re check for remainingDrops and new apps
            remainingDrops = 0 # Will be re-set if appid is still returned by parse_badges_page()
            for b in parse_badges_page():
                if not filter(lambda x: x[0] == b[0], badges):
                    print 'Found a new app to idle: %d has %d remaining drops, play time till now: %0.1f hours' % (b[0], b[1], b[2])
                    if b[2] >= 2.0:
                        # Already out of refund time, add to the one by one idle list
                        badges.append(b)
                    else:
                        # Needs "refund-idle"
                        new_badges.append(b)
                    continue

                if b[0] == appid:
                    # Still drops left for this app, continue idleing
                    appid, remainingDrops, playTime = b
            print '%d drops remaining, playtime is %0.1f' %(remainingDrops, playTime)

        # Stop idleing
        p.shutdown()
        p.join()

    if new_badges:
        # We've found new apps that need "refund-idle"
        print 'Found %d new apps that need "refund-idle":' %(len(new_badges),)
        if args.verbose:
            for appid, remainingDrops, playTime in new_badges:
                print '%d has %d remaining drops, play time till now: %0.1f hours' % (appid, remainingDrops, playTime)
        main_idle(new_badges)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Idle all steam apps with card drops left.')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
    parser.add_argument('-l', '--list', help='don\'t idle, just list apps with card drops', action='store_true')
    parser.add_argument('--skip-multi', help='don\'t multi-idle all apps with playtime < 2h first', action='store_true')
    args = parser.parse_args()

    # make sure this is only run once
    pidfile = os.path.join(os.path.dirname(__file__), 'steam-idle.pid')
    if os.path.isfile(pidfile):
        print 'already running ("%s")' % pidfile
        sys.exit(1)
    with open(pidfile, 'w') as pf:
        pf.write(str(os.getpid()))
    atexit.register(os.unlink, pidfile)

    badges = parse_badges_page()

    print '%d games with a total of %d card drops left:' % (len(badges), sum([x[1] for x in badges]))
    if args.verbose or args.list:
        for appid, remainingDrops, playTime in badges:
            print '%d has %d remaining drops, play time till now: %0.1f hours' % (appid, remainingDrops, playTime)
    if args.list:
        sys.exit(0)

    main_idle(badges)
