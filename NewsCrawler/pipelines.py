# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import redis
from collections import defaultdict
from redis.exceptions import ConnectionError
from Models.Mongo import Mongo

from scrapy.exceptions import DropItem
from Dates.Dates import Dates


class ListPipeline(object):
    """
    Process the items from list spiders.
    Init each url with info get from setup-table to redis.
    """

    def __init__(self):
        self.pool = redis.ConnectionPool(host='localhost', port=6379)
        self.r = redis.Redis(connection_pool=self.pool)

    def get_info_by_start_url(self, start_url):
        try:
            info = self.r.hget('spider_setup', start_url)
        except ConnectionError:
            info = None
        return eval(info) if info else None

    def process_item(self, item, spider):
        if 'list_spider' not in spider.name:                    # Pipeline just for list spider
            return item
        urls = item['urls']                                     # Dict: { url: title, }
        start_url = item['start_url']

        info = self.get_info_by_start_url(start_url)
        if not info:
            raise DropItem("Drop item No setup info with url is %s" % start_url)

        dt = Dates.today()
        crawlat = ':'.join(['crawlat', dt])                     # Counts of websites crawled by day.

        timeout = int(time.time())+60*60*24*2                   # Keep the url for 2 days
        q_name = ':'.join([info['qname'], 'content'])             # Push to content spider

        for url, title in urls.iteritems():                     # Foreach url, title
            if not url:
                continue
            print 'get url:', url

            flag = self.r.hget(url, 'flag')
            if flag is None:
                info['title'] = title
                info['flag'] = 0
                self.r.hmset(url, info)
                self.r.expireat(url, timeout)
                self.r.lpush(q_name, url)
                self.r.lpush(crawlat, url)
                print 'Pipeline lpush %s:%s' % (q_name, url)
            elif int(flag) == 0:
                # Do something else like crawl again.
                pass
            else:
                print "This url is already exists with flag is %s." % flag

        return item


class ContentPipeline(object):
    """
    Process the items from content spiders.
    Save the content with info to mongodb or crawl again.
    """

    def __init__(self):
        self.pool = redis.ConnectionPool(host='localhost', port=6379)
        self.r = redis.Redis(connection_pool=self.pool)

    def process_item(self, item, spider):
        if 'content_spider' not in spider.name:
            return item
        url = item['url']

        # Check the control Flag from redis with url,
        # if url.flag != 0(means crawled before or have not init in list spider), Drop item.
        # if no content, Drop item.
        try:
            flag, title, start_url, start_title, channel = \
                self.r.hmget(url, 'flag', 'title', 'start_url', 'start_title', 'channel')
            if flag != '0':
                raise DropItem("Drop item with the control is %s!" % flag)
            if not item['content']:
                raise DropItem("Drop item with the No content!")
        except ConnectionError, e:
            raise DropItem("Drop item with the Redis err: %s" % e)

        table = defaultdict()
        # info from spider setup
        table['title'] = title or item['title']
        table['start_url'] = start_url
        table['start_title'] = start_title
        table['channel'] = channel

        # info from content spider
        table['url'] = url
        table['tags'] = item['tags']
        table['source'] = item['source']
        table['source_url'] = item['source_url']
        table['author'] = item['author']
        table['update_time'] = item['update_time'] or Dates.time()
        table['imgnum'] = item['imgnum']
        table['content'] = item['content']

        try:
            news_items = Mongo('NewsItems')
            db = news_items.table
            db.insert(table)
        except Exception, e:
            raise DropItem("Drop item with Insert NewsItems err: ", e)

        return item