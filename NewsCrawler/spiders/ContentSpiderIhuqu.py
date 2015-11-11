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
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Cleaners.Encoding import encode_value
from Extractors.Parse_ihuqu import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue
from Reqs import redisclient

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderIhuqu(Spider):

    name = 'content_spider_ihuqu'
    qname = 'ihuqu:content'
    r = redisclient.from_settings()

    # start_urls = [
    #     'http://www.ihuqu.com/article/201501/639.html',
    # ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ContItem()

        source = encode_value(response)
        root = soup.fromstring(source)

        item['url'] = response.url
        item['title'] = Parser.get_title(root) or ''
        item['tags'] = Parser.get_tag(root) or ''
        item['source'] = 'ihuqu.com'
        item['source_url'] = response.url
        item['author'] = ''
        item['update_time'] = ''
        item['content'] = Parser.get_content(item['url'], root) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item