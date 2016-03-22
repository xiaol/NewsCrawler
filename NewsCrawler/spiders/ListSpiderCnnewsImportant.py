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
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem
from Reqs import redisclient
from ..spiders import RedisSpider
reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderCnnewsImportant(RedisSpider):

    name = 'list_spider_cnnews_important'
    qname = 'cnnews_important'

    def parse(self, response):
        item = ListItem()

        source = Cleaners.clean(response.body)
        root = soup.fromstring(source)

        xp = '//*[@class="content_list"]/ul/li/div[2]/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            if not title:
                continue
            if not url.startswith('http'):
                continue
            if '.com.cn' not in url:
                url = ''.join(['http://www.chinanews.com/m', url.split('.com')[-1]])
            else:
                url = ''.join(['http://www.chinanews.com/m', url.split('.com.cn')[-1]])
            uris_titles[url.strip()] = ''       # use the title from content spider

        for k, v in uris_titles.iteritems():
            print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item