# coding=utf-8

import requests
from bs4 import BeautifulSoup
import urllib.request
import os

base_url = 'http://www.qiushibaike.com/pic/page/'
suffix_url = '/?s=4955510'
sourceFolder = os.getcwd() + '/qiubaipic'
if not os.path.exists(sourceFolder):
    os.mkdir(sourceFolder)


def get_match_content(full_url):
    response = requests.get(full_url)
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    whole_match_contents = soup.find_all('div', {'class': 'article block untagged mb15'})
    for each_match_content in whole_match_contents:
        pic_tag = each_match_content.find('div', {'class': 'thumb'})
        pic_url = pic_tag.img['src']
        pic_content = pic_tag.img['alt']
        print('         ', pic_content, pic_url)
        download_img('qiubaipic/' + pic_content + '.jpg', pic_url)


def download_img(image_path, image_url):
    try:
        req = urllib.request.urlretrieve(image_url, image_path)
        print('             saving image...', image_path)
    except Exception as e:
        print(e)


def get_total_page_number():
    max_page = 1
    response = requests.get("http://www.qiushibaike.com/imgrank/")
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    page_number_content = soup.find_all('span', {'class': 'page-numbers'})
    for number_content in page_number_content:
        number = int(number_content.string.strip())
        if number > max_page:
            max_page = number
    return max_page


page = 1
total_page = get_total_page_number()
print('max page is:', total_page)
while page <= total_page:
    full_url = base_url + str(page) + suffix_url
    print('##################', page, full_url)
    get_match_content(full_url)
    page += 1
