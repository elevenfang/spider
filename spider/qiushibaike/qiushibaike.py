# coding=utf-8

import requests
import sqlite3
from bs4 import BeautifulSoup

main_url = 'http://www.qiushibaike.com/hot/page/'
conn = sqlite3.connect('/Users/xxxxxxxx/develop/pycharm_workspace/spider/com/ld/db/qiubai.db')
cur = conn.cursor()


def drop_table():
    drop_table_sql = '''drop table qiubai_remen'''
    cur.execute(drop_table_sql)
    conn.commit()


def create_table():
    creat_table_sql = '''create table qiubai_remen(content text)'''
    cur.execute(creat_table_sql)
    conn.commit()


def save_sqlite(span):
    sql = "insert into qiubai_remen values('" + str(span) + "')"
    cur.execute(sql)
    conn.commit()


def get_all_match_contents(page_index):
    full_url = main_url + str(page_index) + '/?s=4950605'
    response = requests.get(full_url)
    html = response.text
    soup = BeautifulSoup(html)
    contents = soup.find_all('div', {'class': 'content'})
    return contents


def parse_contents(contents):
    for content in contents:
        spans = content.find_all('span')
        for span in spans:
            print('         ####-->', span.text)
            save_sqlite(span)


drop_table()
create_table()
page_index = 1
while page_index <= 35:
    contents = get_all_match_contents(page_index)
    parse_contents(contents)
    print('Current page', page_index)
    page_index += 1
