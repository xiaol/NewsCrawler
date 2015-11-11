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
from InitSetup import Status
import redis
from Reqs import redisclient

if __name__ == '__main__':
    # print Status.get_qlen_by_qname()
    status = Status.get_status()
    for k, v in status.iteritems():
        print k, '------>', v
    r = redisclient.from_settings()
    print 'related_spider',
    print r.llen('related_spider')
