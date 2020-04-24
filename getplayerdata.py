import json
import sqlite3
from itertools import count
import plotly.graph_objects as go
import pandas as pd

from bs4 import BeautifulSoup
import requests

BASE_URL = 'https://www.ncaa.com/'
RANK_URL = 'rankings/lacrosse-women/d1/ncaa-womens-lacrosse-rpi'
STATS_URL = 'stats/lacrosse-women/d1'
CACHE_FILENAME = "allcache.json"
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


def get_url_team():
    rank_page = BASE_URL + RANK_URL
    page = requests.get(rank_page).text
    if rank_page not in CACHE_DICT.keys():
        CACHE_DICT[rank_page] = page
        save_cache(CACHE_DICT)
    return CACHE_DICT[rank_page]


def get_url_player():
    stats_page_url = BASE_URL + STATS_URL
    page = requests.get(stats_page_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find(class_='js-form-item form-item js-form-type-select form-item- js-form-item- form-no-label') \
               .find_all('option')[1:]
    list_of_webpages = []
    for link in soup:
        page_link_tag = link['value']
        page_detail = BASE_URL + page_link_tag
        response = BeautifulSoup(requests.get(page_detail).text, 'html.parser')
        response = response.find(class_='stats-pager').find_all('a')
        for page_link in response:
            page_name = page_link['href']
            page = BASE_URL + page_name
            response = requests.get(page).text
            CACHE_DICT[page] = response
    save_cache(CACHE_DICT)
    return CACHE_DICT[page_detail]


def get_url_two():
    pages_to_crawl = ['Points', 'Save Percentage']
    list_of_stats = []
    stats_page_url = BASE_URL + STATS_URL
    page = requests.get(stats_page_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    soup = soup.find(class_='js-form-item form-item js-form-type-select form-item- js-form-item- form-no-label') \
               .find_all('option')[1:]
    for link in soup:
        page_link_tag = link['value']
        page_detail = BASE_URL + page_link_tag
        response = BeautifulSoup(requests.get(page_detail).text, 'html.parser')
        response = response.find(class_='stats-pager').find_all('a')
        for page_link in response:
            page_name = page_link['href']
            stats_page = BASE_URL + page_name
            list_of_stats.append(stats_page)
    final_pages = []
    for stats_pages in list_of_stats:
        response = BeautifulSoup(requests.get(stats_pages).text, 'html.parser')
        response = response.find('div', class_='stats-header__lower__title')
        if response.string in pages_to_crawl:
            final_pages.append(stats_pages)
    for every_page in final_pages:
        raw_html = requests.get(every_page).text
        CACHE_DICT[every_page] = raw_html
    save_cache(CACHE_DICT)


def open_json():
    with open(CACHE_FILENAME, 'r') as j:
        json_data = json.load(j)
    return json_data


def get_team_data():
    table_info = []
    for key, value in open_json().items():
        if key == 'https://www.ncaa.com/rankings/lacrosse-women/d1/ncaa-womens-lacrosse-rpi':
            soup = BeautifulSoup(value, 'html.parser')
            tables = soup.find_all('tr')
            for i in range(len(tables)):
                tag_to_find = 'td'
                td = tables[i].find_all(tag_to_find)
                row = [foo.text for foo in td]
                table_info.append(row[:3])
    table_info = [team for team in table_info if team != []]
    return table_info


def create_player_lists(stat):
    players = []
    for row in open_json().values():
        soup = BeautifulSoup(row, 'html.parser')
        find_title = soup.find_all('div', class_='stats-header__lower__title')
        for element in find_title:
            if stat in element:
                soup = soup.find_all('tr')
                for i in range(len(soup)):
                    tag_to_find = 'td'
                    td = soup[i].find_all(tag_to_find)
                    record = [foo.text for foo in td]
                    players.append(record[1:])
    players = [list(x) for x in set(tuple(x) for x in players)]
    players = [player for player in players if player != []]
    return players


def merge_lists():
    team_info = get_team_data()
    complete_list = []
    fblanks = [" ", " ", " ", " ", " "]
    field_players = create_player_lists('Points')
    for each_list in field_players:
        f_complete_list = each_list + fblanks
        complete_list.append(f_complete_list)

    defence = create_player_lists('Save Percentage')
    dblanks = [" ", " ", " "]
    for each_list in defence:
        d_complete_list = each_list[:4] + dblanks + each_list[4:]
        complete_list.append(d_complete_list)
    return complete_list


def init_data(team_info, complete_list):
    connection = sqlite3.connect(DBNAME)
    cur = connection.cursor()

    drop_teams = """
            DROP TABLE IF EXISTS "Teams";

        """

    create_teams = """
            CREATE TABLE IF NOT EXISTS "Teams" (
                "Rank" INTEGER  ,
                "School" TEXT PRIMARY KEY, 
                "Conference" TEXT 
                );
        """

    drop_players = """
           DROP TABLE IF EXISTS "Players";

        """

    create_players = """
            CREATE TABLE IF NOT EXISTS "Players" (
                "Player" TEXT,
                "School" TEXT,
                "Class" TEXT,
                "Field Position" TEXT, 
                "Games" INTEGER,
                "Goals" INTEGER,
                "Assists" INTEGER,
                "Points" INTEGER,
                "Minutes Played" INTEGER,
                "Team Minutes" INTEGER,
                "Goals Allowed" INTEGER,
                "Saves" INTEGER,
                "Save Percent" INTEGER 
                );
        """
    cur.execute(drop_teams)
    cur.execute(create_teams)
    cur.execute(drop_players)
    cur.execute(create_players)

    connection.commit()

    insert_players = """
                          INSERT INTO Players
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                  """

    for player in complete_list:
        cur.execute(insert_players, player)

    insert_teams = """
                    INSERT INTO Teams
                    VALUES (?, ?, ?)
                """

    for team in team_info:
        cur.execute(insert_teams, team)

    connection.commit()


def parse_query_params(command):
    params = ['command', 'team_name', 'team_conference', 'order-direction', 'limit', 'plot']
    defaults = ['rank', 'team', 'conference', 'top', 10, None]
    query_dict = dict(zip(params, defaults))

    cmd_list = command.split(' ')

    for cmd in cmd_list:
        if cmd in ('rank', 'team_points', 'player_points', 'saves'):
            query_dict['command'] = cmd

        elif cmd in ('top', 'bottom'):
            query_dict['order_direction'] = cmd

        elif cmd.isnumeric() and (float(cmd) > 0):
            query_dict['limit'] = cmd

        elif cmd == 'barplot':
            query_dict['plot'] = cmd

    return query_dict


def build_sql_from_dict(query_dict):
    columns = ''

    from_clause = '''
    from Teams t
    JOIN Players p 
    on t.School = p.School
    '''

    from_clause = from_clause.replace('  ', '')

    where = ''
    group_by = ''
    having = ''
    order_by = ''

    if query_dict['order-direction'] == 'top':
        order_direction = 'DESC'
    else:
        order_direction = 'ASC'

    limit = f"\nLIMIT {query_dict['limit']}"

    if query_dict['command'] == 'rank':
        columns = 'Rank, t.School, Conference'

    elif query_dict['command'] == 'team_points':
        columns = 't.[rank], t.School, sum(p.Points), sum(p.Goals), sum(p.Assists)'
        group_by = f'\n GROUP BY t.School'
        order_by = f'\n ORDER BY t.rank {order_direction}'

    elif query_dict['command'] == 'player_points':
        columns = 'Player, t.School, p.Points, Goals, Assists'
        where = f"\n WHERE Points is not ' '"

    elif query_dict['command'] == 'saves':
        columns = 'Player, t.School, Saves, [save percent]'
        where = f"\n WHERE Saves is not  ' ' "

    query = f"SELECT {columns} {from_clause} {where} {group_by} {having} {order_by} {limit}"

    return query


def execute_sql(connection, cursor, sql):
    result = cursor.execute(sql).fetchall()

    return result


def print_cmd_result(result):
    for line in result:
        new_line = []

        for item in line:
            if str(item).isnumeric() and float(item) > 0:
                new_item = '{0:d}'.format(item)
                new_item = new_item.ljust(4)
            else:
                new_item = str(item).ljust(30)
            new_line.append(new_item)

        print(' '.join(new_line))


def plot_results(result, query_dict):
    if query_dict['command'] == 'rank':
        x_vals = [line[0] for line in result]
        y_vals = [line[1] for line in result]

    elif query_dict['command'] == 'team_points':
        x_vals = [line[1] for line in result]
        y_vals = [line[2] for line in result]


    elif query_dict['command'] == 'player_points':
        x_vals = [line[0] for line in result]
        y_vals = [line[2] for line in result]

    elif query_dict['command'] == 'saves':
        x_vals = [line[0] for line in result]
        y_vals = [line[3] for line in result]
    else:
        return

    fig = go.Figure(go.Bar(x=x_vals, y=y_vals))
    fig.show()


def process_command(command):
    conn = sqlite3.connect('womenslax.sqlite')
    cur = conn.cursor()

    query_dict = parse_query_params(command)

    if query_dict:
        sql = build_sql_from_dict(query_dict)
        result = execute_sql(connection=conn, cursor=cur, sql=sql)

    else:
        return None

    if query_dict['plot']:
        plot_results(result, query_dict)

    else:
        print_cmd_result(result)

    return result


def interactive_prompt():
    response = ''

    while response != 'exit':
        response = input('Enter on of the following commands:'
                         '\nrank'
                         '\nteam_points'
                         '\nplayer_points'
                         '\nsaves'
                         '\nEnter a command: ').lower().strip()

        if response == 'exit':
            continue

        elif response.split(' ')[0] in ('rank', 'team_points', 'player_points', 'saves'):
            process_command(command=response)
        else:
            print('Sorry your command is not recognized')


if __name__ == '__main__':
    init_data(get_team_data(), merge_lists())
    interactive_prompt()





