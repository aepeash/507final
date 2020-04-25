import json
import sqlite3
from bs4 import BeautifulSoup as bs
import requests

BASE_URL = 'https://www.ncaa.com/'
RANK_URL = 'rankings/lacrosse-women/d1/ncaa-womens-lacrosse-rpi'
STATS_URL = 'stats/lacrosse-women/d1'
CACHE_FILENAME = "laxcache.json"
CACHE_DICT = {}
DBNAME = 'womenslax.sqlite'


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


def get_url_html(url):
    if url not in CACHE_DICT.keys():
        response = requests.get(url).text
        CACHE_DICT[url] = response
        save_cache(cache_dict=CACHE_DICT)

    return CACHE_DICT[url]


def beautify_html(html):
    return bs(html, 'html.parser')


def get_team_data():
    url = BASE_URL + RANK_URL

    team_data = []

    raw_html = get_url_html(url=url)
    soup_html = beautify_html(raw_html)

    table_rows = soup_html.find_all('tr')

    for row in table_rows:
        cols = row.find_all('td')
        return_record = [col.text for col in cols]
        team_data.append(return_record[:3])

    team_data = [team for team in team_data if team != []]

    return team_data


def save_player_html(stats_wanted):
    homepage_url = BASE_URL + STATS_URL
    homepage_html = get_url_html(homepage_url)
    homepage_html = beautify_html(homepage_html)

    stats_dropdown = homepage_html.find(
        class_='js-form-item form-item js-form-type-select form-item- js-form-item- form-no-label')
    links = stats_dropdown.find_all('option')[1:]

    links = [link for link in links if link.text in stats_wanted]

    for link in links:
        stat_page_url = BASE_URL + link['value']
        stat_page_html = get_url_html(stat_page_url)
        stat_page_html = beautify_html(stat_page_html)

        subpages = stat_page_html.find(class_='stats-pager').find_all('a')

        for subpage in subpages:
            subpage_url = BASE_URL + subpage['href']
            get_url_html(subpage_url)


def get_player_page(player_stat_page_url):
    players = []

    raw_html = get_url_html(player_stat_page_url)
    soup_html = beautify_html(raw_html)

    table_rows = soup_html.find_all('tr')

    for i in range(len(table_rows)):
        cols = table_rows[i].find_all('td')
        return_record = [col.text for col in cols]
        players.append(return_record[1:])

    players = [list(x) for x in set(tuple(x) for x in players)]
    players = [player for player in players if player != []]

    return players


def get_player_data():
    player_pages = []
    for url, html in CACHE_DICT.items():

        if beautify_html(html).find_all('div', class_='stats-header__lower__title') != []:
            player_pages.append(url)

    player_data_table = []
    for page in player_pages:
        player_page_data = get_player_page(page)

        for player in player_page_data:
            player_data_table.append(player)

    field_players = []
    goalies = []

    for player in player_data_table:
        if len(player) == 8:
            field_players.append(player + ["N/A"] * 5)
        elif len(player) == 10:
            goalies.append(player[:5] + ["N/A"] * 3 + player[5:])

    player_data_table = field_players + goalies

    return player_data_table


if __name__ == '__main__':

    save_cache(CACHE_DICT)
    team_data = get_team_data()

    save_player_html(stats_wanted=['Points', 'Save Percentage'])
    player_data = get_player_data()

    connection = sqlite3.connect(DBNAME)
    cur = connection.cursor()

    drop_teams = """
            DROP TABLE IF EXISTS "teams";
        """

    create_teams = """
            CREATE TABLE IF NOT EXISTS "teams" (
                "rank" INTEGER  ,
                "school" TEXT PRIMARY KEY, 
                "conference" TEXT 
                );
        """

    drop_players = """
           DROP TABLE IF EXISTS "players";
        """

    create_players = """
            CREATE TABLE IF NOT EXISTS "players" (
                "player" TEXT,
                "school" TEXT,
                "class" TEXT,
                "field_position" TEXT, 
                "games_played" TEXT,
                "goals" TEXT,
                "assists" TEXT,
                "points" TEXT,
                "minutes_played" TEXT,
                "team_minutes" TEXT,
                "goals_allowed" TEXT,
                "saves" TEXT,
                "save_percent" TEXT 
                );
        """
    cur.execute(drop_teams)
    cur.execute(create_teams)
    cur.execute(drop_players)
    cur.execute(create_players)

    connection.commit()

    insert_players = """
                          INSERT INTO players
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                  """

    for player in player_data:
        cur.execute(insert_players, player)

    insert_teams = """
                    INSERT INTO teams
                    VALUES (?, ?, ?)
                """

    for team in team_data:
        cur.execute(insert_teams, team)

    connection.commit()