# coding=utf-8

import requests
from bs4 import BeautifulSoup

main_url = 'http://www.qiushibaike.com/hot/page/'

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


page_index = 1
while page_index <= 35:
    contents = get_all_match_contents(page_index)
    parse_contents(contents)
    print('Current page', page_index)
    page_index += 1
