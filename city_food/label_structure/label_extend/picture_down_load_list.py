#-*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os
import numpy as np
import shutil
import time
import json
#下载图片加载完成后，在批量下载
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
            print('Not exist')
            return get_start_links(url)
        else:
            print('exist')
            html.encoding = 'utf-8'
            html = html.text
            #print(html)
            return html
    except Exception as e:
        print('ip error')
        time.sleep(1)
        return get_start_links(url)

def picture_download(dish_category,picture_list,picture_name_list,picture_num_list):
    global picture_num
    for i,each in enumerate(picture_list):
        try:
            pic = requests.get(each, timeout=10)
        except requests.exceptions.ConnectionError:
            print('picture can not be downloaded')
            continue
        string = dish_category + '/' + 'pictures_for' + dish_category + '_' + picture_name_list[i] + '_' + picture_num_list[i] + str(picture_num) + '.jpg'
        with open(string, 'xb') as fp:
            fp.write(pic.content)
        picture_num += 1
        print(dish_category, "downloading", picture_name_list[i], "picture_num", picture_num)
# dish_load
dic_save = {}
for i in range(11):
    file_name = './label_structure/label_extend/changed_dic_save_dish' + str(i) + '.txt'
    with open(file_name, 'r') as f:
        dic_save[i] = json.load(f)
        # dic_save have all the information

dish_category_list=dic_save[6].keys()
all_dish=dic_save[6]


for dish_category in dish_category_list:
    if not os.path.exists(dish_category):
        os.mkdir(dish_category)
    picture_list=[]
    picture_name_list=[]
    picture_num_list=[]
    for m,dish in enumerate(all_dish[dish_category][1:10]):
        length=len(all_dish[dish_category][1:10])
        print("loading %.3f"%(m/length))
        dish_num=dish[0]
        dish_name=dish[1]
        dish_page='http://www.haodou.com/recipe/'+dish_num+'/'
        main_page = get_start_links(dish_page)
        soup = BeautifulSoup(main_page, 'lxml')
        try:
            picture_url = soup.find("img", class_="recipe_cover")["src"]
        except TypeError as e:
            print("log in error")
            continue
        picture_list.append(dish_page)
        picture_name_list.append(dish_name)
        picture_num_list.append(dish_num)
    picture_download(dish_category,picture_list,picture_name_list,picture_num_list)
