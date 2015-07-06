# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/9
"""

import re
from Dates.Dates import Dates
from Extractor import Extractor
from Reqs.Reqs import Reqs
from collections import defaultdict
import simplejson as json
from lxml import etree
from lxml.html import soupparser as soup


class Parser(object):

    @classmethod
    def get_list(cls, root, xp):
        items = []
        urls = root.xpath(xp)
        urls = urls[0]
        uri, txt = '', ''
        if urls is not None:
            for url in urls.iter():
                if url.tag == 'section' and 'data-id' in url.attrib:
                    uri = url.attrib['data-id']
                if url.tag == 'h3':
                    txt = url.text
                if uri and txt:
                    items.append((txt, uri))
        return items or []

    @classmethod
    def get_title(cls, root):
        attrs = [{'attr': 'class', 'value': 'title'}]
        tag = Extractor.get_ment_by_attrs(root, attrs)
        if tag is not None:
            tag = tag.text_content().strip()
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

    @staticmethod
    def clean_quote(source):
        re_script = re.compile('<blockquote[\s\S]+?/blockquote>', re.I)
        source = re_script.sub('', source)
        return source

    @staticmethod
    def format_img(source):
        source = source.replace('<img', '</p><p><img').replace('" >', '" ></p><p>')
        return source

    @classmethod
    def get_content_by_url(cls, url):
        contents = []
        dedupe = set()

        uri = "http://m.toutiao.com/articleContent"
        content_id = [block for block in url.split('/') if block]
        url = '/'.join([uri, content_id[-1].replace('a', '')]) + '/'
        source = Reqs.mobile_req(url)
        if not source:
            return contents
        source = cls.clean_quote(source.content)
        source = cls.format_img(source)
        print source
        root = soup.fromstring(source)
        for child in root.iter('p'):
            item = defaultdict(dict)

            print 'Tag', child.tag, 'ATTR', child.attrib
            if child.tag == 'html':
                continue

            # video = child.find('div')
            # if video:
            #     if 'class' in video.attrib and video.attrib['class'] == 'online-video-wrapper':
            #         video = etree.tostring(video)
            #         video = video.replace('/></a>', '></i></a>')
            #         picli.append(video)

            img = child.find('img')
            if img is not None:
                src = img.get('src')
                if src and src not in dedupe:
                    item[str(len(contents))]['img'] = src
                    contents.append(item)
                    dedupe.add(src)
                continue

            if child.tag == 'p':
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt and txt not in dedupe:
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)

        return contents
