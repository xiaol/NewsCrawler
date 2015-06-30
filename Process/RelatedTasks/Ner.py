# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 命名实体分析
    Version:
    Author:  ZG
    Date:    15/6/29
"""

import re
import sys
import simplejson as json
from collections import defaultdict

from Reqs.Reqs import Reqs
from Process.RelatedTasks import filter_words

reload(sys)
sys.setdefaultencoding('utf8')


class Ner(object):

    @classmethod
    def get_ner(cls, keywords):
        tags = ' '.join(keywords)
        ne_host = '60.28.29.47'
        ne_api = "http://%s:8080/ner_mvc/api/ner?sentence=" % ne_host + tags
        ne = Reqs.pc_req(ne_api)
        if ne:
            ne = ne.content
            try:
                ne = json.loads(ne)
                if ne.get('error_code') == 0:
                    print ne
                    ne = cls.parse_ne(ne)
            except TypeError:
                ne = None
        return ne

    @staticmethod
    def parse_ne(nes):
        ne = defaultdict(list)
        ne['time'] = []
        ne['gpe'] = []
        ne['loc'] = []
        ne['person'] = []
        ne['org'] = []

        pat = re.compile('<[^<>]+?>')
        for tag, values in nes.iteritems():
            if not values:
                continue
            for value in values:
                value = re.sub(pat, '', value)
                print tag, value, len(value)
                if not value:
                    continue

                if tag == 'misc':
                    time_flag = value.count('年')
                    time_flag += value.count('月')
                    time_flag += value.count('日')
                    if value not in filter_words and len(value) > 2 and time_flag >= 2:
                        ne['time'].append(value)
                elif tag == 'gpe':
                    if value not in filter_words and len(value) > 2:
                        ne['gpe'].append(value)
                else:
                    ne[tag].append(value)
        return ne
