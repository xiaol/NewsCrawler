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


class ListSpiderJandan(Spider):

    name = 'list_spider_jandan'
    qname = 'jandan'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 煎蛋网：
    # 重口味：http://i.jandan.net/tag/%E9%87%8D%E5%8F%A3%E5%91%B3
    # 笨贼：http://i.jandan.net/tag/%E7%AC%A8%E8%B4%BC
    # 大丈夫：http://i.jandan.net/tag/%E5%A4%A7%E4%B8%88%E5%A4%AB
    # tech：http://i.jandan.net/tag/tech
    # 创意产品：http://i.jandan.net/tag/%E5%88%9B%E6%84%8F%E4%BA%A7%E5%93%81
    # 走进科学：http://i.jandan.net/tag/%E8%B5%B0%E8%BF%9B%E7%A7%91%E5%AD%A6
    # start_urls = [
    #     'http://i.jandan.net/tag/%E9%87%8D%E5%8F%A3%E5%91%B3',
    #     'http://i.jandan.net/tag/%E7%AC%A8%E8%B4%BC',
    #     'http://i.jandan.net/tag/%E5%A4%A7%E4%B8%88%E5%A4%AB',
    #     'http://i.jandan.net/tag/tech',
    #     'http://i.jandan.net/tag/%E5%88%9B%E6%84%8F%E4%BA%A7%E5%93%81',
    #     'http://i.jandan.net/tag/%E8%B5%B0%E8%BF%9B%E7%A7%91%E5%AD%A6',
    # ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ListItem()

        source = response.body
        root = soup.fromstring(source)

        xp = '//*[@class="post"]/div/div[2]/h2/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            uris_titles[url] = title
        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
