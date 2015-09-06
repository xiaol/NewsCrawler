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
import scrapy
from scrapy.spiders import Spider
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Cleaners.Encoding import encode_value
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem, SpecialItem

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderSohuSpecial(Spider):

    name = 'list_spider_sohu_special'
    qname = 'sohu_special'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 搜狐专题：http://news.sohu.com/special.shtml
    # start_urls = ['http://news.sohu.com/special.shtml',
    #               ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = SpecialItem()                        # special item

        source = Cleaners.clean(response.body)
        root = soup.fromstring(source)

        xp = '//*[@class="article-list"]/div/h3/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            uris_titles[url] = title

        for k, v in uris_titles.iteritems():
            # print k, v
            yield scrapy.Request(k, callback=self.parse_item)

        item['special'] = True
        item['start_url'] = response.url            # This url is the start url from spider setup.
        item['urls'] = uris_titles

        yield item

    @staticmethod
    def parse_item(response):
        item = ListItem()                           # list item

        source = encode_value(response)
        root = soup.fromstring(source)

        xp = '//*[@class="article-list"]/div/h3/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]

            # convert web url to mobile url.
            try:
                news_id = url.split('/')[-1].split('.')[0]
                news_id = news_id.replace('n', '') if news_id.startswith('n') else None
            except:
                news_id = None
            if news_id:
                mob_url = ''.join(['http://m.sohu.com/n/', news_id, '/'])
                uris_titles[mob_url] = unicode(title)

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url            # This url is the special url.
        item['urls'] = uris_titles

        yield item
