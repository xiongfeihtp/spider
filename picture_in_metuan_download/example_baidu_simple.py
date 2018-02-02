import requests
from bs4 import BeautifulSoup
import re
import os
import numpy as np
import shutil
import time
import json
from urllib.parse import quote
#根据名字爬取百度百科的内容
picture_num = 0

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'baike.baidu.com',
    'Referer': 'https://www.baidu.com/link?url=GXJEe6ivIoz-pIjL5oRNOEZuriihzPRkko57tJI49l_HuaGOjfpN-BUbtRKOzeZL&wd=&eqid=8bccd3200000a9c40000000359ef643f',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Content-Type': 'text/html',
}


def get_start_links(url):
    try:
        ip = requests.get(
            'http://api.ip.data5u.com/dynamic/get.html?order=a3db5ab3e1a8162ae1f6362c3d15fd5b&sep=3').text.strip()
        print(ip)
        proxy = {'http': 'http://' + ip}
        html = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        time.sleep(1)
        if "You don't have permission to access the URL on this server" in html.text:
            print('Not exist')
            return get_start_links(url)
        else:
            print('exist')
            html.encoding = 'utf-8'
            html = html.text
            # print(html)
            return html
    except Exception as e:
        print('ip error')
        time.sleep(1)
        return get_start_links(url)


fp = open('label_from.txt', 'r')
x = json.load(fp)  # 分隔符
label_list = []
for key in x.keys():
    for i in x[key]:
        label_list.append(i)

context_dic = {}

for i, word in enumerate(label_list[2:3]):
    # problem with chinese decoding in url,quote
    url1 = 'https://baike.baidu.com/item/' + quote(word)
    main_page = get_start_links(url1)
    soup = BeautifulSoup(main_page, 'lxml')
    # store_name
    s = soup.find_all('div', class_="para")
    context_list = []
    for item in s:
        text = item.get_text()
        if len(text) < 20:
            continue
        else:
            text.replace('\\n', '')
            # all necessary character
            text = "".join(re.findall('[\u4e00-\u9fa5A-Za-z,，\。\（\）\(\)：:]+', text))
            context_list.append(text)
    context_dic[word] = context_list
fp = open('test.txt', 'w')
json.dump(context_dic,fp)

