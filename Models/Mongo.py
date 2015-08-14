# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/10
"""

import os
import sys
import time
import redis
import random
import pymongo
from collections import defaultdict
from pymongo.read_preferences import ReadPreference

reload(sys)
sys.setdefaultencoding('utf8')


class Mongo(object):

    def __init__(self, colle, db='news_ver2'):
        self.conn = pymongo.MongoReplicaSetClient("h44:27017, h213:27017, h241:27017",
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

    start_url = 'http://toutiao.com/m3678008825/'
    start_title = '今日头条-吴静儿囧事播报'
    channel = '重口味'
    channel_id = '2'
    frequency = '15'
    status = '1'
    qname = 'jinritoutiao'

    setup = {
        'start_url': start_url,             # 抓取起始网址
        'start_title': start_title,         # 抓取起始站名
        'channel': channel,                 # 所属频道名
        'channel_id': channel_id,           # 所属频道ID
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
        items[tb['start_url']]['channel_id'] = tb['channel_id']
    # print items
    for k, v in items.iteritems():
        print k, v

    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    r.hmset('spider_setup', dict(items))

    spider = r.hget('spider_setup', 'http://m.sohu.com/c/518/')
    print type(spider)
    print type(eval(spider))


def query_news_by_setup():
    spider_setup = Mongo('SpiderSetup')
    table_setup = spider_setup.table

    news_items = Mongo('NewsItems')
    table_news = news_items.table

    for tb in table_setup.find():
        start_url = tb['start_url']
        news_list = table_news.find({'start_url': start_url}).sort('create_time', pymongo.DESCENDING).limit(50)

        for news in news_list:
            url = news['url']
            create_time = news['create_time']
            imgnum = news['imgnum']
            channel_id = news['channel_id']
            start_url = news['start_url']
            start_title = news['start_title']
            channel = news['channel']
            content = []

            contents = news['content']
            for cont in contents:
                item = cont.values()[0]

                txt = item.get('txt')
                if txt:
                    txt = '<p>' + txt + '</p>'
                    content.append(txt)
                    continue

                img = item.get('img')
                if img:
                    img = '<p><img src="'+img+"\" onerror=\"javascript:errorimg.call(this);\" class=\"lazy\"></p>"
                    content.append(img)
                    continue

                img_info = item.get('img_info')
                if img_info:
                    txt = '<p>' + img_info + '</p>'
                    content.append(txt)
                    continue

            html_source = [
                ''.join(['<h2><a href=\"', url, '\">', url, '</a></h2>']),
                ''.join(['<h2>' + 'create_time:' + str(create_time) + '</h2>']),
                ''.join(['<h2>' + 'imgnum:' + str(imgnum) + '</h2>']),
                ''.join(['<h2>' + 'channel_id:' + str(channel_id) + '</h2>']),
                ''.join(['<h2>' + 'start_url:' + str(start_url) + '</h2>']),
                ''.join(['<h2>' + 'start_title:' + start_title + '</h2>']),
                ''.join(['<h2>' + 'channel:' + channel + '</h2>']),
            ]
            html_source += content
            html_source = '\n'.join(html_source)

            path = os.getcwd()
            start_path = '/'.join([path, start_title]) + '/'
            if not os.path.isdir(start_path):
                os.mkdir(start_path)
            html_name = ''.join([start_path, ''.join([str(int(time.time())), str(random.randint(1111, 9999))]), '.html'])
            try:
                f = open(html_name, 'w+')
                f.write(html_source)
                f.close()
                print url + ' success!'
            except:
                print url + ' faield!'
                continue

def initializeRedisForDuplicate():
    spider_setup = Mongo('SpiderSetup')
    table_setup = spider_setup.table

    news_items = Mongo('NewsItems')
    table_news = news_items.table

    for tb in table_setup.find():
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=pool)
        start_url = tb['start_url']
        news_list = table_news.find({'start_url': start_url}).sort('create_time', pymongo.DESCENDING).limit(50)
        for news in news_list:
            url = news['url']
            r.hset(url, 'flag', "1")
            print "Set %s flag to 1." % url
            time.sleep(0.5)


if __name__ == '__main__':
    # insert_spider_setup()
    # update_spider_setup()
    # update_spider_setup_to_redis()

    # query_news_by_setup()

    initializeRedisForDuplicate()
