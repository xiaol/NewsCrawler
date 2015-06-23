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


class ListSpiderIfanr(Spider):

    name = 'list_spider_ifanr'
    qname = 'ifanr'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 爱范儿：API
    # start_urls = [
    #     'http://www.ifanr.com/api/v3.0/?action=latest&posts_per_page=10&post_type=news&excerpt_length=40'
    #     '&thumb_size=680xauto&page=1&offset=0&cancel_cache=false&add_dasheng_fields=true&'
    #     'appkey=k0umfuztmirn5v73z3ij&timestamp=1435052619&sign=a0cd435e70efacb3eab60c7571fdee04&_=1435052626335',
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
            data = json.loads(source)
            data = data.get('data')
        except TypeError:
            return

        uris_titles = defaultdict(str)
        for it in data:
            url = it.get('link')
            title = it.get('title')
            if url and title:
                uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
