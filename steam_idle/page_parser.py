import os
import re
import shelve
import logging
import requests
import multiprocessing
from bs4 import BeautifulSoup
from steam_idle import GLOBAL_BLACKLIST

# Some regular expressions
re_AppId = re.compile(r'card_drop_info_gamebadge_(\d+)_')
re_Drops = re.compile(r'(\d+) card drop(?:s\b|\b) remaining')
re_PlayTime = re.compile(r'(\d+\.\d) hrs on record')

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
        return '<[%d] "%s" (%d, %.1f)>' % (
            self.appid or 0,
            self.name or 'Unknown app',
            -1 if self.remainingDrops == None else self.remainingDrops,
            -1.0 if self.playTime == None else self.playTime,
        )
    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.appid == other.appid and \
            self.name == other.name and \
            self.remainingDrops == self.remainingDrops and \
            self.playTime == self.playTime
    def __hash__(self):
        return hash((
            self.appid,
            self.name,
            self.remainingDrops,
            self.playTime
        ))
    def _imgname(self, imgtype):
        if not isinstance(self.appid, int):
            return None
        return '%d_%s.jpg' % (self.appid, imgtype)
    @property
    def storeUrl(self):
        return 'https://store.steampowered.com/app/{}'.format(self.appid or '')

def mockSome():
    import random
    apps = {}
    for i in (232770,262830,285010,321950,343100,307170):
        a = App()
        a.appid = i
        a.remainingDrops = random.randint(0,6)
        a.playTime = round(random.uniform(0.0, 10.0),1)
        apps[i] = a
    return apps


def fetch_images(appinfo):
    ''' Multiprocessing worker function to fetch and store icon and logo for an app
        Will run in multiprocessing.Pool
    '''
    appid = appinfo.get('appid')
    fetched = {}
    for imgtype in ('icon', 'logosmall', 'header'):
        # TODO: Path for images
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


class SteamBadges(object):
    ''' Holds methods for parsing badge pages etc. '''
    def __init__(self, swb):
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))
        self.swb = swb

    def parse_badge(self, badge):
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

    def parse_badges_pages(self, return_all=True, appid_filter=[]):
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
            r = self.swb.get('https://steamcommunity.com/my/badges', params={'p': currentPage})
            if r.status_code == 302:
                if retry:
                    # We already tries to force a login
                    raise Exception('Unable to fetch badges')
                # Looks like we've been redirected. Force a login and retry
                print('Need to login again')
                self.swb.login()
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
                    app = self.parse_badge(b)
                except PageParserError:
                    # Could not correctly parse app info, continue with the next one
                    continue

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

        if not parsed_apps:
            #FIXME: empty badges page == no good.
            print('ERRPOR: Could not find any badges on badge page')
            from tempfile import NamedTemporaryFile
            tmpf = NamedTemporaryFile(prefix='quickDump_', suffix='.html', delete=False)
            print('Dumping r.content to: "file://%s"' % tmpf.name)
            tmpf.write(r.content)
            tmpf.close()
            rname = tmpf.name.replace('.html', '.dat')
            with open(rname, 'w') as tmpf:
                print('Dumping r to: "file://%s"' % rname)
                tmpf.write(vars(r))

        return parsed_apps

    def drop_app_cache(self, appid):
        ''' Drop all info about an app (images from filesystem and app info from shelve)
        '''
        # TODO: Path for images
        # TODO: Path for appshelve
        with shelve.open('appshelve') as appshelve:
            try:
                del appshelve[str(appid)]
            except KeyError:
                # No such key in shelve, ignore
                pass
        for imgtype in ('icon', 'logosmall'):
            filename = '%d_%s.jpg' % (appid, imgtype)
            if os.path.exists(filename):
                os.unlink(filename)

    def get_apps(self,appid_filter=[]):
        ''' Parse the badge pages, add app info (like name and icon) if needed
            fetch and store the icons and cache app info in shelve.
            Return all apps on badges page (with and without remaining drops).
        '''
        apps = self.parse_badges_pages(appid_filter)
        #apps = mockSome()

        # check for appids not in shelve
        # TODO: Path for appshelve
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
                'access_token': self.swb.oauth_access_token,
                'appids': ','.join(appids_not_in_shelve)
            }
            r = self.swb.get('https://api.steampowered.com/ISteamGameOAuth/GetAppInfo/v1/', params=params)
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
