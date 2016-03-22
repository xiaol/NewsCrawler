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


class ListSpiderPeopleImportant(RedisSpider):

    name = 'list_spider_people_important'
    qname = 'people_important'
    # r = redisclient.from_settings()
    #
    # # 人民网要闻：http://www.people.com.cn/GB/59476/
    # # 人民网观点：http://opinion.people.com.cn/
    # # start_urls = [
    # #     'http://www.people.com.cn/GB/59476/',
    # #     'http://opinion.people.com.cn/',
    # #               ]
    #
    # def start_requests(self):
    #     # formate start_urls from redis pop
    #     while 1:
    #         yield self.make_requests_from_url(
    #             Popqueue.rpop(self.r, self.qname)
    #         )

    def parse(self, response):
        item = ListItem()

        # source = Cleaners.clean(response.body)
        source = response.body
        print source
        root = soup.fromstring(source)

        # for http://www.people.com.cn/GB/59476/
        xp = '//*[@class="p6"]/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1]
            title = it[0]
            uris_titles[url] = ''       # use the title from content spider.

        # for http://opinion.people.com.cn/
        if not uris_titles:
            xp_opinion = '//*[@class=" hdNews clearfix"]/p/strong/a'
            urls_opinion = Extractor.get_list(root, xp_opinion)
            for it in urls_opinion:
                url = it[1]
                if not url.startswith('http'):
                    url = ''.join(['http://opinion.people.com.cn', url])
                title = it[0]
                uris_titles[url] = ''       # use the title from content spider.

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item