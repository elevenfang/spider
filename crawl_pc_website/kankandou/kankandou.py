# coding=utf-8

from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import logging
import time
import collections

# **************feature
# get book list for each category
# get total page

# **************feature
# login (precondition)
# get book details for each book ( include download url )
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
# &&&&&&&&&&&&&&please customer define the log path***************
                    filename='/home/xxxxx/xxxxx/kankandou.log',
                    filemode='w')

s = requests.session()
response = s.get('https://kankandou.com/')
cookies = response.cookies

base_url = 'https://kankandou.com/'
category_arrays = []
category_url_arrays = []

client = MongoClient('127.0.0.1', 27017)
db = client['kankandou']
collection = db['kankandou_book']

proxy = {'http': '33.33.33.10:8118'}


def get_each_category_base_url():
    for category in category_arrays:
        category_url = base_url + 'book/' + category + '.html'
        category_url_arrays.append(category_url)


def get_full_category():
    soup = get_soup_from_url(base_url)
    category_summary = soup.find('ul', {'class': 'nav'})
    tag_for_category_arrays = category_summary.find_all(
        lambda tag: tag.name == 'li' and tag.get('class') == ['navi', ''])
    for tag_for_category in tag_for_category_arrays:
        category = tag_for_category.find('a').string
        category_arrays.append(category)


def get_current_category_total_pages(url):
    soup = get_soup_from_url(url)
    page_summary = soup.find('ul', {'class': 'paging'})
    page_arrays = page_summary.find_all('li')
    last_page = page_arrays[len(page_arrays) - 1]
    total_page = last_page.find('a')['data-page']
    return total_page


def get_soup_from_url(url):
    time.sleep(2)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
    print(url)
    requests.adapters.DEFAULT_RETRIES = 5
    response = requests.get(url, headers=headers, cookies=cookies, verify=False, proxies=proxy)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    return soup


def fetch_book_info_from_url(page_url):
    try:
        soup = get_soup_from_url(page_url)
    except Exception as e:
        print(e)
        time.sleep(10)
        logging.error('fetch again for url:%s', page_url)
        try:
            soup = get_soup_from_url(page_url)
        except Exception as e:
            print(e)
            logging.error('error url second time,return:%s', page_url)
            return
    print(page_url)
    extract_info_from_html(soup)


def extract_info_from_html(soup):
    book_info_arrays = soup.find_all('div', {'class': 'o-info'})
    for book_info in book_info_arrays:
        book_name_tag = book_info.find('h3', {'class': 'o-name'})
        book_name = book_name_tag.string
        book_url = book_name_tag.find('a')['href']
        book_author = book_info.find('p', {'class': 'o-author'}).get_text().split('：')[1]
        book_type = book_info.find('p', {'class': 'o-cate'}).get_text().split('：')[1]
        print(book_name, book_author, book_type, book_url)
        logging.info('book list:%s,%s,%s,%s', book_name, book_author, book_type, book_url)
        book = {'name': book_name, 'author': book_author, 'type': book_type, 'url': book_url}
        save_book_info_to_db(book)


def save_book_info_to_db(book):
    sorted_result = collections.OrderedDict(sorted(book.items()))
    collection.save(sorted_result)


def analyze_each_page_of_category(single_category_url, total_page_size):
    for page in range(1, int(total_page_size)):
        page_url = single_category_url.replace('.html', '/' + str(page))
        fetch_book_info_from_url(page_url)


def analyze_each_category():
    for single_category_url in category_url_arrays:
        total_page_size = get_current_category_total_pages(single_category_url)
        analyze_each_page_of_category(single_category_url, total_page_size)


if __name__ == "__main__":
    get_full_category()
    get_each_category_base_url()
    analyze_each_category()
