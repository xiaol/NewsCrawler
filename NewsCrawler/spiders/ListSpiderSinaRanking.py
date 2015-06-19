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


class ListSpiderSinaRanking(Spider):

    name = 'list_spider_sina_ranking'
    qname = 'sina_ranking'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 新浪排行：
    # 国内：http://pro.sina.cn/?sa=d1t240v2158&vt=4&channel=news&col=china
    # 社会：http://pro.sina.cn/?sa=d1t240v2158&vt=4&channel=news&col=society
    # start_urls = [
    #     'http://pro.sina.cn/?sa=d1t240v2158&vt=4&channel=news&col=china',
    #     'http://pro.sina.cn/?sa=d1t240v2158&vt=4&channel=news&col=society',
    #     ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ListItem()

        source = Cleaners.clean(response.body)
        # print source
        root = soup.fromstring(source)

        xp = '//a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            if url.endswith('vt=4') and url.startswith('http://news'):
                uris_titles[url] = ''

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item