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
import simplejson as json
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


class ListSpiderTtpet(Spider):

    name = 'list_spider_ttpet'
    qname = 'ttpet'
    r = redisclient.from_settings()

    # 天天宠物网-新闻资讯：http://www.ttpet.com/zixun/39/category-catid-39.html
    # start_urls = [
    #     'http://www.ttpet.com/zixun/39/category-catid-39.html',
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

        xp = '//*[@class="p_pad"]/ul/dl/dd/a'
        urls = Extractor.get_list(root, xp)

        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]

            if not url.startswith('http'):
                url = ''.join(['http://m.ttpet.com/zixun/detail-', url.split('-')[-1]])
            if url and title:
                uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
