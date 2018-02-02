import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
import time
import json
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.haodou.com',
    'Referer': 'http://www.haodou.com/recipe/all/?ct=1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Content-Type': 'text/html; charset=UTF-8',
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


# meun
url1 = 'http://www.haodou.com/recipe/category/'
main_page = get_start_links(url1)
soup = BeautifulSoup(main_page, 'lxml')
# find label
s = soup.find('div', class_="rcp_all_class")
# find all label
A = s.find_all('dd', class_="rcp_tags")
dic_save_meun = {}
#leave the name and number
for item in A[6].find_all('a'):
    dic_save_meun[item.get_text()] = re.sub("\D", "", item["href"])

dic_save_dish={}
for i, word in enumerate(dic_save_meun):
    temp_list=[]
    for m in range(1,4):
        for n in range(1,100):
            url = 'http://www.haodou.com/recipe/all/?do=getrecipe&tid=' + dic_save_meun[word] + '&order=popular&bigpage=' + str(n)+ '&smallpage=' + str(m)
            main_page = get_start_links(url)
            if 'id' not in main_page:
                print('page is outier')
                break
            soup = BeautifulSoup(main_page, 'lxml')
            temp_list.extend(re.findall('"id":(.*?),"cover"',soup.text))
    dic_save_dish[word] =temp_list


