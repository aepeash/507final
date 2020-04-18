
import json
import requests
from bs4 import BeautifulSoup
import sqlite3

BASE_URL = 'https://www.ncaa.com/'
CACHE_FILENAME = "cache.json"
CACHE_DICT = {}
RANK_PAGE = "https://www.ncaa.com/rankings/lacrosse-women/d1/ncaa-womens-lacrosse-rpi"
def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()


# team table data
def get_url():
    page = requests.get(RANK_PAGE).text
    if RANK_PAGE not in CACHE_DICT.keys():
        CACHE_DICT[RANK_PAGE] = page
        save_cache(CACHE_DICT)
    return CACHE_DICT[RANK_PAGE]

with open(CACHE_FILENAME, 'r') as j:
    json_data = json.load(j)
    print(json_data)
table_info = []

for row in json_data.values():
    soup = BeautifulSoup(row, 'html.parser')
    tables = soup.find_all('tr')
    for i in range(len(tables)):

        tag_to_find = 'td'

        td = tables[i].find_all(tag_to_find)

        row = [foo.text for foo in td]
        table_info.append(row[:3])
print(table_info[1:])


connection = sqlite3.connect('womenslax.sqlite')
cur = connection.cursor()

drop_teams = """
    DROP TABLE IF EXISTS "Teams";

"""

create_teams = """
    CREATE TABLE IF NOT EXISTS "Teams" (
        "Rank" INTEGER,
        "School" TEXT PRIMARY KEY, 
        "Conference" TEXT 
        );
"""

cur.execute(drop_teams)
cur.execute(create_teams)

connection.commit()

insert_teams = """
    INSERT INTO Teams
    VALUES (?, ?, ?)
"""
for team in table_info[1:]:
    cur.execute(insert_teams, team)

connection.commit()

