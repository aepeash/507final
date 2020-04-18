#get data
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.ncaa.com/stats/lacrosse-women/d1'
CACHE_FILENAME = "cache.json"
CACHE_DICT = {}

def select_indiv_stat():
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find(class_='js-form-item form-item js-form-type-select form-item- js-form-item- form-no-label')\
        .find_all('option')
    indiv_stat_options = []
    for stat in soup:
        stat = stat.string
        indiv_stat_options.append(stat)
    return indiv_stat_options


def select_team_stat():
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find_all('div', class_='js-form-item form-item js-form-type-select form-item- js-form-item- form-no-label')[1]
    soup = soup.find_all('option')
    team_stat_options = []
    for stat in soup:
        stat = stat.string
        team_stat_options.append(stat)
    return team_stat_options

def get_stats():
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find('table')
    table_rows = soup.find_all('tr')
    for i in range(len(table_rows)):
        if i == 0:
            tag_to_find = 'th'
        else:
            tag_to_find = 'td'

        td = table_rows[i].find_all(tag_to_find)

        row = [foo.text for foo in td]
        print(row)


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()