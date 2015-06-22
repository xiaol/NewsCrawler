# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/9
"""

import sys
from Dates.Dates import Dates
from Extractor import Extractor
from Reqs.Reqs import Reqs
from collections import defaultdict
import simplejson as json
from lxml.html import soupparser as soup
# reload(sys)
# sys.setdefaultencoding('utf-8')


class Parser(object):

    @classmethod
    def get_title(cls, root):
        attrs = [{'attr': 'class', 'value': 'diary-title'}]
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
        attrs = [{'attr': 'class', 'value': 'profile_nickname'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            return origin
        else:
            return None

    @classmethod
    def get_originurl(cls, root):
        return

    @classmethod
    def get_author(cls, root):
        attrs = [{'attr': 'class', 'value': 'profile_nickname'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
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

        attrs = [{'attr': 'class', 'value': 'bd'},
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
            if 'class' in child.attrib and child.attrib['class'] == 'rich_media_content':
                continue
            if 'id' in child.attrib and child.attrib['id'] == 'js_toobar':
                break
            if 'id' in child.attrib and child.attrib['id'] == 'ft':
                break

            # video frame
            if 'class' in child.attrib and child.attrib['class'] == 'finVideo':
                continue

            # image frame
            if child.tag == 'p' and 'class' in child.attrib and child.attrib['class'] == 'img':
                img = child.get('src') or child.get('data-feedlazy')
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
