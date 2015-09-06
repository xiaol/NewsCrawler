# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/16
"""
import simplejson as json
import sys
import time
import redis
from Reqs.Reqs import Reqs
from scrapy.spiders import Spider
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Extractors.Parse_hqiu import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue

reload(sys)
sys.setdefaultencoding('utf-8')


class ContentSpiderHuanqiuImportant(Spider):

    name = 'content_spider_huanqiu_important'
    qname = 'huanqiu_important:content'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # start_urls = [
    #     # 'http://m.huanqiu.com/view.html?id=1566988&v=9',    # image page
    #     'http://m.huanqiu.com/view.html?id=2081757&v=9',    # common page
    # ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    @staticmethod
    def get_contents_by_api(url):
        contents = []
        api = 'http://m.huanqiu.com/mtview.html?id=NewsID&page=PageN'
        try:
            news_id = url.split('id=')[-1].split('&')[0]
        except IndexError:
            return None
        page = 0
        while 1:
            page += 1
            url = api.replace('NewsID', news_id).replace('PageN', str(page))
            print url
            cont = Reqs.mobile_req(url)
            if cont:
                cont = cont.content
                try:
                    cont = json.loads(cont)
                    cont = cont[0]
                except TypeError:
                    break
                except IndexError:
                    break
                if cont not in contents:
                    contents.append(cont)
                else:
                    print 'End page.'
                    break
            else:
                break
        return contents

    def parse(self, response):
        item = ContItem()

        contents = self.get_contents_by_api(response.url)
        if not contents:
            yield item

        item['url'] = response.url
        item['title'] = contents[0].get('title', '')
        item['tags'] = contents[0].get('tag', '')
        item['source'] = contents[0].get('comefrom', '')
        item['source_url'] = response.url
        item['author'] = contents[0].get('author', '')
        item['update_time'] = ''
        item['content'] = Parser.get_content(contents, response.url) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item