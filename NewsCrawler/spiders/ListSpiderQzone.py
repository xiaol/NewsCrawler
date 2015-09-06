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
import urlparse
import simplejson as json
from scrapy.spiders import Spider
from collections import defaultdict
from lxml.html import soupparser as soup
from Cleaners.Cleaners import Cleaners
from Cleaners.Encoding import encode_value
from Extractors.Extractor import Extractor
from Reqs.Popqueue import Popqueue
from NewsCrawler.items import ListItem

import random
from Agents.Agents import Agents
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

reload(sys)
sys.setdefaultencoding('utf-8')


class ListSpiderQzone(Spider):

    name = 'list_spider_qzone'
    qname = 'qzone'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)

    # qzone：
    # 我们都爱内涵图：http://user.qzone.qq.com/822989010/
    # 娱乐没有圈：http://user.qzone.qq.com/563206360/
    # 奇葩会：http://user.qzone.qq.com/2809679718/
    # 网上这点事：http://user.qzone.qq.com/563206360/
    # 男人这点事：http://user.qzone.qq.com/732952656/
    # start_urls = [
    #     'http://user.qzone.qq.com/p/b1/cgi-bin/blognew/get_abs?'
    #     'hostUin=732952656&blogType=0&cateName=&cateHex=&statYear='
    #     '&reqInfo=1&pos=0&num=15&sortType=0&absType=0&source=0&'
    #     'rand=0.8373222181107849&ref=qzone&g_tk=2132350819&verbose=0'
    #     '&iNotice=0&inCharset=utf8&outCharset=utf8&format=jsonp',
    #     ]

    def start_requests(self):
        # formate start_urls from redis pop
        while 1:
            yield self.make_requests_from_url(
                Popqueue.rpop(self.r, self.qname)
            )

    def parse(self, response):
        item = ListItem()
        blog_url = 'http://user.qzone.qq.com/HostId/blog/BlogId'
        # blog_url = 'http://m.qzone.com/details?ticket=&stat=&srctype=10&g_f=2000000209&res_uin=HostId' \
        #           '&appid=2&cellid=BlogId&no_topbar=1&subid=&g_ut=3'
        uris_titles = defaultdict(str)

        source = encode_value(response)                 # decode gb18030
        source = source.replace('<html><body><p>_Callback(', '').replace(');</p></body></html>', '')

        parurl = urlparse.urlparse(response.url)
        parm = urlparse.parse_qs(parurl.query, True)
        host_id = parm.get('hostUin')
        if not len(host_id):
            yield item
        host_id = host_id[0]

        try:
            source = json.loads(source)
            logs = source.get('data')['list']
            if not logs:
                yield item
            for log in logs:
                title = log.get('title')
                url = log.get('blogId')
                if url and title:
                    url = blog_url.replace('HostId', host_id).replace('BlogId', str(url))
                    uris_titles[url] = title
        except Exception, e:
            print e
            pass

        for k, v in uris_titles.iteritems():
            print k, v

        item['start_url'] = response.url
        item['urls'] = uris_titles

        yield item