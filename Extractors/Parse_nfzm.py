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
        attrs = [{'attr': 'class', 'value': 'subject'}]
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
        attrs = [{'attr': 'class', 'value': 'source'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            origin = origin.split()[0]
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
        attrs = [{'attr': 'class', 'value': 'inf'},
                 ]
        date = Extractor.get_ment_by_attrs(root, attrs)
        if date is not None:
            date = date.text_content()
            date = date.strip().split()[:-1]
            date = ' '.join(date)
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

        attrs = [{'attr': 'class', 'value': 'content'},
                 ]
        conts = Extractor.get_ment_by_attrs(root, attrs)

        # attrs = ['article',
        #           ]
        # conts = Extractor.get_ment_by_tags(root, attrs)

        # print 'conts:', conts
        if conts:
            picli += cls.cont_format(conts)
        else:
            return picli

        # last_page = cls.get_last_page(url, root)
        # if last_page:
        #     index = len(conts) - 1
        #     for item in last_page:
        #         it = defaultdict(dict)
        #         it[str(index + int(item.keys()[0]))] = item.values()[0]
        #         picli.append(it)

        return picli

    # @classmethod
    # def get_last_page(cls, url, root):
    #     attrs = [{'attr': 'class', 'value': 'btnsW3'},
    #              ]
    #     last_page = Extractor.get_ment_by_attrs(root, attrs)
    #     if last_page is None:
    #         return None
    #     news_id = [block for block in url.split('/') if block][-1]
    #     api = 'http://m.sohu.com/api/n/v3/rest/ID/'
    #     api = api.replace('ID', news_id)
    #     last_content = Reqs.mobile_req(api)
    #     if not last_content:
    #         return None
    #     last_content = last_content.content
    #     last_content = json.loads(last_content)
    #     last_content = last_content.get('rest_content')
    #     if not last_content:
    #         return None
    #     last_content = soup.fromstring(last_content)
    #     last_content = cls.cont_format(last_content)
    #
    #     return last_content or None
    #

    @staticmethod
    def cont_format(node):
        contents = []
        dedupe = set()

        # Content info with tag is p, delete it.
        try:
            node.find('.//div[@class="article_sfont article_head"]').drop_tree()
        except AttributeError:
            pass

        for child in node.iter():
            item = defaultdict(dict)

            print 'Tag', child.tag, 'ATTR', child.attrib

            # tags filter
            if 'class' in child.attrib and child.attrib['class'] == 'article_p':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'contentImg':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'image':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'pic_head':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'comment_block':
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
                # image ingo
                if 'class' in child.attrib and child.attrib['class'] == 'picCaption':
                    txt = child.text_content()
                    txt = txt.strip() if txt else None
                    if txt and txt not in dedupe:
                        item[str(len(contents))]['img_info'] = txt
                        contents.append(item)
                        dedupe.add(txt)
                    continue

                # content
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt and txt not in dedupe:
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                continue

            if child.tag == 'h3':
                if 'class' in child.attrib and child.attrib['class'] == 'thirdTitle':
                    txt = child.text_content()
                    txt = txt.strip() if txt else None
                    if txt and txt not in dedupe:
                        item[str(len(contents))]['txt'] = txt
                        contents.append(item)
                        dedupe.add(txt)
                continue

        return contents or []
