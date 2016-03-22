# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/8
"""

import time
import random


class Popqueue(object):

    @classmethod
    def rpop(cls, r, qname):
        # pop url from setup url list from redis
        while 1:
            # set_up:url
            l = r.llen(qname)
            if l == 0:
                print 'Queue-->%s-->Wait' % qname
                time.sleep(random.randint(3, 15))
            else:
                rpop = r.rpop(qname)
                print 'Queue-->%s-->%s-->%s' % (qname, l, rpop)
                return rpop
