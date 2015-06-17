# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/16
"""

import sys
import lxml
import redis
from scrapy.spider import Spider
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Parse_sina import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderSinaImportant(Spider):

    name = 'content_spider_sina_important'
    qname = 'sina_important:content'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # start_urls = [
    #     'http://news.sina.cn/gn/2015-06-17/detail-ifxczpzy2517767.d.html?vt=4&pos=8&cid=56261',
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

        # Tree convert by htmlparse for video
        tree = lxml.html.fromstring(source)

        item['url'] = response.url
        item['title'] = Parser.get_title(root) or ''
        item['tags'] = Parser.get_tag(root) or ''
        item['source'] = 'sina'
        item['source_url'] = response.url
        item['author'] = Parser.get_author(root) or ''
        item['update_time'] = Parser.get_date(root) or ''
        item['content'] = Parser.get_content(item['url'], root, tree) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item