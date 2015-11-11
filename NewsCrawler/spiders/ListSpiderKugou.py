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
from Cleaners.Encoding import encode_value
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem
from Cleaners.Encoding import encode_value
from Reqs import redisclient

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderKugou(Spider):

    name = 'list_spider_kugou'
    qname = 'kugou'
    r = redisclient.from_settings()

    # 酷狗-音乐咨询：http://yule.kugou.com/alllist/
    # start_urls = [
    #     'http://yule.kugou.com/alllist/',
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

        xp = '//*[@class="newsListCon"]/ul/li/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            if url and not url.startswith('http'):
                url = ''.join(['http://yule.kugou.com', url])
            if url.endswith('html'):
                uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
