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
    def get_imgnum(cls, cont):
        items = [item.values() for item in cont]
        img = [item for item in items if item[0].keys()[0] == 'img']
        return len(img)

    @classmethod
    def get_content(cls, contents, url):
        picli = []

        # ensure the type of content
        mt_url = contents[0].get('mtUrl', '')
        if 'phtml' in mt_url:
            print 'This is a image page.'
            # Api of image page.
            api = 'http://m.huanqiu.com/view.html?id=NewsID&act=img'
            try:
                news_id = url.split('id=')[-1].split('&')[0]
            except IndexError:
                return None
            url = api.replace('NewsID', news_id)
            source = Reqs.mobile_req(url)
            if source:
                source = source.content
                root = soup.fromstring(source)
                attrs = [{'attr': 'class', 'value': 'picCon'},
                         ]
                root = Extractor.get_ment_by_attrs(root, attrs)
                if root:
                    picli += cls.cont_format(root)
        else:
            source = [content.get('content') for content in contents]
            source = ''.join(source)
            root = soup.fromstring(source)
            picli += cls.cont_format(root)

        return picli

    @staticmethod
    def cont_format(node):
        contents = []
        dedupe = set()

        try:
            node.find('.//div[@class="article_date"]').drop_tree()
        except AttributeError:
            pass

        for child in node.iter():
            item = defaultdict(dict)

            print 'Tag', child.tag, 'ATTR', child.attrib

            # tags filter
            if 'class' in child.attrib and child.attrib['class'] == 'article_date':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'article_intro':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'show_more':
                break

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
                    # image info or common txt
                    if 'align' in child.attrib and child.attrib['align'] == 'center':
                        tag = 'img_info'
                    else:
                        tag = 'txt'

                    item[str(len(contents))][tag] = txt
                    contents.append(item)
                    dedupe.add(txt)
                continue

        return contents or []
