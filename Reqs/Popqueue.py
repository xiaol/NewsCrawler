# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/8
"""

import time


class Popqueue(object):

    @classmethod
    def rpop(cls, r, qname):
        time.sleep(3)
        # pop url from setup url list from redis
        while 1:
            # set_up:url
            l = r.llen(qname)
            if l == 0:
                print 'Queue-->%s-->Wait' % qname
                time.sleep(5)
                return 'http://'
            rpop = r.rpop(qname)
            print 'Queue-->%s-->%s' % (qname, l)
            print 'Queue-->%s-->%s' % (qname, rpop)
            return rpop