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

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderAlibuybuy(Spider):

    name = 'list_spider_alibuybuy'
    qname = 'alibuybuy'
    r = redisclient.from_settings()

    # 互联网那点事：
    # 推荐阅读：http://www.alibuybuy.com/posts/category/collection
    # start_urls = [
    #     'http://www.alibuybuy.com/posts/category/collection',
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

        xp = '//*[@class="content articles"]/div/h2/a'
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
