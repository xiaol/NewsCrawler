# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/19
"""

import sys
import redis
from scrapy.spiders import Spider
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Parse_sohu import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderSohuSpecial(Spider):

    name = 'content_spider_sohu_special'
    qname = 'sohu_special:content'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # start_urls = [
    #     'http://m.sohu.com/n/413811116/',
    # ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ContItem()

        source = Cleaners.clean(response.body)
        root = soup.fromstring(source)

        item['url'] = response.url
        item['title'] = Parser.get_title(root) or ''
        item['tags'] = Parser.get_tag(root) or ''
        item['source'] = 'sohu'
        item['source_url'] = response.url
        item['author'] = ''
        item['update_time'] = Parser.get_date(root) or ''
        item['content'] = Parser.get_content(item['url'], root) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item