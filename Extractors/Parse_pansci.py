# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/9
"""

from Dates.Dates import Dates
from Extractor import Extractor
from Reqs.Reqs import Reqs
from collections import defaultdict
import simplejson as json
from lxml.html import soupparser as soup
from Cleaners.Converters import f2j


class Parser(object):

    @classmethod
    def get_title(cls, root):
        attrs = ['title']
        tag = Extractor.get_ment_by_tags(root, attrs)
        if tag is not None:
            tag = tag.text_content()
            tag = tag.split(' | ')[0].strip()
            tag = unicode(f2j(tag))
            return tag
        else:
            return None

    @classmethod
    def get_tag(cls, root):
        tags = []
        attrs = [{'attr': 'name', 'value': 'keywords'}]
        tag = Extractor.get_ment_by_attrs(root, attrs)
        if tag is not None:
            tags = tag.get('content')
            tags = ','.join(tags.split())
        return tags or None

    @classmethod
    def get_origin(cls, root):
        attrs = [{'attr': 'class', 'value': 'source'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            origin = origin.replace(u'来源:', '').strip()
            return origin
        else:
            return None

    @classmethod
    def get_originurl(cls, root):
        return

    @classmethod
    def get_author(cls, root):
        attrs = [{'attr': 'class', 'value': 'article-info'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            origin = origin.split()[0]
            return origin
        else:
            return None

    @classmethod
    def get_date(cls, root):
        attrs = [{'attr': 'class', 'value': 'm_content_date'},
                 ]
        date = Extractor.get_ment_by_attrs(root, attrs)
        if date is not None:
            date = date.text_content()
            date = date.replace(u'发布:', '').strip()
            return date
        else:
            return Dates.time()

    @classmethod
    def get_imgnum(cls, cont):
        items = [item.values() for item in cont]
        img = [item for item in items if item[0].keys()[0] == 'img']
        return len(img)

    @classmethod
    def get_content(cls, url, root):
        picli = []

        # # /html/body/div[5]/div/div[2]/div/div/div[2]/div[1]/img
        # img_attrs = [{'attr': 'itemprop', 'value': 'image'},
        #          ]
        # total_img = Extractor.get_ment_by_attrs(root, img_attrs)
        # if total_img is not None:
        #     total_src = total_img.find('img').get('src')
        #     if total_src is not None:
        #         item = defaultdict(dict)
        #         item['0']['img'] = total_src
        #         picli.append(item)

        attrs = [{'attr': 'class', 'value': 'html'},
                 ]
        conts = Extractor.get_ment_by_attrs(root, attrs)

        # print 'conts:', conts
        if conts:
            picli += cls.cont_format(conts)
        else:
            return picli

        return picli

    @staticmethod
    def cont_format(node):
        contents = []
        dedupe = set()

        for child in node.iter():
            item = defaultdict(dict)

            print 'Tag', child.tag, 'ATTR', child.attrib

            # tags filter
            if 'class' in child.attrib and child.attrib['class'] == 'content':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'tag':
                break

            # video frame
            if 'class' in child.attrib and child.attrib['class'] == 'finVideo':
                continue

            # image frame
            if child.tag == 'img':
                img = child.get('src') or child.get('alt_src')
                if img and img not in dedupe:
                    item[str(len(contents))]['img'] = img
                    contents.append(item)
                    dedupe.add(img)
                continue

            # news content
            if child.tag == 'p':

                # content
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt:
                    txt = unicode(f2j(txt))
                if txt and txt not in dedupe and txt != u"\u8d44\u6599\u6765\u6e90\uff1a":
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                    print txt
                continue

            # news content
            if child.tag == 'h3':

                # content
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt:
                    txt = unicode(f2j(txt))
                if txt and txt not in dedupe and txt != u"\u8d44\u6599\u6765\u6e90\uff1a":
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                continue

        return contents or []
