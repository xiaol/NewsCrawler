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
        attrs = ['title']
        tag = Extractor.get_ment_by_tags(root, attrs)
        if tag is not None:
            tag = tag.text_content().strip()
            if ' | ' in tag:
                tag = tag.split(' | ')[0]
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
        attrs = [{'attr': 'class', 'value': 'time'},
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

        title_img_attrs = [{'attr': 'class', 'value': 'post-img'}, ]
        title_img_node = Extractor.get_ment_by_attrs(root, title_img_attrs)
        if title_img_node is not None:
            if 'style' in title_img_node.attrib.keys():
                attrib_style = title_img_node.attrib.get('style')
                if attrib_style:
                    title_src = attrib_style.replace('background-image: url(', '').replace(')', '')
                    if title_src.startswith('http') and (title_src.endswith('jpg') or title_src.endswith('png')):
                        picli.append({'0': {'img': title_src}})

        attrs = [{'attr': 'id', 'value': 'sc-container'},
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
            if 'id' in child.attrib and child.attrib['id'] == 'sc-container':
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
                if txt and txt not in dedupe:
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                continue

        return contents or []
