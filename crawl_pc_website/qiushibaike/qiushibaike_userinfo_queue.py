# coding=utf-8

import requests
import collections
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import logging
import json
import queue
import threading
import random

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/home/xxxxx/qiushibaike/qiushibaike.log',
                    filemode='w')

base_user_url = 'http://www.qiushibaike.com/users/'

user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

client = MongoClient('127.0.0.1', 27017)
db = client['qiushibaike']
collection = db['user_info_multithread1']

q = queue.Queue(maxsize=0)

s = requests.session()
response = s.get('http://www.qiushibaike.com')
cookies = response.cookies


def save_user_info(users):
    sorted_result = collections.OrderedDict(sorted(users.items()))
    collection.save(users)


def get_user_info(user_url):
    try:
        headers = {'User-Agent': user_agent_list[random.randint(0, 17)]}
        time.sleep(0.2)
        response = requests.get(user_url, cookies=cookies)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        return get_dict_for_user_info(soup)
    except Exception as e:
        logging.error('exception:%s', e)
        return {}


def get_dict_for_user_info(soup):
    head_img_url = get_user_head_img_url(soup)
    user_name = get_user_name(soup)
    user_info = soup.find('div', {'class': 'user-col-left'}).find_all('div', {'class': 'user-statis user-block'})
    return get_user_details(head_img_url, user_info, user_name)


def get_user_details(head_img_url, user_info, user_name):
    users = {'用户名': user_name, '头像': head_img_url}
    for person_profile in user_info:
        person_profile_header = person_profile.find('h3')
        if '个人资料' == person_profile_header.string:
            person_profile_data_collection = person_profile.find('ul').find_all('li')
            for person_profile_data in person_profile_data_collection:
                person_profile_data_detail = person_profile_data.get_text()
                single_person_profile_data_detail = person_profile_data_detail.split(':')
                if len(single_person_profile_data_detail) == 2:
                    users[single_person_profile_data_detail[0]] = single_person_profile_data_detail[1]
                else:
                    users[single_person_profile_data_detail[0]] = ''
    return users


def get_user_name(soup):
    user_name_div = soup.find('div', {'class': 'user-header-cover'})
    user_name_content = user_name_div.find('h2').string
    return user_name_content


def get_user_head_img_url(soup):
    user_head_img = soup.find('div', {'class': 'user-header'})
    head_img_href = user_head_img.find('a')
    head_img_url = head_img_href.find('img')['src']
    return head_img_url


class MyThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q

    def run(self):
        while not self.q.empty():
            full_url = self.q.get()
            logging.info('url:%s', full_url)
            user_info = get_user_info(full_url)
            if len(user_info) > 0:
                user_str = json.dumps(user_info)
                logging.info('get user info:count%s,%s', str(i), user_str.encode('gbk'))
                save_user_info(user_info)
            self.q.task_done()


start_time = time.time()

# for i in range(9991986):
for i in range(200000):
    q.put(base_user_url + str(i))

for i in range(1):
    thread = MyThread(q)
    thread.start()

q.join()
end_time = time.time()
logging.info('end,total time:%f,seconds:%f', (end_time - start_time) / 60 / 60, end_time - start_time)
