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
from scrapy.spider import Spider
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Cleaners.Encoding import encode_value
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem
from Cleaners.Encoding import encode_value

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderIhuqu(Spider):

    name = 'list_spider_ihuqu'
    qname = 'ihuqu'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 爱虎趣-萌宠：http://www.ihuqu.com/animals/
    # start_urls = [
    #     'http://www.ihuqu.com/animals/',
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

        xp = '//*[@class="pageList"]/dl/dd/h2/a'
        urls = Extractor.get_list(root, xp)

        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            if url and title:
                uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
