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
import random
from Agents.Agents import Agents
from scrapy.spider import Spider
from lxml.html import soupparser as soup
from Cleaners.Encoding import encode_value
from Cleaners.Cleaners import Cleaners
from Extractors.Parse_qzone import Parser
from NewsCrawler.items import ContItem
from Reqs.Popqueue import Popqueue
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# reload(sys)
# sys.setdefaultencoding('utf-8')


class ContentSpiderQzone(Spider):

    name = 'content_spider_qzone'
    qname = 'qzone:content'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # start_urls = [
    #     'http://user.qzone.qq.com/732952656/blog/1434680472',
    # ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    @staticmethod
    def get_source(url):
        # choice phantomjs with path.
        agent = random.choice(Agents.mobile)
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            agent
        )
        driver = webdriver.PhantomJS(service_args=['--load-images=no'], desired_capabilities=dcap)
        driver.implicitly_wait(10)
        driver.get(url)
        source = driver.page_source
        driver.close()
        return source

    def parse(self, response):
        item = ContItem()

        source = self.get_source(response.url)
        root = soup.fromstring(source)

        item['url'] = response.url
        item['title'] = Parser.get_title(root) or ''
        item['tags'] = Parser.get_tag(root) or ''
        item['source'] = Parser.get_origin(root) or 'qzone'
        item['source_url'] = response.url
        item['author'] = Parser.get_author(root) or ''
        item['update_time'] = Parser.get_date(root) or ''
        item['content'] = Parser.get_content(item['url'], root) or []
        item['imgnum'] = Parser.get_imgnum(item['content']) if item['content'] else 0

        yield item