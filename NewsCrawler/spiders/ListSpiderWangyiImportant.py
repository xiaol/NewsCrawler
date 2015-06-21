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
from bs4 import BeautifulSoup
import simplejson as json
from scrapy.spider import Spider
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Cleaners.Encoding import encode_value
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderWangyiImportant(Spider):

    name = 'list_spider_wangyi_important'
    qname = 'wangyi_important'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # 网易新闻要闻：http://news.163.com/mobile/
    # 网易新闻社会(API)：http://3g.163.com/touch/article/list/9ARM0ILIbjwangjian/0-10.html
    # start_urls = [
    #     'http://news.163.com/mobile/',
    #     'http://3g.163.com/touch/article/list/9ARM0ILIbjwangjian/0-16.html'
    #     ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ListItem()

        # encoding = response.encoding
        # soup = BeautifulSoup(response.body, "lxml", from_encoding=encoding)
        # source = str(soup)
        source = Cleaners.clean(response.body)
        # print source
        root = soup.fromstring(source)
        uris_titles = defaultdict(str)

        # 网易新闻社会(API)
        if '9ARM0ILIbjwangjian' in response.url:
            source = str(response.body).replace('<html>', '').replace('</html>', '')
            source = source.replace('artiList(', '').replace('}]})', '}]}')
            try:
                source = json.loads(source)
                source = source.get('9ARM0ILIbjwangjian')
                if source:
                    for page in source:
                        url = page.get('url')
                        title = page.get('title')
                        if title and url:
                            uris_titles[url] = title
            except Exception:
                pass
        # 网易新闻要闻
        else:
            xp = '//*[@class="ns-wnews ns-mb40"]/ul/li/h4/a'
            urls = Extractor.get_list(root, xp)
            for it in urls:
                url = it[1]
                title = it[0]
                if url.startswith('http://news.163.com') and url.endswith('html'):
                    uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item