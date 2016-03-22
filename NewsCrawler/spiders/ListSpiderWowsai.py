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
import simplejson as json
from scrapy.spiders import Spider
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem
from Reqs.Reqs import Reqs
from Reqs import redisclient
from ..spiders import RedisSpider
reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderWowsai(RedisSpider):

    name = 'list_spider_wowsai'
    qname = 'wowsai'
    # r = redisclient.from_settings()
    #
    # # 哇塞网：
    # # 最设计：http://www.wowsai.com/zixun/zuichuangyi.html
    # # 艺术界：http://www.wowsai.com/zixun/yishujie.html
    # # start_urls = [
    # #     'http://www.wowsai.com/zixun/zuichuangyi.html',
    # # ]
    #
    # def start_requests(self):
    #     # formate start_urls from redis pop
    #     while 1:
    #         yield self.make_requests_from_url(
    #             Popqueue.rpop(self.r, self.qname)
    #         )

    def parse(self, response):
        item = ListItem()

        if response.url.endswith('yishujie.html'):
            cate_id = 7                         # 艺术界
        else:
            cate_id = 2                         # 最设计

        params = {
            'app': 'zixun',
            'act': 'get_article',
            'page': '1',
            'cate_id': cate_id,
        }
        url = 'http://www.wowsai.com/index.php?'
        r = Reqs.pc_post(url, params, headers={})
        try:
            source = json.loads(r.content)
        except TypeError:
            return
        uris_titles = defaultdict(str)
        for i in source:
            news_id = '-'.join([i.get('blogid'), i.get('classid'), i.get('store_id')]) + '.html'
            url = ''.join(['http://www.wowsai.com/zixun/', news_id])
            title = i.get('subject', '')
            if news_id and title:
                uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
