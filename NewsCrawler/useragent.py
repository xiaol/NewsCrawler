# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/8
"""

import random
from scrapy import log
from Agents.Agents import Agents
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware


class RotateUserAgentMiddleware(UserAgentMiddleware):

    def process_request(self, request, spider):

        web_spiders = [
            'list_spider_sina_important',
            'list_spider_sohu_special',
            'list_spider_sina_special',
            'list_spider_qzone',
            'content_spider_qzone',
            'list_spider_ihuqu',
            'list_spider_moviesoon',
            ]
        if spider.name in web_spiders:
            ua = random.choice(Agents.web)
        else:
            ua = random.choice(Agents.mobile)
        if ua:
            print "********Current UserAgent:%s************" % ua

            log.msg('Current UserAgent: '+ua, level='INFO')
            request.headers.setdefault('User-Agent', ua)