import os
import re
import shelve
import requests
import multiprocessing
from bs4 import BeautifulSoup
from steamweb import SteamWebBrowserCfg
from steam_idle import GLOBAL_BLACKLIST

# Some regular expressions
re_AppId = re.compile(r'card_drop_info_gamebadge_(\d+)_')
re_Drops = re.compile(r'(\d+) card drop(?:s\b|\b) remaining')
re_PlayTime = re.compile(r'(\d+\.\d) hrs on record')

swb = SteamWebBrowserCfg() #TODO: SteamWebBrowserCfg init
if not swb.logged_in():
    swb.login()


class PageParserError(Exception):
    pass
class AppIdBlacklistedError(PageParserError):
    pass
class AppIdNotFoundError(PageParserError):
    pass

class App(object):
    appid = None
    name = None
    remainingDrops = None
    playTime = None
    icon = property(lambda self: self._imgname('icon'))
    logosmall = property(lambda self: self._imgname('logosmall'))
    header = property(lambda self: self._imgname('header'))
    def __repr__(self):
        return '<[%d] %s>' %(self.appid or 0, self.name or 'Unknown app')
    def _imgname(self, imgtype):
        if not isinstance(self.appid, int):
            return None
        return '%d_%s.jpg' % (self.appid, imgtype)

def parse_badge(badge):
    app = App()
    try:
        # Parse AppId
        drop_info = badge.find('div', {'class': 'card_drop_info_dialog'}).attrs.get('id')
        app.appid = int(re_AppId.match(drop_info).groups()[0])
    except:
        raise AppIdNotFoundError('Could not parse AppId from badge: %s' % badge.prettify())

    if app.appid in GLOBAL_BLACKLIST:
        raise AppIdBlacklistedError('%d is in global blacklist' % app.appid)

    try:
        # Parse remaining drops (will raise if there are none)
        progress = badge.find('span', {'class': 'progress_info_bold'}).get_text()
        app.remainingDrops = int(re_Drops.match(progress).groups()[0])
    except:
        app.remainingDrops = 0

    try:
        # Parse play time
        app.playTime = float(re_PlayTime.search(badge.get_text()).groups()[0])
    except:
        app.playTime = 0.0

    return app

def parse_badges_pages(return_all=True, appid_filter=[]):
    ''' Iterates over all badges pages of a steam profile
        Parses all badges (using parse_badge()) to return the appId, play time ('till now) and the number of card drops left.

        @param return_all also return apps that have no card drops left (mostly for testing)
        @param appid_filter only look for appids listed here
    '''

    filter_appids = True if appid_filter else False
    parsed_apps = {}
    currentPage = badgePages = 1

    retry = False
    while currentPage <= badgePages and (filter_appids == False or len(appid_filter) > 0):
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
            try:
                app = parse_badge(b)
            except PageParserError:
                # Could not correctly parse app info, continue with the next one
                continue

            # Check if there are drops remaining if return_all==False
            if return_all or app.remainingDrops > 0:
                # AppId's where given as filter, check if this AppId is one of those
                if filter_appids:
                    if app.appid in appid_filter:
                        appid_filter.remove(app.appid)
                    else:
                        # This appid is NOT in the filter list.
                        # don't include it in the returned list
                        continue

                # Add app info to the list of parsed badges
                parsed_apps[app.appid] = app

                if filter_appids and len(appid_filter) == 0:
                    # AppId's where given as filter and all of them where found already
                    # so we are done.
                    break
        # Continue with next page
        currentPage += 1

    return parsed_apps


def fetch_images(appinfo):
    ''' Worker function to fetch and store icon and logo for an app
        Will run in multiprocessing.Pool
    '''
    print('Starting', multiprocessing.current_process().name)
    appid = appinfo.get('appid')
    fetched = {}
    for imgtype in ('icon', 'logosmall', 'header'):
        # FIXME: Path for images
        filename = '%d_%s.jpg' % (appid, imgtype)
        if imgtype == 'header':
            url = 'http://cdn.akamai.steamstatic.com/steam/apps/%d/header_292x136.jpg' % appid
        else:
            url = appinfo.get(imgtype+'url')

        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)
        fetched[imgtype] = filename
    return (appid, appinfo.get('name'), fetched)

def drop_app_cache(appid):
    ''' Drop all info about an app (images from filesystem and app info from shelve)
    '''
    # FIXME: Path for images
    # FIXME: Path for appshelve
    with shelve.open('appshelve') as appshelve:
        try:
            del appshelve[appid]
        except KeyError:
            # No such key in shelve, ignore
            pass
    for imgtype in ('icon', 'logosmall'):
        filename = '%d_%s.jpg' % (appid, imgtype)
        if os.path.exists(filename):
            os.unlink(filename)


def parse_apps_to_idle(appid_filter=[]):
    # parse badges page, add app info (like name and icon)
    apps = parse_badges_pages(appid_filter)

    # check for appids not in shelve
    # FIXME: Path for appshelve
    appshelve = shelve.open('appshelve')
    appids_not_in_shelve = []
    for appid in apps.keys():
        if str(appid) in appshelve:
            # Load aditional app info from shelve
            a = appshelve[str(appid)]
            apps[appid].name = a['name']
        else:
            appids_not_in_shelve.append(str(appid))

    if appids_not_in_shelve:
        params = {
            'access_token': swb.oauth_access_token,
            'appids': ','.join(appids_not_in_shelve)
        }
        r = swb.get('https://api.steampowered.com/ISteamGameOAuth/GetAppInfo/v1/', params=params)
        data = r.json()

        # Retrieve and store icon and logosmall
        pool_size = multiprocessing.cpu_count() * 2
        pool = multiprocessing.Pool(processes=pool_size)
        pool_outputs = pool.map(fetch_images, data.get('apps'))
        pool.close()
        pool.join()

        # Merge new data with data from shelve and store new values
        for appid, name, fetched in pool_outputs:
            apps[appid].name = name
            # Store in shelve
            data = {
                'name': name,
            }
            appshelve[str(appid)] = data

    appshelve.close()
    return apps
