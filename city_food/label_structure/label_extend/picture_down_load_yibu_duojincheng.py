#-*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
import time
import json
import time
from multiprocessing import Pool
from datetime import timedelta
from tornado import httpclient, gen, ioloop, queues


class AsySpider(object):
    """A simple class of asynchronous spider."""

    def __init__(self, urls, concurrency=10):
        urls.reverse()
        self.urls = urls
        self.concurrency = concurrency
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()

    def handle_page(self, url, html):  #网页处理
        filename = url.rsplit('/', 1)[1]
        with open(filename, 'w+') as f:
            f.write(html)

    @gen.coroutine
    def get_page(self, url):
        try:
            response = yield httpclient.AsyncHTTPClient().fetch(url)
            print('######fetched %s' % url)
        except Exception as e:
            print('Exception: %s %s' % (e, url))
            raise gen.Return('')
        raise gen.Return(response.body)

    @gen.coroutine
    def _run(self):

        @gen.coroutine
        def fetch_url():
            current_url = yield self._q.get()
            try:
                if current_url in self._fetching:
                    return

                print('fetching****** %s' % current_url)
                self._fetching.add(current_url)
                html = yield self.get_page(current_url)
                self._fetched.add(current_url)

                self.handle_page(current_url, html)

                for i in range(self.concurrency):
                    if self.urls:
                        yield self._q.put(self.urls.pop())

            finally:
                self._q.task_done()

        @gen.coroutine
        def worker():
            while True:
                yield fetch_url()

        self._q.put(self.urls.pop())

        # Start workers, then wait for the work queue to be empty.
        for _ in range(self.concurrency):
            worker()
        yield self._q.join(timeout=timedelta(seconds=300000))
        assert self._fetching == self._fetched

    def run(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)


class MySpider(AsySpider):
    def fetch(self, url, **kwargs):
        """重写父类fetch方法可以添加cookies，headers，timeout等信息"""
        cookies_str = "_wconn=-1; UM_distinctid=15f4d39ecd01120-08751f1f87ac3e-31657c00-13c680-15f4d39ecd1e53; HDid=1508829162821; BDTUJIAID=e3b72f976bc19487a3bc77713aff749c; bdshare_firstime=1508829163555; PHPSESSID=39lfbtssbl7c6tr2jrnufdv5h5; _gat=1; CNZZDATA1257055259=1778847916-1508825645-null%7C1509101092; _ga=GA1.2.1755293101.1508829163; _gid=GA1.2.809543324.1508939574; Hm_lvt_06a54a6e8150679f4839ee359171f563=1508829163,1508939574; Hm_lpvt_06a54a6e8150679f4839ee359171f563=1509105422; haodou-bi=r=http%3A%2F%2Fwww.haodou.com%2Frecipe%2F&ul=1509105422287&hd=1509105422299"  # 从浏览器拷贝cookie字符串
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
            'cookie': cookies_str
        }
        return super(MySpider, self).fetch(  # 参数参考tornado文档
            url, headers=headers, request_timeout=1
        )

    def handle_html(self, url, html):
        print(url, html)

def run_spider(beg, end):
    urls = []
    for page in range(beg, end):
        urls.append('http://127.0.0.1/%s.htm' % page) #url池
    s = MySpider(urls)#并发数
    s.run()


def main():
    _st = time.time()
    # dish_load
    dic_save = {}
    for i in range(11):
        file_name = 'changed_dic_save_dish' + str(i) + '.txt'
        with open(file_name, 'r') as f:
            dic_save[i] = json.load(f)
            # dic_save have all the information
    dish_category_list = dic_save[6].keys()
    all_dish = dic_save[6]
    p = Pool()
    all_num = len(all_dish)
    num = 4  # number of cpu cores
    per_num, left = divmod(all_num, num)
    s = range(0, all_num, per_num)
    res = []
    for i in range(len(s) - 1):
        res.append((s[i], s[i + 1]))
    res.append((s[len(s) - 1], all_num))
    print(res) #分每个core的任务数

    for i in res:
        p.apply_async(run_spider, args=(i[0], i[1],))
    p.close()
    p.join()

    print(time.time() - _st)


if __name__ == '__main__':
    main()