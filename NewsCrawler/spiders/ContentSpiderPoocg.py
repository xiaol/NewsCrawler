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
from Extractors.Parse_poocg import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue
from Reqs import redisclient
from ..spiders import RedisSpider
reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderPoocg(RedisSpider):

    name = 'content_spider_poocg'
    qname = 'poocg:content'

    def parse(self, response):
        item = ContItem()

        source = Cleaners.clean(response.body)
        root = soup.fromstring(source)

        item['url'] = response.url
        item['title'] = ''
        item['tags'] = Parser.get_tag(root) or ''
        item['source'] = 'poocg.com'
        item['source_url'] = response.url
        item['author'] = Parser.get_author(root) or ''
        item['update_time'] = ''
        item['content'] = Parser.get_content(item['url'], root) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item