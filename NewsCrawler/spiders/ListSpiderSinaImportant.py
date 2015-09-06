# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/16
"""

import sys
import json
import redis
from scrapy.spiders import Spider
from Reqs.Reqs import Reqs
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderSinaImportant(Spider):

    name = 'list_spider_sina_important'
    qname = 'sina_important'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 新浪新闻要闻：http://news.sina.com.cn/
    # start_urls = ['http://news.sina.com.cn/',
    #               ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    @staticmethod
    def api_urls(url):
        url = 'http://data.api.sina.cn/api/redirect/pc_to_wap.php?ref=' + url
        cont = Reqs.pc_req(url)
        if cont:
            try:
                return cont.url
            except ValueError:
                return None

    def parse(self, response):
        item = ListItem()

        source = Cleaners.clean(response.body)
        root = soup.fromstring(source)

        # Two parts of yaowen
        xp = '//*[@class="p_middle"]/div/div[2]/h1/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            uris_titles[url] = title

        xp = '//*[@class="p_middle"]/div/div[3]/ul/li/a'
        urls = Extractor.get_list(root, xp)
        for it in urls:
            url = it[1]
            title = it[0]
            uris_titles[url] = title

        # convert web url to mobile url
        result = defaultdict(str)
        for k, v in uris_titles.iteritems():
            url = self.api_urls(k)
            # filter for current url of mobile and news.
            if url and url.startswith('http://news') and 'from=wap' in url:
                result[url] = v
                print url, v

        item['start_url'] = response.url
        item['urls'] = result

        yield item