#-*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
import time
import json
#下载图片，一次循环下载一次
picture_num = 0

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.haodou.com',
    'Referer': 'http://www.haodou.com/recipe/',
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
            #print('Not exist')
            return get_start_links(url)
        else:
            #print('exist')
            html.encoding = 'utf-8'
            html = html.text
            # print(html)
            return html
    except Exception as e:
        #print('ip error')
        time.sleep(1)
        return get_start_links(url)

# dish_load
dic_save = {}
for i in range(11):
    file_name = './changed_dic_save_dish' + str(i) + '.txt'
    with open(file_name, 'r') as f:
        dic_save[i] = json.load(f)
        # dic_save have all the information

dish_category_list=dic_save[6].keys()
all_dish=dic_save[6]


for dish_category in dish_category_list:
    directory_name=dish_category
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    for dish in all_dish[dish_category]:
        dish_num=dish[0]
        dish_name=dish[1]
        dish_page='http://www.haodou.com/recipe/'+dish_num+'/'
        print(dish_page)
        main_page = get_start_links(dish_page)
        soup = BeautifulSoup(main_page, 'lxml')
        try:
            picture_url = soup.find("img", class_="recipe_cover")["src"]
        except TypeError as e:   
            print("log in error")
            continue
        try:
            pic = requests.get(picture_url, timeout=10)
        except requests.exceptions.ConnectionError:
            print('picture can not be download!!!')
            continue
        string = directory_name+'/' + 'pictures_for' + dish_category+'_'+dish_name+'_'+dish_num+str(picture_num) + '.jpg'
        with open(string, 'wb') as fp:
            fp.write(pic.content)
        picture_num+=1
        print(dish_category,"downloading",dish_name,"picture_num",picture_num)
