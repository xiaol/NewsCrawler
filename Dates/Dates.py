# -*- coding: utf-8 -*-
"""
    Project: NewsCrawler
    Purpose: Date string formatter.
    Version:
    Author:  ZG
    Date:    15/6/8
"""

import time
import random
import datetime


class Dates(object):

    date = datetime.date.today()

    @classmethod
    def today(cls):
        return cls.date.strftime('%Y-%m-%d')

    @classmethod
    def yesterday(cls):
        return (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    @classmethod
    def bfyesterday(cls):
        return (datetime.date.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

    @classmethod
    def time(cls):
        return time.strftime("%Y-%m-%d %X", time.localtime())

    @classmethod
    def reletime(cls):
        return time.strftime("%Y-%m-%d %X", time.localtime(time.time() + random.randint(60, 1000)))
