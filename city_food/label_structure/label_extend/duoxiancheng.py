#!/usr/bin/env python
# -*- coding:utf-8 -*-
import queue
import sys
import requests
import os
import threading
import time
import json
from bs4 import BeautifulSoup
import re
import shutil
#多线程下载图片,递归下载，一次只启动一个程序
#另外一种思路，用另外一个python程序去控制启动其他python程序
num=int(sys.argv[1])
picture_num=0

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

class Worker(threading.Thread):  # 处理工作请求
    def __init__(self, workQueue, resultQueue, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue

    def run(self):
        while 1:
            try:
                callable, args, kwds = self.workQueue.get(False)  # get task
                res = callable(*args, **kwds)
                self.resultQueue.put(res)  # put result
            except queue.Empty:
                break


class WorkManager:  # 线程池管理,创建
    def __init__(self, num_of_workers=10):
        self.workQueue = queue.Queue()  # 请求队列
        self.resultQueue = queue.Queue()  # 输出结果的队列
        self.workers = []
        self._recruitThreads(num_of_workers)

    def _recruitThreads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.workQueue, self.resultQueue)  # 创建工作线程
            self.workers.append(worker)  # 加入到线程队列

    def start(self):
        for w in self.workers:
            w.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()  # 从池中取出一个线程处理请求
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append(worker)  # 重新加入线程池中
        print('All jobs were complete.')

    def add_job(self, callable, *args, **kwds):
        self.workQueue.put((callable, args, kwds))  # 向工作队列中加入请求

    def get_result(self, *args, **kwds):
        return self.resultQueue.get(*args, **kwds)


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
            #print(html)
            return html
    except Exception as e:
        #print('ip error')
        time.sleep(1)
        return get_start_links(url)

def get_picture(url):
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
            print(html)
            return html
    except Exception as e:
        print('ip error')
        time.sleep(1)
        return get_start_links(url)


def download_file(item):
    global picture_num
    pic=None
    picture_url=None
    main_page = get_start_links(item[0])

    soup = BeautifulSoup(main_page, 'lxml')
    try:
        picture_url = soup.find("img", class_="recipe_cover")["src"]
        pic = requests.get(picture_url,timeout=10)
    except Exception as e:
        print('picture can not be download!!!')
    string = './picture_place/'+item[2] + '/' + 'pictures_for' + item[2] + '_' + item[1] + '_' + item[3] + str(
        picture_num) + '.jpg'
    try:
        tmp=pic.content
        with open(string, 'wb') as fp:
            fp.write(pic.content)
    except Exception as e:
        print("picture with no data")
    picture_num += 1
    print(item[2], "downloading", item[1], "picture_num", picture_num)

def main():
    global num
    if not os.path.exists('picture_place'):
        os.mkdir('picture_place')

    num_of_threads = 10
    _st = time.time()
    wm = WorkManager(num_of_threads)
    print(num_of_threads)
    # dish_load
    dic_save = {}
    for i in range(1,11):
        file_name = './changed_dic_save_dish' + str(i) + '.txt'
        with open(file_name, 'r') as f:
            dic_save[i] = json.load(f)
            # dic_save have all the information
    dish_category_list = list(dic_save[6].keys())
    all_dish = dic_save[6]

    dish_category=dish_category_list[num]
    if not os.path.exists('./picture_place/'+dish_category):
        os.mkdir('./picture_place/'+dish_category)
    url_list = []
    for m, dish in enumerate(all_dish[dish_category]):
        length = len(all_dish[dish_category])
        print("loading %f" % (m / length))
        dish_num = dish[0]
        dish_name = dish[1]
        dish_page = 'http://www.haodou.com/recipe/' + dish_num + '/'
        url_list.append([dish_page,dish_name,dish_category,dish_num])
    print("loading competeing,stay 5 sec")
    for i in url_list:
        wm.add_job(download_file, i)
    wm.start()
    print("start")
    wm.wait_for_complete()
    print(time.time() - _st)
    num+=1
    print("complete,begin another",dish_category_list[num])
    string="nohup python3 -u picture_down_load_yibu_duoxiancheng_c.py "+str(num)+" &"
    os.system(string)

if __name__ == '__main__':
    main()

