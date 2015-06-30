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
from lxml import etree
from Reqs.Reqs import Reqs

reload(sys)
sys.setdefaultencoding('utf8')


class Zhihu(object):

    @classmethod
    def get_zhihu(cls, keywords):
        key = ' '.join(keywords)
        zhihu_api = "http://www.zhihu.com/search?q={0}&type=question".format(key)
        try:
            req = Reqs.mobile_req(zhihu_api)
            if req:
                content = req.content
            else:
                return None
        except Exception:
            return None

        pat = re.compile('<[^<>]+?>')
        # pat_user = re.compile('<[^<>]+?>|[,，]')

        content = etree.HTML(content)
        elements = content.xpath('//li[@class="item clearfix"]')
        zhihus = []
        for element in elements:
            try:
                element_title = element.xpath('./div[@class="title"]/a')[0]
                raw_content_title = etree.tostring(element_title, encoding='utf-8')
                title = re.sub(pat, '', raw_content_title)
                url = "http://www.zhihu.com" + element.xpath('./div[@class="title"]/a[1]/@href')[0]
                user = element.xpath('.//a[@class="author"]/text()')[0]
                zhihu = {"title": title, "url": url, "user": user}
                zhihus.append(zhihu)
            except Exception:
                continue
        return {'zhihu': zhihus} if zhihus else None
