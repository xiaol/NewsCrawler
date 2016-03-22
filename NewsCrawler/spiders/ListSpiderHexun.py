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
from ..spiders import RedisSpider
reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderHexun(RedisSpider):

    name = 'list_spider_hexun'
    qname = 'hexun'

    def parse(self, response):
        item = ListItem()

        source = encode_value(response)
        root = soup.fromstring(source)

        xp = '//*[@class="temp01"]/ul/li/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            if u"\u62db\u6807\u516c\u544a" in title:
                continue
            url = url.replace('http://news.hexun.com', 'http://m.hexun.com/news')
            uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
