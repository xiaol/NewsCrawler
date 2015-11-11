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
from Extractors.Parse_jiecao import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue
from Reqs import redisclient

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderJiecao(Spider):

    name = 'content_spider_jiecao'
    qname = 'jiecao:content'
    r = redisclient.from_settings()

    # start_urls = [
    #     'http://news.jiecao.fm/client/article/detail.htm?v=2.6.2&id=me2rXWeL&down=true',
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
        item['tags'] = Parser.get_tag(root) or ''
        item['source'] = 'jiecao'
        item['source_url'] = response.url
        item['author'] = Parser.get_author(root) or ''
        item['update_time'] = Parser.get_date(root) or ''
        item['content'] = Parser.get_content(item['url'], root) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item