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


class ListSpiderYxputao(RedisSpider):

    name = 'list_spider_yxputao'
    qname = 'yxputao'
    # r = redisclient.from_settings()
    #
    # # 游戏葡萄：
    # # 深度行业动态：
    # # 深度海外观察：
    # # start_urls = [
    # #     'http://youxiputao.com/article/index/id/13',
    # #     'http://youxiputao.com/article/index/id/17',
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

        xp = '//*[@class="news-list"]/li/div/div/h4/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            if not url.startswith('http'):
                url = ''.join(['http://youxiputao.com', url])
            uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
