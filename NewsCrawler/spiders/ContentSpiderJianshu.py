# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/16
"""

import re
import sys
import redis
from scrapy.spiders import Spider
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Parse_jianshu import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue
from Reqs import redisclient

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderJianshu(Spider):

    name = 'content_spider_jianshu'
    qname = 'jianshu:content'
    r = redisclient.from_settings()

    # start_urls = [
    #     'http://www.jianshu.com/p/e51dcf98d3da',
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
        re_link = re.compile('<a[\s\S]+?>', re.I)
        source = re_link.sub('', source)
        root = soup.fromstring(source)

        item['url'] = response.url
        item['title'] = Parser.get_title(root) or ''
        item['tags'] = ''
        item['source'] = 'jianshu.com'
        item['source_url'] = response.url
        item['author'] = Parser.get_author(root) or ''
        item['update_time'] = Parser.get_date(root) or ''
        item['content'] = Parser.get_content(item['url'], root) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item