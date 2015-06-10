# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/10
"""

import redis
import pymongo
from collections import defaultdict
from pymongo.read_preferences import ReadPreference


class Mongo(object):

    def __init__(self, colle, db='news_ver2'):
        self.conn = pymongo.MongoReplicaSetClient("121.41.49.44:27017, 121.41.75.213:27017, 121.41.112.241:27017",
                                                  replicaSet="myset",
                                                  read_preference=ReadPreference.SECONDARY)
        self.db = db
        self.colle = colle
        self.table = self.conn[self.db][self.colle]


def insert_spider_setup():
    """
    Insert a new table of spider setup.
    :return:
    """
    spider_setup = Mongo('SpiderSetup')
    db = spider_setup.table

    start_url = 'http://m.sohu.com/c/518/'
    start_title = '搜狐要闻-财经'
    channel = '头条焦点'
    # channel_id = ''
    frequency = '1'
    status = '1'
    qname = 'sohu_news_important'

    setup = {
        'start_url': start_url,             # 抓取起始网址
        'start_title': start_title,         # 抓取起始站名
        'channel': channel,                 # 所属频道名
        # 'channel_id': channel_id,          # 所属频道ID
        'frequency': frequency,             # 抓取频率/分钟
        'status': status,                   # 抓取状态/0=关闭、1=启动
        'qname': qname,                     # 消息名
    }

    insert_id = db.insert(setup)
    print 'insert_id: ', insert_id

    inserted = db.find_one({'_id': insert_id})
    print inserted

def update_spider_setup():
    """
    Change Staus of something else by start url.
    :return:
    """
    spider_setup = Mongo('SpiderSetup')
    db = spider_setup.table

    start_url = 'http://m.sohu.com/c/518/'
    setup = db.find_one({'start_url': start_url})
    print setup
    setup['status'] = '1'
    db.save(setup)

def update_spider_setup_to_redis():
    """
    If update the table of spider_setup, update to the redis.
    :return:
    """
    spider_setup = Mongo('SpiderSetup')
    db = spider_setup.table

    items = defaultdict(dict)

    for tb in db.find():
        items[tb['start_url']]['status'] = tb['status']
        items[tb['start_url']]['qname'] = tb['qname']
        items[tb['start_url']]['frequency'] = tb['frequency']
        items[tb['start_url']]['start_url'] = tb['start_url']
        items[tb['start_url']]['start_title'] = tb['start_title']
        items[tb['start_url']]['channel'] = tb['channel']
    # print items
    for k, v in items.iteritems():
        print k, v

    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    r.hmset('spider_setup', dict(items))

    spider = r.hget('spider_setup', 'http://m.sohu.com/c/518/')
    print type(spider)
    print type(eval(spider))


if __name__ == '__main__':
    # insert_spider_setup()
    # update_spider_setup()
    update_spider_setup_to_redis()