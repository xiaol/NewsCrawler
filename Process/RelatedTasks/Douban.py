# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/29
"""

from Reqs.Reqs import Reqs
from lxml.html import soupparser as soup


class Douban(object):

    @classmethod
    def get_douban(cls, ne):
        douban_tags = []
        ne = [value[0] for value in ne.values() if value]
        if not ne:
            return None

        for tag in ne:
            url_tag = cls.extract_douban(tag)
            if url_tag:
                tag_url_pairs = [tag, url_tag]
                douban_tags.append(tag_url_pairs)
        return {'douban': douban_tags}

    @staticmethod
    def extract_douban(tag):

        # url = "http://www.douban.com/tag/%s/?source=topic_search" % tag
        url = "http://www.douban.com/search?cat=1019&q=%s" % tag
        req = Reqs.pc_req(url)
        if req:
            cont = req.content
        else:
            return None
        try:
            root = soup.fromstring(cont)
            element_href = root.xpath('//div[@class="result"]/div[@class="content"]'
                                      '/div[@class="title"]/descendant::a[@target="_blank"]/@href')[0]
            return element_href or None
        except Exception as e:
            print "douban tag request error==>", e
            return None
