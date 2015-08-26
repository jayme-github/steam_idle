import re
from bs4 import BeautifulSoup
from steamweb import SteamWebBrowserCfg
from steam_idle import BLACKLIST

# Some regular expressions
re_AppId = re.compile(r'card_drop_info_gamebadge_(\d+)_')
re_Drops = re.compile(r'(\d+) card drop(?:s\b|\b) remaining')
re_PlayTime = re.compile(r'(\d+\.\d) hrs on record')

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

def parse_badges_page(return_all=True, appid_filter=[]):
    ''' Iterates over all badges pages of a steam profile
        Parses all badges (using parse_badge()) to return the appId, play time ('till now) and the number of card drops left.
        
        @param return_all also return apps that have no card drops left
        @param appid_filter only look for appids listed here
    '''
    swb = SteamWebBrowserCfg() #TODO: SteamWebBrowserCfg init
    if not swb.logged_in():
        swb.login()
    
    filter_appids = True if appid_filter else False
    parsed_badges = []
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
            pbadge = parse_badge(b)
            # Ensure all no value is None and there are drops remaining
            if all(e != None for e in pbadge) and (return_all or pbadge[1] > 0):
                if filter_appids:
                    # appId's where given as filter, check if this appId is one of those
                    if pbadge[0] in appid_filter:
                        appid_filter.remove(pbadge[0])
                    else:
                        # This appid is NOT in the filter list.
                        # don't include it in the returned list
                        continue

                # Append app info to the list of parsed badges
                parsed_badges.append(pbadge)

                if filter_appids and len(appid_filter) == 0:
                    # appId's where given as filter and all of them where found already
                    # so we are done.
                    break
        # Next page
        currentPage += 1

    return sorted(parsed_badges, key=lambda x: x[2], reverse=True)

def parse_apps_to_idle(appid_filter=[]):
    # TODO: parse badges page, add app info (like name and icon)
    raise NotImplementedError 
