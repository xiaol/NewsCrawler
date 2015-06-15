# -*- coding: utf-8 -*-

"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/12
"""

import sys
sys.path.append("..")

import time
import redis
import gevent
from Mail import send_mail
from Status import Status
from Models.Mongo import Mongo
from collections import defaultdict
from redis.exceptions import ConnectionError


class InitSetup(object):

    @classmethod
    def redis_setup(cls):
        pool = redis.ConnectionPool(host='localhost', port=6379)
        r = redis.Redis(connection_pool=pool)
        return r

    @classmethod
    def update_spider_setup_to_redis(cls, items):
        try:
            r = cls.redis_setup()
            r.hmset('spider_setup', dict(items))
            print 'Update all spider tasks!'
        except ConnectionError:
            return None

    @classmethod
    def get_setupid(cls):
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

        # Update all spider to redis.
        cls.update_spider_setup_to_redis(items)

        # Filter the spider with status == 1.
        tasks = []
        for k, v in items.iteritems():
            if v.get('status') != '1':
                continue
            tasks.append(v)
        return tasks

    @classmethod
    def init_setup(cls):
        tasks = cls.get_setupid()
        if not tasks:
            return

        prod = {}
        for item in tasks:
            url = item['start_url']
            grab_time = item['frequency']
            q_name = item['qname']
            if grab_time in prod.keys():
                url_q = (url, q_name)
                prod[grab_time].append(url_q)
            else:
                prod[grab_time] = []
                url_q = (url, q_name)
                prod[grab_time].append(url_q)
        print prod
        max_times = []
        for key in prod.keys():
            max_times.append(int(key))
        max_time = max(max_times)
        res = {}
        for t in max_times:
            times = max_time/t
            for i in range(1, times+1):
                if str(t*i) in res.keys():
                    for item in prod[str(t)]:
                        res[str(t*i)].append(item)
                else:
                    res[str(t*i)] = []
                    for item in prod[str(t)]:
                        res[str(t*i)].append(item)

        threads = []
        for key, value in res.iteritems():
            print key, value
            threads.append(gevent.spawn(cls.task_queue, key, value))
        gevent.joinall(threads)

    @classmethod
    def task_queue(cls, pri, url_q_s):
        minit = 10
        r = cls.redis_setup()
        gevent.sleep(int(pri)*minit)
        print '*'*60
        print 'Total: ', len(url_q_s)
        for url_q in url_q_s:
            q_name = url_q[1]
            url = url_q[0]
            print "Task at %s-->%s-->%s" % (pri, q_name, url)
            r.lpush(q_name, url)


if __name__ == '__main__':

    flag = defaultdict(int)
    for i in range(8, 20):
        flag[str(i)] = 1

    row = 1
    while 1:
        print "At row: ", row
        h = time.localtime()[3]
        if h in flag.keys() and flag[h]:
            status = Status.get_status()
            send_mail(status)
            flag[h] = 0

        InitSetup.init_setup()
        row += 1