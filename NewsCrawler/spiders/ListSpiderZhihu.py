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
import simplejson as json
from Reqs import redisclient

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderZhihu(Spider):

    name = 'list_spider_zhihu'
    qname = 'zhihu'
    r = redisclient.from_settings()

    # 知乎专栏-影评：
    # start_urls = [
    #     'http://zhuanlan.zhihu.com/api/columns/zhimovie/posts?limit=10&offset=0',
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

        try:
            res = json.loads(source)
        except TypeError:
            return

        uris_titles = defaultdict(str)
        for r in res:
            title = r.get('title')
            url = r.get('href')
            if url and title:
                if not url.startswith('http'):
                    url = ''.join(['http://zhuanlan.zhihu.com', url])
                uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
