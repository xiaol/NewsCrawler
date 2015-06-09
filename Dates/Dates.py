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
    def today(cls, formater='%Y-%m-%d'):
        return cls.date.strftime(formater)

    @classmethod
    def reledate_by_day(cls, day, formater='%Y-%m-%d'):
        return (datetime.date.today() + datetime.timedelta(days=day)).strftime(formater)

    @classmethod
    def time(cls, formater='%Y-%m-%d %X'):
        return time.strftime(formater, time.localtime())

    @classmethod
    def reletime_by_sec(cls, sec, formater='%Y-%m-%d %X'):
        return time.strftime(formater, time.localtime(time.time() + int(sec)))

    @classmethod
    def rangtime(cls, formater='%Y-%m-%d %X'):
        return time.strftime(formater, time.localtime(time.time() + random.randint(60, 6000)))
