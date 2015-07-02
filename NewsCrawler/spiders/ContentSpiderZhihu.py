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
from scrapy.spider import Spider
from lxml.html import soupparser as soup
from collections import defaultdict
from Cleaners.Cleaners import Cleaners
from Extractors.Parse_yxputao import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderZhihu(Spider):

    name = 'content_spider_zhihu'
    qname = 'zhihu:content'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # start_urls = [
    #     'http://zhuanlan.zhihu.com/api/columns/zhimovie/posts/20085804',
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

        try:
            source = json.loads(source)
        except TypeError:
            return

        item['url'] = response.url
        item['title'] = source.get('title', '')
        item['tags'] = ''
        item['source'] = 'zhihu.com'
        item['source_url'] = response.url
        item['author'] = ''
        item['update_time'] = source.get('publishedTime', '')
        item['content'] = self.cont_format(source.get('content', ''))
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item

    @staticmethod
    def cont_format(content):
        if not content:
            return ''
        root = soup.fromstring(content)
        contents = []
        dedupe = set()

        for child in root.iter():
            item = defaultdict(dict)
            print 'Tag', child.tag, 'ATTR', child.attrib

            # image frame
            if child.tag == 'img':
                img = child.get('src') or child.get('alt_src')
                if img and img not in dedupe:
                    item[str(len(contents))]['img'] = img
                    contents.append(item)
                    dedupe.add(img)
                continue

            # news content
            if child.tag == 'p':

                # content
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt and txt not in dedupe:
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                continue
        return contents or []