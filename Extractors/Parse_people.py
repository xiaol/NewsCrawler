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
from bs4 import BeautifulSoup
from lxml.html import soupparser as soup
from Cleaners.Encoding import encode_value

class Parser(object):

    @classmethod
    def get_title(cls, root):
        attrs = [{'attr': 'id', 'value': 'p_title'}]
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
        attrs = [{'attr': 'id', 'value': 'p_origin'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            origin = origin.replace(r'来源：', '').replace('\n', '')
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
        attrs = [{'attr': 'id', 'value': 'p_publishtime'},
                 ]
        date = Extractor.get_ment_by_attrs(root, attrs)
        if date is not None:
            date = date.text_content()
            date = date.strip()
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

        # a content with multi pages.
        attrs_multi = [{'attr': 'class', 'value': 'zdfy clearfix'},
                       ]
        multi_pages = Extractor.get_ment_by_attrs(root, attrs_multi)
        if multi_pages:
            multi_urls = []
            for page in multi_pages.iter():
                href = page.get('href')
                if href and not href.startswith('http:'):
                    href = ''.join([url.split('.cn')[0], '.cn', href])
                    print href
                    multi_urls.append(href)
            for url in multi_urls:
                source = Reqs.mobile_req(url)
                if not source:
                    continue
                print source.encoding
                # source = source.content
                try:
                    sp = BeautifulSoup(source.content, "lxml", from_encoding='gb18030')
                    source = str(sp)
                except:
                    source = source.content

                source = soup.fromstring(source)

                # a content with a image before p_content.
                attrs_img = [{'attr': 'class', 'value': 'text_img'},
                             ]
                conts_img = Extractor.get_ment_by_attrs(source, attrs_img)
                if conts_img:
                    picli += cls.cont_format(conts_img)

                # common content.
                attrs = [{'attr': 'id', 'value': 'p_content'},
                         ]
                conts = Extractor.get_ment_by_attrs(source, attrs)

                # print 'conts:', conts
                if conts:
                    picli += cls.cont_format(conts)

            return picli

        # a content with a image before p_content.
        attrs_img = [{'attr': 'class', 'value': 'text_img'},
                     ]
        conts_img = Extractor.get_ment_by_attrs(root, attrs_img)
        if conts_img:
            picli += cls.cont_format(conts_img)

        # common content.
        attrs = [{'attr': 'id', 'value': 'p_content'},
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
            if 'id' in child.attrib and child.attrib['id'] == 'p_content':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'diwen_ad':
                break
            if 'class' in child.attrib and child.attrib['class'] == 'zdfy clearfix':
                break
            if 'class' in child.attrib and child.attrib['class'] == 'textcode':
                break

            # video frame
            if 'class' in child.attrib and child.attrib['class'] == 'finVideo':
                continue

            # image frame
            if child.tag == 'img':
                img = child.get('src') or child.get('alt_src')

                if img and img.startswith('/mediafile'):
                    break

                if img and img not in dedupe:
                    if not img.startswith('http:'):
                        img = ''.join(['http://people.com.cn', img])
                    item[str(len(contents))]['img'] = img
                    contents.append(item)
                    dedupe.add(img)

                    # image ingo

                continue

            # news content
            if child.tag == 'p':

                # content
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt and txt not in dedupe:
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                continue

        return contents or []
