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
from scrapy.spiders import Spider
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem
from Reqs import redisclient
from ..spiders import RedisSpider
reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderQianzhan(RedisSpider):

    name = 'list_spider_qianzhan'
    qname = 'qianzhan'
    # r = redisclient.from_settings()
    #
    # # 前瞻网-娱乐电视：
    # # start_urls = [
    # #     'http://xw.qianzhan.com/ent/list/325.html',
    # # ]
    #
    # def start_requests(self):
    #     # formate start_urls from redis pop
    #     while 1:
    #         yield self.make_requests_from_url(
    #             Popqueue.rpop(self.r, self.qname)
    #         )

    def parse(self, response):
        item = ListItem()

        source = response.body
        root = soup.fromstring(source)

        xp = '//*[@class="list list3"]/ul/li/p[2]/a'
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
