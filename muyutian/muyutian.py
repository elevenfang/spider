# -*- coding:utf-8 -*-

import urllib.request
import re
import collections
import os
import time
import sys
import codecs

homePageUrl = 'http://m.muyutian.net'
base_url = 'http://m.muyutian.net/vodtype/'
date = time.strftime("_%Y-%m-%d")
sourceFolder = os.getcwd() + '/StoreFolder/'
if not os.path.exists(sourceFolder):
    os.mkdir(sourceFolder)

part_of_path_dict = {
    # '1':'电影',
    # '2':'电视剧',
    # '4':'动漫',
    5: u'动作片',
    6: u'喜剧片',
    7: u'爱情片',
    8: u'科幻片',
    9: u'恐怖片',
    11: u'战争片',
    12: u'国产剧',
    13: u'港台剧',
    14: u'日韩剧',
    15: u'欧美剧',
    16: u'日韩动漫',
    17: u'国产动漫',
    18: u'剧情片'
}

print('default encoding:' + sys.stdout.encoding)


def get_video_info(url):
    common_pattern = re.compile(
        r'<li><div class="video"><a class="pic" href="(.*?)"><img width="90" height="120" src="(.*?)"></a><a class="set" href="(.*?)">(.*?)</a></div><a href="(.*?)">(.*?)</a></li>')
    response = urllib.request.urlopen(url, timeout=180)
    html = response.read().decode()
    video_info = re.findall(common_pattern, html)
    return video_info


def store_video_info(videoInfo, itemName):
    lines = []
    for each_info in videoInfo:
        video_name = each_info[5]
        video_url = homePageUrl + each_info[4]
        video_extral_info = each_info[3]
        #       videoPic = each_info[1]
        line = video_name + '[' + video_extral_info + ']' + '\n' + video_url
        lines.append(line)
    path = (os.getcwd() + '/StoreFolder/' + itemName + date + '.txt')
    with codecs.open(path, 'a', encoding='utf-8') as f:
        f.writelines('%s\n' % line for line in lines)


def run_spider(path_no, item_name):
    filename = item_name + date + ".txt"
    full_path = os.path.join(sourceFolder, filename)
    if os.path.isfile(full_path):
        os.remove(full_path)
    i = 1
    while True:
        full_url = base_url + path_no + '-' + str(i) + '.html'
        try:
            video_info = get_video_info(full_url)
            if len(video_info) == 0:
                i -= 1
                break
            else:
                store_video_info(video_info, item_name)
                i += 1
        except Exception as e:
            print(e)
            print('finish item:' + path_no)
            break
    count = get_video_count(full_path)
    print('video type:' + item_name + ' total pages:' + str(i) + ' video count:' + str(count))


def get_video_count(full_path):
    f = codecs.open(full_path, 'r', 'UTF-8')
    return len(f.readlines()) // 2


sorted_result = collections.OrderedDict(sorted(part_of_path_dict.items()))
for (k, v) in sorted_result.items():
    run_spider(str(k), v)
