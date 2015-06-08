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
    start_url = Field()
    urls = Field()


class ContItem(Item):
    """
    Hold the field form content by each url from ListItem.urls.
    """
    url = Field()
    title = Field()
    tag = Field()
    source = Field()
    source_url = Field()
    author = Field()
    update_time = Field()
    imgnum = Field()

    content = Field()