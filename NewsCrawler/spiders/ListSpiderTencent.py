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
from Cleaners.Encoding import encode_value
from Reqs import redisclient
from ..spiders import RedisSpider
reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderTencent(RedisSpider):

    name = 'list_spider_tencent'
    qname = 'tencent'
    # r = redisclient.from_settings()
    #
    # # 腾讯新闻:
    # # 社会：http://xw.qq.com/m/shehui/
    # # start_urls = [
    # #     'http://xw.qq.com/m/shehui/',
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

        xp = '//*[@class="list"]/ul/li/a'
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
