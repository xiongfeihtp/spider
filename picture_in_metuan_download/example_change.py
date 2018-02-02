import requests
from bs4 import BeautifulSoup
import re
import os
import numpy as np
import shutil
import time
import config

picture_num = 0
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'sh.meituan.com',
    'Referer': 'http://sh.meituan.com/meishi/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Content-Type': 'text/html; charset=utf-8',
}


def get_start_links(url):
    try:
        ip = requests.get(
            'http://api.ip.data5u.com/dynamic/get.html?order=a3db5ab3e1a8162ae1f6362c3d15fd5b&sep=3').text.strip()
        print(ip)
        proxy = {'http': 'http://' + ip}
        html = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        time.sleep(0.5)
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
        time.sleep(0.5)
        return get_start_links(url)


def picture_download(pic_url, posion):
    global picture_num
    for each in pic_url:
        each = each.replace("126.126", "668.500")
        try:
            pic = requests.get(each, timeout=10)
        except requests.exceptions.ConnectionError:
            print('【错误】当前图片无法下载')
            continue
        string = '/Users/xiongfei/PycharmProjects/爬虫/' + str(posion) + '/pictures\\' + str(picture_num) + '.jpg'
        with open(string, 'xb') as fp:
            fp.write(pic.content)
        picture_num += 1


store_list = np.load('store_np.npy')
list = []
for item in store_list:
    list.append(item[0])


Begin_num=config.Begin_num
store_num_list = list[Begin_num:]
length = len(store_num_list)
comment_list = []
pic_list = []
store_information = []
all_information = []
NUM_Page = config.NUM_Page


for i, store_num in enumerate(store_num_list):
    # store information
    url1 = 'http://sh.meituan.com/shop/' + str(store_num)
    main_page = get_start_links(url1)
    soup = BeautifulSoup(main_page, 'lxml')
    # store_name
    s = soup.find("div", class_="fs-section__left")
    # s.find("h2").get_text()
    # position
    # s.find("p").get_text()
    # position data
    # s.find_all("span")[2]["data-params"]
    store_information_item = [s.find("h2").get_text(),
                              s.find("p", class_="under-title").find("span", class_="geo").get_text(),
                              s.find("p", class_="under-title").find("span",id="map-canvas")["data-params"]]

    # store_information.append(store_information_item)
    comment_list = []
    pic_list = []
    # page one
    url2 = 'http://sh.meituan.com/deal/feedbacklist/0/' + str(
        store_num) + '/all/0/default/10?limit=10&showpoititle=0&offset=0&withpic=1'
    main_page = get_start_links(url2)
    if 'norate-tip' in main_page:
        # stores with no comments were also stored
        all_information.append([store_information_item])
        continue
    # store have no comment
    # before lxml preprocessing first
    pre_main_page = main_page.replace('\\n', '').replace('\\', '')
    soup = BeautifulSoup(pre_main_page, 'lxml')
    for link in soup.find_all('div', class_=r'J-normal-view'):
        comment_list.append(link.find('p').get_text())
        pic_list.append([link.find("a").find("img")["src"] for link in link.find("ul").find_all("li")])
    # page two and so on
    for page_num in range(1, NUM_Page):
        print(page_num)
        url3 = 'http://sh.meituan.com/deal/feedbacklist/0/' + str(
            store_num) + '/all/0/default/10?limit=10&showpoititle=0&offset=' + str(page_num) + '0' + '&withpic=1'
        main_page = get_start_links(url3)
        # page_num is outer
        if 'norate-tip' in main_page:
            break
        # before lxml preprocessing first
        pre_main_page = main_page.replace('\\n', '').replace('\\', '')
        soup = BeautifulSoup(pre_main_page, 'lxml')
        for link in soup.find_all('div', class_=r'J-normal-view'):
            comment_list.append(link.find('p').get_text())
            pic_list.append([link.find("a").find("img")["src"] for link in link.find("ul").find_all("li")])
    all_information.append([store_information_item, comment_list, pic_list])

    #comments change coding
    temp = []
    for item in all_information[i][1]:
        temp_comment = item.strip().replace('u', '\\u')
        try:
            Chinese_characters = eval("'" + temp_comment + "'")
            temp.append(Chinese_characters)
        except SyntaxError as e:
            print("comment coding error")
            temp.append(temp_comment)
    all_information[i][1] = temp

    # download the special store picture and delete \\
    file = '/Users/xiongfei/PycharmProjects/爬虫/' + str(store_num)
    # if os.path.exists(file):
    #     shutil.rmtree(file)
    os.mkdir(file)

    temp_length = len(all_information[i][2])
    large_temp\
        = []  # repetition in different comment
    for item in range(temp_length):
        temp = []
        for picture in all_information[i][2][item]:
            # find there are many repetition picture
            if picture in temp:
                print('picture repetition happen in one comment')
                continue
            else:
                if picture in large_temp:
                    print('picture repetition happen in different comment')
                    continue
                else:
                    large_temp.append(picture)
                    temp.append(picture)
        all_information[i][2][item] = temp
        picture_download(temp, store_num)
    print("compete percen tage %f" % ((i + 1) / length))

