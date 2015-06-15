# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/15
"""

import sys
sys.path.insert(0, "..")
sys.path.append("/work/pro/NewsCrawler/")

import redis
from collections import defaultdict
from InitSetup import InitSetup
from Dates.Dates import Dates


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
    # print Status.get_qlen_by_qname()
    status = Status.get_status()
    for k, v in status.iteritems():
        print k, '------>', v