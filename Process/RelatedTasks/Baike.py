# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/29
"""

import re
import sys
from Reqs.Reqs import Reqs
from lxml.html import soupparser as soup
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf8')


class Baike(object):

    @classmethod
    def get_baike(cls, ne):
        ne = [value[0] for value in ne.values() if value]
        if ne:
            tag = ne[0]
            result = cls.extract_baike(tag)
            return result or None
        else:
            return None

    @staticmethod
    def extract_baike(tag):
        result = {}
        url = "http://baike.baidu.com/search/none?word=%s&pn=0&rn=10&enc=utf8" % tag
        cont = Reqs.pc_req(url)
        if cont:
            cont = cont.content
            try:
                root = soup.fromstring(cont)
                element = root.xpath('//dl[@class="search-list"]/descendant::a[@target="_blank"]')[0]
                element_href = root.xpath('//dl[@class="search-list"]/descendant::a[@target="_blank"]/@href')[0]
                element_abstract = root.xpath('//dl[@class="search-list"]/descendant::p[@class="result-summary"]')[0]
                raw_content = etree.tostring(element, encoding="utf-8")
                raw_content_abstract = etree.tostring(element_abstract, encoding="utf-8")
                pat = re.compile('<[^<>]+?>|&#13;|\\n')
                title = re.sub(pat, '', raw_content)
                url = element_href
                abstract = re.sub(pat, '', raw_content_abstract)
                result = {"title": title, "url": url, "abstract": abstract}
            except Exception:
                result = None
        return {'baike': result} if result else None
