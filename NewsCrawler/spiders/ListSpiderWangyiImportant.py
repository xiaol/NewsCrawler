# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/16
"""

import sys
import redis
from scrapy.spider import Spider
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderWangyiImportant(Spider):

    name = 'list_spider_wangyi_important'
    qname = 'wangyi_important'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 网易新闻要闻：http://news.163.com/mobile/
    start_urls = ['http://news.163.com/mobile/',
                  ]

    # def start_requests(self):
    #     # formate start_urls from redis pop
    #     while 1:
    #         yield self.make_requests_from_url(
    #             Popqueue.rpop(self.r, self.qname)
    #         )

    def parse(self, response):
        item = ListItem()

        source = Cleaners.clean(response.body)
        root = soup.fromstring(source)

        xp = '//*[@class="ns-wnews ns-mb40"]/ul/li/h4/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            if url.startswith('http://news.163.com') and url.endswith('html'):
                uris_titles[url] = title

        for k, v in uris_titles.iteritems():
            print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item