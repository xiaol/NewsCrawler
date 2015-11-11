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
from Extractors.Parse_jinritoutiao import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue
from Reqs import redisclient

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderJinritoutiao(Spider):

    name = 'content_spider_jinritoutiao'
    qname = 'jinritoutiao:content'
    r = redisclient.from_settings()

    # start_urls = [
    #     'http://m.toutiao.com/a4370132852/',
    #     'http://m.toutiao.com/a4389294904/',
    # ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ContItem()

        source = response.body
        root = soup.fromstring(source)

        item['url'] = response.url
        item['title'] = Parser.get_title(root) or ''
        item['tags'] = ''
        item['source'] = 'toutiao.com'
        item['source_url'] = response.url
        item['author'] = ''
        item['update_time'] = Parser.get_date(root) or ''
        item['content'] = Parser.get_content_by_url(item['url']) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item