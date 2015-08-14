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


class Parser(object):

    @classmethod
    def get_title(cls, root):
        attrs = [{'attr': 'id', 'value': 'title'}]
        tag = Extractor.get_ment_by_attrs(root, attrs)
        if tag is not None:
            tag = tag.text
            tag = tag.replace('\n', ' ').strip()
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
        attrs = [{'attr': 'id', 'value': 'source'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            origin = origin.replace(r'来源：', '')
            return origin
        else:
            return None

    @classmethod
    def get_originurl(cls, root):
        return

    @classmethod
    def get_author(cls, root):
        attrs = [{'attr': 'class', 'value': 'authorName'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            origin = origin.split()[0]
            return origin
        else:
            return None

    @classmethod
    def get_date(cls, root):
        attrs = [
            {'attr': 'id', 'value': 'pubtime'},
            {'attr': 'class', 'value': 'time'},
                 ]
        date = Extractor.get_ment_by_attrs(root, attrs)
        if date is not None:
            date = date.text_content()
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

        currpage_urls = set()
        currpage_attrs = [{'attr': 'id', 'value': 'div_currpage'}, ]
        currpage_node = Extractor.get_ment_by_attrs(root, currpage_attrs)
        if currpage_node is not None:
            print currpage_node.tag, currpage_node.attrib
            for child in currpage_node.iter():
                print 'Tag', child.tag, 'ATTR', child.attrib
                if child.tag == 'a' and 'href' in child.attrib.keys():
                    href = child.attrib.get('href')
                    if href.startswith('http'):
                        currpage_urls.add(child.attrib.get('href'))
        if currpage_urls:
            currpage_urls = sorted([url for url in currpage_urls])
            print 'currpage_urls:', currpage_urls

        attrs = [
            {'attr': 'id', 'value': 'content'},
            {'attr': 'class', 'value': 'article'},
            {'attr': 'class', 'value': 'content00'},
        ]
        conts = Extractor.get_ment_by_attrs(root, attrs)

        # print 'conts:', conts
        if conts:
            picli += cls.cont_format(conts, url)
        if not currpage_urls:
            return picli

        for next_url in currpage_urls:
            cont = Reqs.mobile_req(next_url)
            if cont:
                conts = Extractor.get_ment_by_attrs(soup.fromstring(cont.content), attrs)
                if conts:
                    picli += cls.cont_format(conts, next_url)
        return picli

    @staticmethod
    def cont_format(node, url):
        contents = []
        dedupe = set()

        for child in node.iter():
            item = defaultdict(dict)

            print 'Tag', child.tag, 'ATTR', child.attrib

            # tags filter
            if 'class' in child.attrib and child.attrib['class'] == 'article_p':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'contentImg':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'page-Article':
                break
            if 'id' in child.attrib and child.attrib['id'] == 'div_page_roll1':
                break
            if 'id' in child.attrib and child.attrib['id'] == 'k14_00':
                break

            # video frame
            if 'class' in child.attrib and child.attrib['class'] == 'finVideo':
                continue

            # image frame
            if child.tag == 'img':
                # source image
                if child.get('sourcename'):
                    continue

                img = child.get('src') or child.get('alt_src')
                if img and img not in dedupe:

                    if not img.startswith('http'):
                        img = url.replace(url.split('/')[-1], img)

                    item[str(len(contents))]['img'] = img
                    contents.append(item)
                    dedupe.add(img)
                continue

            # news content
            if child.tag == 'p':

                # content
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt and txt not in dedupe and \
                        (u"\u4e0a\u4e00\u9875" not in txt or u"\u4e0a\u4e00\u9875" not in txt):
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                continue

        return contents or []
