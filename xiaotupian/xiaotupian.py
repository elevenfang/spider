# coding=utf-8

import threading
import urllib.request
import re
import os
import shutil

home_url = "http://www.xxxxxx.com/"
list_url_without_specila_page = home_url + "thread0806.php?fid=21&search=&page="
img_root_folder_name = "img_root"
page_index = 1
total_page = 100


def get_result_lists_from_html_by_pattern(url, regular_expression):
    result_lists = []
    try:
        response = urllib.request.urlopen(url, timeout=18)
        html = response.read().decode('GBK')
        pattern = re.compile(regular_expression)
        result_lists = re.findall(pattern, html)
    except Exception as e:
        print('Exception:', url, e)
    return result_lists


def create_img_folder(page_index):
    img_root_folder = os.getcwd() + '/' + img_root_folder_name
    if not os.path.exists(img_root_folder):
        os.mkdir(img_root_folder)
    img_child_folder = img_root_folder + '/' + str(page_index)
    if not os.path.exists(img_child_folder):
        os.mkdir(img_child_folder)
    else:
        shutil.rmtree(img_child_folder)


def get_current_page_all_items(page_url):
    print('page_url', page_url)
    return get_result_lists_from_html_by_pattern(page_url,
                                                 r'<h3><a href="(.*?)" target="_blank" id="">(.*?)</a></h3>')


def download_current_page_image(lists, folder_index):
    count = 0
    current_page_count = count
    for list in lists:
        extend_url = list[0]
        item_full_url = home_url + extend_url
        subject = list[1][0:list[1].find('[')]
        if not subject.startswith('<b>'):
            imgs = get_result_lists_from_html_by_pattern(item_full_url, r'<img src="(.*?)"')
            for img in imgs:
                img_url = img
                count = download_img(subject, img_url, count, folder_index)
    return count


def download_img(subject, image_url, count, folder_index):
    print('     start-->image_url', image_url)
    img_path = (img_root_folder_name + '/' + str(folder_index) + '/%d_%s.png') % ((count + 1), subject)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = urllib.request.Request(url=image_url, headers=headers)
        img_data = urllib.request.urlopen(req, timeout=18).read()
        f = open(img_path, 'wb')
        f.write(img_data)
        print('     end-->saving image...', img_path, '********', count)
        f.close()
        count += 1
    except Exception as e:
        print('     fail-->saving image', img_path, e, '########', count)
    return count


class MyThread(threading.Thread):
    def __init__(self, page_index):
        threading.Thread.__init__(self)
        self.page_index = page_index

    def run(self):
        create_img_folder(self.page_index)
        folder_index = self.page_index
        try:
            page_url = list_url_without_specila_page + str(self.page_index)
            items = get_current_page_all_items(page_url)
            count = download_current_page_image(items, folder_index)
            print('download ' + str(self.page_index) + ' page image', 'total count:' + str(count))
        except Exception as e:
            print('thread exception for:', e, page_url)


while page_index <= total_page:
    try:
        thread = MyThread(page_index)
        thread.start()
        page_index += 1
    except Exception as e:
        print('outside_of_thread_exception', e)
