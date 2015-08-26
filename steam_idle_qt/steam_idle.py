#!/usr/bin/env python
from __future__ import print_function
import os
import re
import sys
import argparse
import atexit
from time import sleep
from ctypes import CDLL, c_bool, c_void_p
import multiprocessing
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from math import ceil
from steamweb import SteamWebBrowserCfg as SteamWebBrowser

BLACKLIST = (368020, 335590)
MAX_IDLE = 5 * 60 * 60 # Maximum idle time (avoid infinite loop)

re_Drops = re.compile(r'(\d+) card drop(?:s\b|\b) remaining')
re_AppId = re.compile(r'card_drop_info_gamebadge_(\d+)_')
re_PlayTime = re.compile(r'(\d+\.\d) hrs on record')

swb = SteamWebBrowser()
if not swb.logged_in():
    swb.login()

def get_steam_api():
    try:
        if sys.platform.startswith('win'):
            so = 'steam_api.dll'
        elif sys.platform.startswith('darwin'):
            so = 'libsteam_api.dylib'
        elif sys.platform.startswith('linux'):
            if sys.maxsize > 2**32:
                so = 'libsteam_api_64.so'
            else:
                so = 'libsteam_api.so'
        else:
            raise EnvironmentError('Unsupported operating system')
        steam_api = CDLL(os.path.join('libs', so))
        steam_api.SteamAPI_IsSteamRunning.restype = c_bool
        steam_api.SteamAPI_Init.restype = c_bool
        steam_api.SteamAPI_Shutdown.restype = c_void_p
    except Exception as e:
        print('Not loading Steam library: {}'.format(e))
    return steam_api

class Idle(multiprocessing.Process):
    def __init__(self, appid):
        super(Idle, self).__init__()
        self.appid = int(appid)
        self.name += '-[%s]' % str(self.appid)
        self.exit = multiprocessing.Event()

    def run(self):
        os.environ['SteamAppId'] = str(self.appid)
        p = multiprocessing.current_process()
        me = '%s(%d):' % (p.name, p.pid)
        
        self.redirect_streams()
        steam_api = get_steam_api()
        try:
            steam_api.SteamAPI_Init()
            self.restore_streams()
        except:
            self.restore_streams()
            print(me, "Couldn't initialize Steam API") 
            sys.stdout.flush()
            return

        print(me, 'Ideling appid %d' % (self.appid,))
        sys.stdout.flush()

        while not self.exit.is_set():
            sys.stdout.flush()
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
    ''' Parses badges (using parse_badge()) on all badges pages
    If specific appid's are given on the command line, only those are returned.
    '''
    global args
    parsed_badges = []
    currentPage = 1
    badgePages = 1

    # args.appid is None if no appids where provided on command line
    argv_appids = list(args.appid) if args.appid else list()

    retry = False
    while currentPage <= badgePages and (args.appid == None or len(argv_appids) > 0):
        r = swb.get('https://steamcommunity.com/my/badges', params={'p': currentPage})
        if r.status_code == 302:
            if retry:
                # We already tries to force a login
                raise Exception('Unable to fetch badges')
            # Looks like we've been redirected. Force a login and retry
            swb.login()
            retry = True
            continue

        soup = BeautifulSoup(r.content, 'html.parser')
        if currentPage == 1:
            try:
                badgePages = int(soup.find_all('a', {'class': 'pagelink'})[-1].get_text())
            except:
                pass

        for b in soup.find_all('div', {'class': 'badge_title_stats'}):
            pbadge = parse_badge(b)
            # Ensure all no value is None and there are drops remaining
            if all(e != None for e in pbadge) and pbadge[1] > 0:
                if args.appid != None:
                    # appid's are given on the command line
                    if pbadge[0] in argv_appids:
                        # This appid was given on the command line
                        argv_appids.remove(pbadge[0])
                    else:
                        # This appid was NOT given on the command line
                        # don't include it in the returned list
                        continue

                # Append app info to the list of parsed badges
                parsed_badges.append(pbadge)

                if args.appid != None and len(argv_appids) == 0:
                    # appid's are given on the command line and all of them where found already
                    break

        currentPage += 1

    return sorted(parsed_badges, key=lambda x: x[2], reverse=True)


