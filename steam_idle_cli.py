#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import argparse
import atexit
from time import sleep
from datetime import timedelta, datetime
from math import ceil
import logging
from steamweb import SteamWebBrowserCfg as SteamWebBrowser
from steam_idle import steam_api
from steam_idle.page_parser import SteamBadges
from steam_idle.idle import strfsec, IdleChild, calc_delay

def main_idle(apps):
    # Just to make sure it's ordered
    apps = sorted(apps, key=lambda x: x.playTime, reverse=True)
    if not args.skip_multi:
        # Idle all apps with playTime < 2h in parallel
        processes = []
        for app in [app for app in apps if app.playTime < 2.0]:
            delay = int((2.0 - app.playTime) * 60 * 60)
            endtime = (datetime.now() + timedelta(seconds=delay))
            p = IdleChild(app)
            p.start()
            processes.append((endtime, p))
            if args.verbose:
                print(p.name)
            # Steam client will crash if childs spawn too fast; Fixes #1
            sleep(0.25)
        if args.verbose:
            print('Multi-Idling %d apps' % len(processes))

        # Should be ordered, shortest idle first
        for endtime, p in processes:
            now = datetime.now()
            if endtime < now:
                print(p, 'endtime (%s) is in the past, shutting down' % (endtime,))
                p.terminate()
                p.join()
                continue
            diff = int(ceil((endtime - now).total_seconds()))
            if diff <= 0:
                print(p, 'diff (%s) is below 0, shutting down' % (diff,))
                p.terminate()
                p.join()
                continue
            print('Sleeping for %s till %s' %(
                strfsec(diff),
                (datetime.now() + timedelta(seconds=diff)).strftime('%c')
            ))
            sleep(diff)
            if args.verbose:
                print(p, 'Woke up, shutting down')
            p.terminate()
            p.join()

        if processes:
            # Multi-Idled some apps, update values as they will have changed
            apps = [app for app in sbb.get_apps(fetch_images=False).values() if app.remainingDrops > 0]
            # If there are still apps with < 2.0h play time, restart
            if [app for app in apps if app.playTime < 2.0] > 1:
                print('There are still apps within refund time, restarting multi-idle')
                return main_idle(apps)

    # All apps should be out of refund time, (playTime >= 2h), idle one by one
    if args.verbose:
        print('Startin sequential idle of %d apps' % len(apps))
    new_apps = [] # new apps added douring idle
    for app in apps:
        p = IdleChild(app)
        p.start()
        while app.remainingDrops > 0:
            delay = calc_delay(app.remainingDrops)
            print('"%s" has %d remaining drops: Idling for %s (\'till %s)' % (
                    app.name,
                    app.remainingDrops,
                    strfsec(delay),
                    (datetime.now() + timedelta(seconds=delay)).strftime('%c')
            ))
            sleep(delay)

            # Re check for remainingDrops and new apps
            for a in sbb.get_apps(fetch_images=False).values():
                if a.remainingDrops > 0 and not [x for x in apps + new_apps if x.appid == a.appid]:
                    print('Found a new app to idle: "%s" has %d remaining drops, play time till now: %0.1f hours' % (a.name, a.remainingDrops, a.playTime))
                    if a.playTime >= 2.0:
                        # Already out of refund time, add to the one by one idle list
                        apps.append(a)
                    else:
                        # Needs "refund-idle"
                        new_apps.append(a)
                    continue

                if a.appid == app.appid:
                    # Still drops left for this app, continue idleing
                    app = a
            print('%d drops remaining, playtime is %0.1f' %(app.remainingDrops, app.playTime))

        # Stop idleing
        p.terminate()
        p.join()

    if new_apps:
        # We've found new apps that need "refund-idle"
        print('Found %d new apps that need "refund-idle":' %(len(new_apps),))
        if args.verbose:
            for app in new_apps:
                print('"%s" has %d remaining drops, play time till now: %0.1f hours' % (app.name, app.remainingDrops, app.playTime))
        return main_idle(new_apps)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Idle all steam apps with card drops left.')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
    parser.add_argument('-d', '--debug', help='enable debug output', action='store_true')
    parser.add_argument('-l', '--list', help='don\'t idle, just list apps with card drops', action='store_true')
    parser.add_argument('--skip-multi', help='don\'t multi-idle all apps with playtime < 2h first', action='store_true')
    parser.add_argument('-a', '--appid', help='idle only specific app ID\'s', type=int, nargs='*')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(asctime)s (%(name)s.%(funcName)s) [%(levelname)s] %(message)s', level=logging.DEBUG)

    swb = SteamWebBrowser()
    sbb = SteamBadges(swb)

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
        if not steam_api.IsSteamRunning():
            print('Could not find a running Steam instance!')
            print('Please start your Steam Client.')
            sys.exit(1)

    apps = [app for app in sbb.get_apps(fetch_images=False).values() if app.remainingDrops > 0]

    print('%d games with a total of %d card drops left:' % (len(apps), sum([app.remainingDrops for app in apps])))
    if args.verbose or args.list:
        for app in apps:
            print('"%s" has %d remaining drops, play time till now: %0.1f hours' % (app.name, app.remainingDrops, app.playTime))
    if args.list:
        sys.exit(0)

    main_idle(apps)
