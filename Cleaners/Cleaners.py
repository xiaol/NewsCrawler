# -*- coding: utf-8 -*-
"""
    Project: NewsCrawler
    Purpose: Clean the doc from spider.
    Version:
    Author:  ZG
    Date:    15/6/8
"""

import re


class Cleaners(object):

    re_script = re.compile('<script[\s\S]+?/script>', re.I)
    re_style = re.compile('<style[\s\S]+?/style>', re.I)
    re_br = re.compile('<br\s*?/?>')
    re_comment = re.compile('<!--[^>]*-->')
    re_link = re.compile('<link[\s\S]+?>', re.I)
    re_foot = re.compile('<foot[\s\S]+?>', re.I)
    re_footer = re.compile('<footer[\s\S]+?>', re.I)
    re_footer_s = re.compile('<Footer[\s\S]+?>', re.I)
    re_footnote = re.compile('<footnote[\s\S]+?>', re.I)

    @classmethod
    def clean(cls, htmlstr):
        s = cls.re_script.sub('', htmlstr)
        s = cls.re_style.sub('', s)
        s = cls.re_br.sub('\n', s)
        s = cls.re_comment.sub('', s)
        s = cls.re_link.sub('', s)
        s = cls.re_foot.sub('', s)
        s = cls.re_footer.sub('', s)
        s = cls.re_footer_s.sub('', s)
        s = cls.re_footnote.sub('', s)
        s = '\n'.join([line for line in s.split('\n') if line.strip()])
        return s

