import os
import re
import stat
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
    icon = property(lambda self: self._imgpath('icon'))
    logosmall = property(lambda self: self._imgpath('logosmall'))
    header = property(lambda self: self._imgpath('header'))
    def __init__(self, image_path=''):
        self.image_path = image_path
    def __repr__(self):
        return '<[{:6d}] "{}" ({}, {:.1f})>'.format(
            self.appid or 0,
            self.name.encode('ascii', 'ignore') or 'Unknown app',
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
    def _imgpath(self, imgtype):
        if not isinstance(self.appid, int):
            return None
        return os.path.join(self.image_path, '%d_%s.jpg' % (self.appid, imgtype))
    @property
    def storeUrl(self):
        return 'https://store.steampowered.com/app/{}'.format(self.appid or '')

def mockSome():
    import random
    apps = {}
    for i in (232770,262830,285010,321950,343100,307170,311210,233290):
        a = App()
        a.appid = i
        a.remainingDrops = random.randint(0,6)
        a.playTime = round(random.uniform(0.0, 10.0),1)
        apps[i] = a
    return apps

class FetchImages(multiprocessing.Process):
    ''' Multiprocessing worker to fetch and store icon and logo for an app
    '''
    def __init__(self, task_queue, image_path):
        super(FetchImages, self).__init__()
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))
        self.task_queue = task_queue
        self.image_path = image_path
        self.session = requests.Session()

    def run(self):
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill
                self.task_queue.task_done()
                self.session.close()
                break
            # Process this task
            self.fetch_images(next_task)
            self.task_queue.task_done()
        self.session.close()
        return

    def fetch_images(self, task):
        appinfo = task
        appid = appinfo.get('appid')
        for imgtype in ('icon', 'logosmall', 'header'):
            filename = '%d_%s.jpg' % (appid, imgtype)
            imagepath = os.path.join(self.image_path, filename)
            if imgtype == 'header':
                url = 'https://steamcdn-a.akamaihd.net/steam/apps/%d/header_292x136.jpg' % appid
            else:
                url = appinfo.get(imgtype+'url')
            self.logger.debug('Processing %d: imgtype: %s, filename: "%s", path: "%s", url: "%s"',
                                appid, imgtype, filename, imagepath, url)
            if url is None:
                self.logger.error('No URL found')
                continue

            r = self.session.get(url)
            with open(imagepath, 'wb') as f:
                f.write(r.content)

def chunks(l, n):
    '''Yield successive n-sized chunks from l.'''
    for i in range(0, len(l), n):
        yield l[i:i+n]

class SteamBadges(object):
    ''' Holds methods for parsing badge pages etc. '''
    def __init__(self, swb, data_path=''):
        self.logger = logging.getLogger('.'.join((__name__, self.__class__.__name__)))
        self.swb = swb
        if data_path != '':
            self.data_path = data_path
        else:
            self.data_path = swb.appdata_path
        self.logger.info('Using "%s" as data path', self.data_path)
        self.shelve_path = os.path.join(self.data_path, 'cache')
        self.image_path = os.path.join(self.data_path, 'images')
        if not os.path.exists(self.image_path):
            os.makedirs(self.image_path, stat.S_IRWXU)

    def parse_badge(self, badge):
        app = App(self.image_path)
        try:
            # Parse AppId
            drop_info = badge.find('div', {'class': 'card_drop_info_dialog'}).attrs.get('id')
            app.appid = int(re_AppId.match(drop_info).groups()[0])
        except:
            raise AppIdNotFoundError('Could not parse AppId from badge: %s' % badge.prettify())

        if app.appid in GLOBAL_BLACKLIST: #TODO Blacklist check should be done by the "frontend"
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

    def parse_badges_pages(self, appid_filter=None):
        ''' Iterates over all badges pages of a steam profile
            Parses all badges (using parse_badge()) to return the appId, play time ('till now) and the number of card drops left.

            @param appid_filter only look for appids listed here
        '''
        appid_filter = appid_filter or []
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
        with shelve.open(self.shelve_path) as appshelve:
            try:
                del appshelve[str(appid)]
            except KeyError:
                # No such key in shelve, ignore
                pass
        for imgtype in ('icon', 'logosmall'):
            filename = '%d_%s.jpg' % (appid, imgtype)
            imagepath = os.path.join(self.image_path, filename)
            if os.path.exists(imagepath):
                os.unlink(imagepath)

    def get_apps(self, appid_filter=None, fetch_images=True):
        ''' Parse the badge pages, add app info (like name and icon) if needed
            fetch and store the icons and cache app info in shelve.

            Return a dict of all apps on badges page (with and without remaining drops):
            {<appid>: <App istance>, <appid>: <App instance>, ...}
        '''
        appid_filter = appid_filter or []
        apps = self.parse_badges_pages(appid_filter)
        #apps = mockSome()

        # check for appids not in shelve
        appshelve = shelve.open(self.shelve_path)
        appids_not_in_shelve = []
        for appid in apps.keys():
            if str(appid) in appshelve:
                # Load aditional app info from shelve
                a = appshelve[str(appid)]
                apps[appid].name = a['name']
            else:
                appids_not_in_shelve.append(str(appid))

        if appids_not_in_shelve:
            # GetAppInfo only returns info for 100 apps at once
            # TODO: Call https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/ with access_token instead?
            # params = {'access_token': self.swb.oauth_access_token, 'appids_filter': ','.join(appids_not_in_shelve), 'steamid': swb.steamid, 'format': 'json', 'include_appinfo': 1}

            appinfos = []
            self.logger.debug('Requesting %d appids from GetAppInfo:', len(appids_not_in_shelve))
            for appid_chunk in chunks(appids_not_in_shelve, 100):
                params = {
                    'access_token': self.swb.oauth_access_token,
                    'appids': ','.join(appid_chunk)
                }
                self.logger.debug('Requesting a chunk of %d appids from GetAppInfo:', len(appid_chunk))
                r = self.swb.get('https://api.steampowered.com/ISteamGameOAuth/GetAppInfo/v1/', params=params)
                ainfo = r.json().get('apps', [])
                appinfos.extend(ainfo)
                self.logger.debug('GetAppInfo returned data for %d appids:', len(ainfo))

            if fetch_images is True:
                # Retrieve and store icon and logosmall
                tasks = multiprocessing.JoinableQueue()
                num_consumers = multiprocessing.cpu_count() * 2

                consumers = []
                for _i in range(num_consumers):
                    c = FetchImages(tasks, self.image_path)
                    c.start()
                    consumers.append(c)

                for appinfo in appinfos:
                    tasks.put(appinfo)

                # Add a poison pill for each consumer
                for _i in range(num_consumers):
                    tasks.put(None)

                # Wait for all of the tasks to finish
                tasks.join()

            # Merge new data with data from shelve and store new values
            for appinfo in appinfos:
                appid = appinfo.get('appid')
                name = appinfo.get('name')
                apps[appid].name = name
                # Store in shelve
                data = {
                    'name': name,
                }
                appshelve[str(appid)] = data

        appshelve.close()
        return apps
