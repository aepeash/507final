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



def parse_query_params(command):
    params = ['command', 'order_direction', 'limit', 'plot', 'table', 'stacked']
    defaults = ['rank', 'top', 10, None, None, None]
    query_dict = dict(zip(params, defaults))

    cmd_list = command.split(' ')

    for cmd in cmd_list:
        if cmd in ('rank', 'team_points', 'player_points', 'team_saves', 'player_saves'):
            query_dict['command'] = cmd

        elif cmd in ('top', 'bottom'):
            query_dict['order_direction'] = cmd

        elif cmd.isnumeric() and (float(cmd) > 0):
            query_dict['limit'] = cmd

        elif cmd == 'barplot':
            query_dict['plot'] = cmd

        elif cmd == 'tableplot':
            query_dict['table'] = cmd

        elif cmd == 'stackedbar':
            query_dict['stacked'] = cmd

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

    if query_dict['order_direction'] == 'top':
        order_direction = 'ASC'
    else:
        order_direction = 'DESC'

    limit = f"\nLIMIT {query_dict['limit']}"

    if query_dict['command'] == 'rank':
        columns = '[Rank], t.School, Conference'
        group_by = f'\n GROUP BY t.School'
        order_by = f'\n ORDER BY [rank] {order_direction}'


    elif query_dict['command'] == 'team_points':
        columns = 't.[rank], t.School, sum(p.Points), sum(p.Goals), sum(p.Assists)'
        group_by = f'\n GROUP BY t.School'
        order_by = f'\n ORDER BY t.[rank] {order_direction}'

    elif query_dict['command'] == 'player_points':
        columns = 'Player, t.School, p.Points, Goals, Assists'
        where = f"\n WHERE Points is not ' '"
        order_by = f'\nORDER BY {order_direction}'


    elif query_dict['command'] == 'team_saves':
        columns = 't.[rank], t.School, sum(saves)'
        group_by = f'\n GROUP BY t.School'
        order_by = f'\n ORDER BY t.[rank] {order_direction}'

    elif query_dict['command'] == 'player_saves':
        columns = 'Player, t.School, Saves, [save percent]'
        where = f"\n WHERE Saves is not  ' ' "
        order_by = f'\n ORDER BY Saves {order_direction}'

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
    if query_dict['command'] == 'player_saves':
        Player = [line[0] for line in result]
        Saves = [line[2] for line in result]


        fig = go.Figure(go.Bar(x=Player, y=Saves,
                               marker_color='rgb(255,203,5)',

                               ))

        fig.show()
    elif query_dict['command'] == 'team_saves':
        Team = [line[1] for line in result]
        Saves = [line[2] for line in result]


        fig = go.Figure(go.Bar(x=Team, y=Saves,
                               marker_color='darkblue',

                              ))
        fig.update_layout(title="Saves")
        fig.show()
    else:
        return


def rank_table(result, query_dict):
    if query_dict['command'] == 'rank':
        fig = go.Figure(data=[go.Table(header=dict(values=['Rank', 'Team'],
                                                    line_color = 'black',
                                                    font_color = 'white',
                                                    fill_color = 'darkblue',
                                                    ),
                                       cells=dict(values=[[line[0] for line in result]
                                           , [line[1] for line in result]],
                                                  line_color='black',
                                                  fill_color='rgb(255,203,5)',
                                                  align='right'
                                                  ))
                              ])
        fig.update_layout(width=500, title="Team Rank")
        fig.show()


def player_plot(result, query_dict):
    if query_dict['command'] == 'player_points':
        x = [line[0] for line in result]
        fig = go.Figure(go.Bar(x=x, y=[line[3] for line in result], name='Goals',
                               marker_color='darkblue'
                               ))
        fig.add_trace(go.Bar(x=x, y=[line[4] for line in result], name='Assists',
                             marker_color='rgb(255,203,5)'))
    elif query_dict['command'] == 'team_points':
        x = [line[1] for line in result]

        fig = go.Figure(go.Bar(x=x, y=[line[3] for line in result], name='Goals',
                               marker_color='darkblue'))
        fig.add_trace(go.Bar(x=x, y=[line[4] for line in result], name='Assists',
                             marker_color='rgb(255,203,5)'))
    fig.update_layout(barmode='stack', title="Points", xaxis={'categoryorder': 'category ascending'})
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

    elif query_dict['table']:
        rank_table(result, query_dict)

    elif query_dict['stacked']:
        player_plot(result, query_dict)

    else:
        print_cmd_result(result)

    return result


def interactive_prompt():
    response = ''

    while response != 'exit':
        response = input("Enter on of the following commands or 'exit' to quit:"
                         '\nrank'
                         '\nteam_points'
                         '\nplayer_points'
                         '\nteam_saves'
                         '\nplayer_saves'
                         '\nEnter a command: ').lower().strip()

        if response == 'exit':
            continue

        elif response.split(' ')[0] in ('rank', 'team_points', 'player_points', 'team_saves', 'player_saves'):
            process_command(command=response)
        else:
            print('Sorry your command is not recognized')


if __name__ == '__main__':
    interactive_prompt()