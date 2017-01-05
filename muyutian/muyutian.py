# -*- coding:UTF-8 -*-

import urllib2
import re

homePageUrl = 'http://m.muyutian.net'
base_url = 'http://m.muyutian.net/vodtype/'

part_of_path_dict = {
# '1':'电影',
# '2':'电视剧',
# '4':'动漫',
'5':'动作片',
'6':'喜剧片',
'7':'爱情片',
'8':'科幻片',
'9':'恐怖片',
'11':'战争片',
'12':'国产剧',
'13':'港台剧',
'14':'日韩剧',
'15':'欧美剧',
'16':'日韩动漫',
'17':'国产动漫'
}

def get_Video_Info(url):
    common_pattern = re.compile(r'<li><div class="video"><a class="pic" href="(.*?)"><img width="90" height="120" src="(.*?)"></a><a class="set" href="(.*?)">(.*?)</a></div><a href="(.*?)">(.*?)</a></li>')
    response = urllib2.urlopen(url)
    html = response.read()
    videoInfo = re.findall(common_pattern, html)
    return videoInfo

def store_Video_Info(videoInfo, itemName):
    lines = []
    for each_info in videoInfo:
        videoName = each_info[5]
        videoUrl = homePageUrl + each_info[4]
        videoExtralInfo = each_info[3]
#       videoPic = each_info[1]
        line = videoName + '['+videoExtralInfo+']'+'\n'+videoUrl
        lines.append(line)
    f = open('StoreFolder/' + itemName + '.txt', 'a＋')
    f.writelines('%s\n' % line for line in lines)
    f.close()
        
def run_sprider(pathNo, itemName):
    print pathNo, itemName
    i = 1
    while True:
        full_url = base_url + pathNo + '-' + str(i) + '.html'
        try:
            videoInfo = get_Video_Info(full_url)
            if len(videoInfo) == 0:
                i -= 1
                break
            else:
                store_Video_Info(videoInfo, itemName)
                i += 1
        except:
            print 'finish item:', pathNo
            break    
    print 'total pages:', str(i), 'with source_path:', homePageUrl + pathNo + '****'
    
sort_result = sorted(part_of_path_dict.iteritems(), key=lambda d:d[0]) 
for (k, v) in  part_of_path_dict.items():
    run_sprider(k, v)








