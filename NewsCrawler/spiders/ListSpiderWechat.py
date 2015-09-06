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

import random
from Agents.Agents import Agents
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderWechat(Spider):

    name = 'list_spider_wechat'
    qname = 'wechat'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # wechat：
    # 我们爱讲冷笑话：http://weixin.sogou.com/gzh?openid=oIWsFt_60J20VTUbAEOviZNWlmcQ
    # 世界未解之谜：http://weixin.sogou.com/gzh?openid=oIWsFt6hzKBqCr8ox4VRqTw3__MY
    # 笑功震武林：http://weixin.sogou.com/gzh?openid=oIWsFt37E4GzclO_YlHOJfHHgkB4
    # 湿哒子：http://weixin.sogou.com/gzh?openid=oIWsFtx605C07Yp9yZ_Gsj4aW5pM
    # 关爱八卦成长协会：http://weixin.sogou.com/gzh?openid=oIWsFt-KvMdF3qA2Z62ZXqzQov00
    # 汪星人：http://weixin.sogou.com/gzh?openid=oIWsFt0_V_PJRVUHyM5-M96rOHSM
    # 萌宠：http://weixin.sogou.com/gzh?openid=oIWsFt8LUzcDNjsoLt6lcFnfAjXY
    # 大爱猫咪控：http://weixin.sogou.com/gzh?openid=oIWsFt4Dl6kREBsD_KrMA84ThiIA
    # 玩蛋：http://weixin.sogou.com/gzh?openid=oIWsFt72Ib6V1s3p0244uPg9nJQM
    # 单读：http://weixin.sogou.com/gzh?openid=oIWsFt-W8WxV7WDe0nnGz1SlLzwE
    # start_urls = [
    #     'http://weixin.sogou.com/gzh?openid=oIWsFt-W8WxV7WDe0nnGz1SlLzwE',
    #     ]

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
        item = ListItem()

        source = Cleaners.clean(self.get_source(response.url))
        root = soup.fromstring(source)

        xp = '//*[@id="wxbox"]/div/div/div[2]/h4/a'
        urls = Extractor.get_list(root, xp)
        uris_titles = defaultdict(str)
        for it in urls:
            url = it[1].replace('#rd', '')
            title = it[0]
            uris_titles[url] = title

        # for k, v in uris_titles.iteritems():
        #     print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item
