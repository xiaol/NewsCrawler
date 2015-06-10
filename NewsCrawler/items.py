# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ListItem(Item):
    """
    Hold the list of urls from start url.
    """
    start_url = Field()             # str                           # 抓取起始网址
    urls = Field()                  # list                          # 新闻网址列表


class ContItem(Item):
    """
    Hold the field form content by each url from ListItem.urls.
    """
    url = Field()                   # str                           ，抓取网址
    title = Field()                 # str                           ，文章标题
    tags = Field()                  # str("tag1,tag2,tag3")         ，关键字
    source = Field()                # str                           ，来源网站
    source_url = Field()            # str("http://..")              ，来源网址
    author = Field()                # str                           ，作者
    update_time = Field()           # str("YYYY-MM-DD HH:MM:SS")    ，发布时间
    imgnum = Field()                # int                           ，图片个数

    content = Field()                                               # 文章正文
    # list[
    #      {'0':{'img':'http://'}},
    #      {'1':{'img_info':'xxxxx'}},
    #      {'2':{'txt':'xxxxx'}},
    #      ....]

