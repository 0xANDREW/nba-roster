import json
import re

import requests
from bs4 import BeautifulSoup
import html5lib

URL_BASE = 'http://espn.go.com'
SCHEDULE_URL = '%s/nba/team/schedule/_/name/gs/year/%d/golden-state-warriors'
BOXSCORE_URL = '%s/nba/boxscore?gameId=%s'
YEARS = [ 2015, 2014, 2013 ]

def get_game_ids(soup):
    rv = []

    for link in soup.select('li.score a'):
        m = re.search('id=(\d+)', link['href'])

        if m:
            rv.append(m.group(1))

    return rv

def get_starters(game_id):
    rv = {
        'game_id': game_id,
        'starters': []
    }

    # Use Box Score page to find starters
    url = BOXSCORE_URL % (URL_BASE, game_id)

    # Use html5lib parser, Box Score page HTML is broken
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')

    theads = soup.select('#my-players-table thead')
    gs_head = None

    for th in theads:
        link = th.select('.team-color-strip a')

        # Break when team found (can be in top or bottom table)
        if len(link) > 0 and link[0]['name'] == 'Golden State':
            gs_head = th
            break

    if gs_head:

        # Find sibling <tbody>
        player_tr = gs_head.findNext('tbody').select('tr')

        for tr in player_tr:
            rv['starters'].append(tr.find('td').text)
        
    return rv

if __name__ == '__main__':
    rv = {}
    
    for year in YEARS:
        rv[year] = []

        # Use Schedule page to find master list of game IDs
        url = SCHEDULE_URL % (URL_BASE, year)
        soup = BeautifulSoup(requests.get(url).content)

        game_ids = get_game_ids(soup)
        ct = 1

        for gid in game_ids:
            print '%d: %d/%d' % (year, ct, len(game_ids))
            ct += 1
            
            st = get_starters(gid)
            rv[year].append(st)

            print st

    # Pretty print to JSON
    with open('gsw-starters.json', 'w') as f:
        f.write(json.dumps(rv,
                           sort_keys=True,
                           indent=4,
                           separators=(',', ': ')
        ))
