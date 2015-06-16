# -*- coding: utf-8 -*-

"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/12
"""

import sys
sys.path.insert(0, "..")
sys.path.append("/work/pro/NewsCrawler/")


import time
import redis
import gevent
from Mail import send_mail
from Dates.Dates import Dates
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
        minit = 60
        r = cls.redis_setup()
        gevent.sleep(int(pri)*minit)
        print '*'*60
        print 'Total: ', len(url_q_s)
        for url_q in url_q_s:
            q_name = url_q[1]
            url = url_q[0]
            print "Task at %s-->%s-->%s" % (pri, q_name, url)
            r.lpush(q_name, url)


class Status(object):

    @classmethod
    def redis_setup(cls):
        print 'Setup Redis!'
        pool = redis.ConnectionPool(host='localhost', port=6379)
        r = redis.Redis(connection_pool=pool)
        return r

    @classmethod
    def get_qlen_by_qname(cls):
        q_name_length = defaultdict(str)
        r = cls.redis_setup()
        tb_setup = InitSetup.get_setupid()
        if not tb_setup:
            return
        q_name_set = set()
        for item in tb_setup:
            q_name = item['qname']
            q_name_set.add(q_name)
        for q in q_name_set:
            q_length = r.llen(q)
            q_name_length[q] = str(q_length)
            q_cont = ':'.join([q, 'content'])
            q_cont_length = r.llen(q_cont)
            q_name_length[q_cont] = str(q_cont_length)
        dt = Dates.today()
        crawlat = ':'.join(['crawlat', dt])
        q_name_length[crawlat] = r.llen(crawlat)
        dt_1 = Dates.reledate_by_day(-1)
        crawlat_1 = ':'.join(['crawlat', dt_1])
        q_name_length[crawlat_1] = r.llen(crawlat_1)
        return q_name_length

    @classmethod
    def get_status(cls):
        queue_status = cls.get_qlen_by_qname()
        # spider_status = cls.get_running_spiders()
        spider_status = {}
        statu = dict(spider_status, **queue_status)
        return statu


if __name__ == '__main__':

    flag = defaultdict(int)
    for i in range(8, 21):
        flag[str(i)] = 1

    row = 1
    while 1:
        print "At row: ", row
        h = str(time.localtime()[3])
        if h in flag.keys() and flag[h]:
            status = Status.get_status()
            send_mail(status)
            flag[h] = 0

        InitSetup.init_setup()
        row += 1
