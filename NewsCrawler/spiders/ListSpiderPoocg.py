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
from Cleaners.Encoding import encode_value
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem
from Cleaners.Encoding import encode_value
from Extractors.Parse_poocg import Parser

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderPoocg(Spider):

    name = 'list_spider_poocg'
    qname = 'poocg'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 涂鸦王国：http://www.poocg.com/works/new
    # start_urls = [
    #     'http://www.poocg.com/works/new',
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

        xp = '//*[@class="TheWorks wrapper"]/div/ul/li/div[1]/a'
        urls = Extractor.get_list(root, xp)

        xp_t = '//*[@class="TheWorks wrapper"]/div/ul/li/p/span'
        tits = Parser.get_list(root, xp_t)

        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = tits[urls.index(it)]
            if not url.startswith('http'):
                url = ''.join(['http://www.pento.cn', url])
            if url and title:
                uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
