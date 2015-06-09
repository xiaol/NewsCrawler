# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/8
"""

import random
import requests
from Agents.Agents import Agents


class Reqs(object):

    @staticmethod
    def req(url, agent):
        timeout = 10
        headers = {
            'User-Agent': agent,
        }

        for i in range(3):
            try:
                r = requests.get(url, headers=headers, timeout=timeout)
                if r.status_code == 200:
                    return r
                else:
                    print r.status_code
            except Exception, e:
                print 'Requests err: ', e
                pass
        return None

    @classmethod
    def mobile_req(cls, url):
        agent = random.choice(Agents.mobile)
        r = cls.req(url, agent)
        return r if r else None

    @classmethod
    def pc_req(cls, url):
        agent = random.choice(Agents.web)
        r = cls.req(url, agent)
        return r if r else None

