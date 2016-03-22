# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/9
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


class ListSpiderSohuNewsImportant(RedisSpider):

    name = 'list_spider_sohu_news_important'
    qname = 'sohu_news_important'
    # r = redisclient.from_settings()
    #
    # # 要闻：http://m.sohu.com/c/2/
    # # 国内排行：http://m.sohu.com/c/459/
    # # 国际排行：http://m.sohu.com/c/478/
    # # 社会排行：http://m.sohu.com/c/461/
    # # 体育排行：http://m.sohu.com/c/515/
    # # 娱乐排行：http://m.sohu.com/c/516/
    # # 财经排行：http://m.sohu.com/c/518/
    # # start_urls = [
    # #     # 'http://m.sohu.com/c/459/',
    # #     # 'http://m.sohu.com/c/478/',
    # #     # 'http://m.sohu.com/c/461/',
    # #     # 'http://m.sohu.com/c/515/',
    # #     # 'http://m.sohu.com/c/516/',
    # #     # 'http://m.sohu.com/c/518/',
    # #     ]
    #
    # def start_requests(self):
    #     # formate start_urls from redis pop
    #     while 1:
    #         yield self.make_requests_from_url(
    #             Popqueue.rpop(self.r, self.qname)
    #         )

    def parse(self, response):
        item = ListItem()

        source = Cleaners.clean(response.body)
        root = soup.fromstring(source)

        xp = '//*[@class="it"]/div/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = ''.join(['http://m.sohu.com', it[1]])
            title = it[0]
            uris_titles[url] = title
        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item