def main_idle(apps):
    global args

    # Just to make sure it's ordered
    apps = sorted(apps, key=lambda x: x[2], reverse=True)
    if not args.skip_multi:
        # Idle all apps with playTime < 2h in parallel
        processes = []
        for appid, remainingDrops, playTime in [x for x in apps if x[2] < 2.0]:
            delay = int((2.0 - playTime) * 60 * 60)
            endtime = (datetime.now() + timedelta(seconds=delay))
            p = Idle(appid)
            p.start()
            processes.append((endtime, p))
        if args.verbose:
            print('Multi-Ideling %d apps' % len(processes))

        # Should be ordered, shortest idle first
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
            if args.verbose:
                print(p, 'Woke up, shutting down')
            p.shutdown()
            p.join()

        if processes:
            # Multi-Ideled some apps, update values as they will have changed
            apps = parse_badges_page()
            # If there are still apps with < 2.0h play time, restart
            if [x for x in apps if x[2] < 2.0]:
                print('There are still apps within refund time, restarting multi-idle')
                return main_idle(apps)

    # All apps should be out of refund time, (playTime >= 2h), idle one by one
    if args.verbose:
        print('Startin sequential idle of %d apps' % len(apps))
    new_apps = [] # new apps added douring idle
    for appid, remainingDrops, playTime in apps:
        idletime = 0
        p = Idle(appid)
        p.start()
        while remainingDrops > 0:
            delay = calc_delay(remainingDrops, playTime)
            print('%d has %d remaining drops: Ideling for %s (\'till %s)' % (
                    appid,
                    remainingDrops,
                    strfsec(delay),
                    (datetime.now() + timedelta(seconds=delay)).strftime('%c')
            ))
            idletime += r_sleep(delay)
            if idletime >= MAX_IDLE:
                break

            # Re check for remainingDrops and new apps
            remainingDrops = 0 # Will be re-set if appid is still returned by parse_badges_page()
            for a in parse_badges_page():
                if not [x for x in apps + new_apps if x[0] == a[0]]:
                    print('Found a new app to idle: %d has %d remaining drops, play time till now: %0.1f hours' % (a[0], a[1], a[2]))
                    if a[2] >= 2.0:
                        # Already out of refund time, add to the one by one idle list
                        apps.append(a)
                    else:
                        # Needs "refund-idle"
                        new_apps.append(a)
                    continue

                if a[0] == appid:
                    # Still drops left for this app, continue idleing
                    appid, remainingDrops, playTime = a
            print('%d drops remaining, playtime is %0.1f' %(remainingDrops, playTime))

        # Stop idleing
        p.shutdown()
        p.join()

    if new_apps:
        # We've found new apps that need "refund-idle"
        print('Found %d new apps that need "refund-idle":' %(len(new_apps),))
        if args.verbose:
            for appid, remainingDrops, playTime in new_apps:
                print('%d has %d remaining drops, play time till now: %0.1f hours' % (appid, remainingDrops, playTime))
        return main_idle(new_apps)


def is_steam_running():
    ''' Check if steam is running
    '''
    api = get_steam_api()
    running = api.SteamAPI_IsSteamRunning()
    api.SteamAPI_Shutdown()
    return running

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Idle all steam apps with card drops left.')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
    parser.add_argument('-l', '--list', help='don\'t idle, just list apps with card drops', action='store_true')
    parser.add_argument('--skip-multi', help='don\'t multi-idle all apps with playtime < 2h first', action='store_true')
    parser.add_argument('-a', '--appid', help='idle only specific app ID\'s', type=int, nargs='*')
    args = parser.parse_args()

    if not args.list:
        # make sure this is only run once
        pidfile = os.path.join(os.path.dirname(__file__), 'steam-idle.pid')
        if os.path.isfile(pidfile):
            print('already running ("%s")' % pidfile)
            sys.exit(1)
        with open(pidfile, 'w') as pf:
            pf.write(str(os.getpid()))
        atexit.register(os.unlink, pidfile)

        # Check if Steam is running
        if not is_steam_running():
            print('Could not find a running Steam instance!')
            print('Please start your Steam Client.')
            sys.exit(1)

    apps = parse_badges_page()

    print('%d games with a total of %d card drops left:' % (len(apps), sum([x[1] for x in apps])))
    if args.verbose or args.list:
        for appid, remainingDrops, playTime in apps:
            print('%d has %d remaining drops, play time till now: %0.1f hours' % (appid, remainingDrops, playTime))
    if args.list:
        sys.exit(0)

    main_idle(apps)
