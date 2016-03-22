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
from Reqs.Reqs import Reqs
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


class ListSpiderSinaNews(RedisSpider):

    name = 'list_spider_sina_news'
    qname = 'sina_news'
    # r = redisclient.from_settings()

    # 新浪新闻：
    # 国内：http://news.sina.cn/gn?vt=4&pos=8
    # 社会：http://news.sina.cn/sh?vt=4&pos=8
    # 娱乐：http://ent.sina.cn/?vt=4&pos=108
    # 体育：http://sports.sina.cn/?vt=4&pos=108
    # 军事：http://mil.sina.cn/?vt=4&pos=108
    # 新浪财经：http://finance.sina.cn/roll.d.html?vt=4&cid=76478&rollCid=76478
    # start_urls = [
    #     'http://finance.sina.cn/roll.d.html?vt=4&cid=76478&rollCid=76478',
    #     ]

    # def start_requests(self):
    #     # formate start_urls from redis pop
    #     while 1:
    #         yield self.make_requests_from_url(
    #             Popqueue.rpop(self.r, self.qname)
    #         )

    def parse(self, response):
        item = ListItem()

        source = Cleaners.clean(response.body)
        # print source
        root = soup.fromstring(source)

        # This is a API get
        if response.url.startswith('http://feed'):
            urls = self.api_urls(response.url)
        else:
            xp = '//*[@id="j_items_list"]/div/a'
            urls = Extractor.get_list(root, xp)

        uris_titles = self.clean(urls)

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item

    @staticmethod
    def api_urls(url):
        urls = []
        cont = Reqs.mobile_req(url)
        if cont:
            try:
                cont = json.loads(cont.content)
                dt = cont['result']['data']
                for d in dt:
                    urls.append((d['title'], d['url']))
            except ValueError:
                pass
        return urls

    @staticmethod
    def clean(urls):
        uris_titles = defaultdict(str)
        for it in urls:
            try:
                title = it[0].split('\n')
                if len(title) > 1:
                    title = title[0]
                else:
                    title = it[0].split()[0]
                title = title.replace(u'\uff08\u56fe\uff09', '').strip()                    # u'(图)'
                title = title.replace(u'\u0028\u56fe\u0029', '').strip()                    # u'(高清)'
                title = title.replace(u'\u0028\u9ad8\u6e05\u0029', '').strip()              # u'(高清图集)'
                title = title.replace(u'\u0028\u9ad8\u6e05\u56fe\u96c6\u0029', '').strip()  # u'.图'
                title = title.replace(u'\u7ec4\u56fe\uff1a', '').strip()                    # u'组图：'
                title = title.replace(u'\u9ad8\u6e05\u56fe\uff1a', '').strip()              # u'高清图：'
                title = title.replace(u'\u0028\u7ec4\u56fe\u0029', '').strip()              # u'(组图)'
                title = title.replace(u'\u002e\u56fe', '').strip()
            except IndexError:
                title = ''
            uri = it[1]

            # if ('video' not in uri) and ('photo' not in uri):
            uris_titles[uri] = title
        return uris_titles
