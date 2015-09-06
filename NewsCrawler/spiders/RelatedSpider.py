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
from Cleaners.Encoding import encode_value
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem
from Cleaners.Encoding import encode_value


from Process.Extractors import Extractor, Gist
from Process.RelatedTasks.Baike import Baike
from Process.RelatedTasks.Douban import Douban
from Process.RelatedTasks.Ner import Ner
from Process.RelatedTasks.Weibo import Weibo
from Process.RelatedTasks.Zhihu import Zhihu


reload(sys)
sys.setdefaultencoding('utf-8')


import gevent.monkey
gevent.monkey.patch_socket()

import gevent
from gevent import Greenlet

class RelatedSpider_(Spider):

    name = 'related_spider'
    qname = 'related_spider'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # start_urls = [
    #     'http://m.sohu.com/n/411416712/'
    # ]
    
    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ListItem()

        url = response.url
        items = defaultdict()

        #   1 keywords(auto tags)   title
        #   2 ne                    keywords
        #   3 abs                   content
        #   4 weibo                 title
        #   5 zhihu                 keywords
        #   6 baike                 ne (if ne)
        #   7 douban                ne

        title, content = self.r.hmget(url, ('title', 'content'))
        if not content or not title:
            return

        keywords = Extractor.extract_keywords(title)
        content = content.replace("defaultdict(<type 'dict'>, ", '').replace('}})', '}}')
        content = eval(content)
        content = [it.values()[0] for it in content]
        content = [it.values()[0] for it in content if it.keys()[0] == 'txt']
        content = '\n'.join(content)
        abstract = Gist().get_gist(content)
        ne = Ner.get_ner(keywords)

        threads = [
            Greenlet.spawn(Baike.get_baike, ne),
            Greenlet.spawn(Douban.get_douban, ne),
            Greenlet.spawn(Weibo.get_weibo, title),
            Greenlet.spawn(Zhihu.get_zhihu, keywords)
        ]
        gevent.joinall(threads)
        results = [thread.value for thread in threads]
        for it in results:
            if not it:
                continue
            items[it.keys()[0]] = it.values()[0]
        items['tags'] = ','.join(keywords) if keywords else None
        items['abstract'] = abstract if abstract else None
        items['ne'] = ne if ne else None

        item['start_url'] = url
        item['urls'] = items

        yield item

