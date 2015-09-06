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
from Extractors.Parse_yeeyan import Parser
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderYeeyan(Spider):

    name = 'list_spider_yeeyan'
    qname = 'yeeyan'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 译言每日精选-科学：
    # start_urls = [
    #     'http://select.yeeyan.org/lists/science',
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

        xp = '//*[@class="content"]/div/div/a'
        urls = Parser.get_list(root, xp)
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
