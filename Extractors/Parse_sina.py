# -*- coding: utf-8 -*-
"""
    Project:
    Purpose:
    Version:
    Author:  ZG
    Date:    15/6/17
"""

import json
import urlparse
from lxml import etree
from Reqs.Reqs import Reqs
from Extractor import Extractor
from collections import defaultdict
from lxml.html import soupparser as soup


class Parser(object):

    @classmethod
    def get_title(cls, root):
        tags = ['title']
        tag = Extractor.get_ment_by_tags(root, tags)
        if tag is not None:
            # tag = tag.text.split('-')[0].strip()
            return tag
        else:
            return None

    @classmethod
    def get_tag(cls, root):
        tags = []
        attrs = [{'attr': 'class', 'value': 'hot-area'}]
        tag = Extractor.get_ment_by_attrs(root, attrs)
        if tag is not None:
            for t in tag.iter():
                txt = t.text
                if txt:
                    tags.append(t.text)
            tags = ','.join(tags)
        return tags or None

    @classmethod
    def get_origin(cls, root):
        attrs = [{'attr': 'class', 'value': 'source'}]
        origin = Extractor.get_ment_by_attrs(root, attrs)
        if origin is not None:
            origin = origin.text_content()
            origin = origin.split()[-1]
            origin = origin if u'\u003a' not in origin else None
            return origin
        else:
            return None

    @classmethod
    def get_originurl(cls, root):
        return

    @classmethod
    def get_author(cls, root):
        return

    @classmethod
    def get_date(cls, root):
        attrs = [{'attr': 'class', 'value': 'source'}]
        date = Extractor.get_ment_by_attrs(root, attrs)
        if date is not None:
            date = date.text_content()
            date = date.split()[:-1]
            date = ' '.join(date)
            return date
        else:
            return None

    @classmethod
    def get_imgnum(cls, cont):
        items = [item.values() for item in cont]
        img = [item for item in items if item[0].keys()[0] == 'img']
        return len(img)

    @classmethod
    def get_content(cls, url, root, tree):
        picli = []

        # If this is a video site, just video in content
        vd2 = tree.find_class('video_cnt')      # Or response.url.startswith('http://video')
        if vd2:
            # picli = cls.video_site(tree)
            return picli

        # If this ia a picwarp site, just picwarp in content
        if url.startswith('http://photo'):
            contents = cls.pic_site(url)
            if contents:
                picli = contents
                return picli

        # This is a common site, maybe have a video, a picwarp, or a next page

        # If video, put the video to the front of this site
        vd = tree.find_class('article-module video')
        if vd:
            # picli = cls.video_frame(tree)                 # vd is a list[, ]
            picli = []

        attrs = [{'attr': 'class', 'value': 'art_content'},
                 {'attr': 'id', 'value': 'j_articleContent'}]
        conts = Extractor.get_ment_by_attrs(root, attrs)
        print 'conts:', conts
        if conts:
            picli += cls.cont_format(conts)

        # If has next pages, add to picli with simple check
        last_pages = []
        attrs = [{'attr': 'id', 'value': 'j_loadingbtn'},
                 {'attr': 'id', 'value': 'j_load_btn'}]
        next_page = Extractor.get_ment_by_attrs(root, attrs)
        if next_page:
            last_pages = cls.next_page(url)
        if last_pages:
            for page in last_pages:
                if page not in picli:
                    picli.append(page)
        return picli

    @staticmethod
    def video_site(tree):
        vd = tree.find_class('video_cnt')
        if vd:
            vd = etree.tostring(vd[0])
            vd = vd.replace('\n', '').replace('\t', '') + '</div>'
            vd = vd.replace('id="video"', 'id="video" style="width: 100%;"')
            vd = [vd, ] if len(vd) > 200 else []
            return vd
        else:
            return []

    @staticmethod
    def video_frame(tree):
        # Common website maybe have a video
        vd = tree.find_class('art_video')
        if vd:
            vd = etree.tostring(vd[0])
            vd = vd.replace('\n', '').replace('\t', '') + '</div>'
            vd = vd.replace('id="video"', 'id="video" style="width: 100%;"')
            vd = [vd, ] if len(vd) > 200 else []
            return vd                                           # List[, ]
        else:
            return []

    @staticmethod
    def pic_site(url):
        # This is just a picture website
        uri = 'http://photo.sina.cn/aj/album'
        parurl = urlparse.urlparse(url)
        parm = urlparse.parse_qs(parurl.query, True)
        qs = list()
        qs.append('='.join(['action', 'image']))
        if parm.get('ch'):
            qs.append('='.join(['ch', parm['ch'][0]]))
        if parm.get('sid'):
            qs.append('='.join(['sid', parm['sid'][0]]))
        if parm.get('aid'):
            qs.append('='.join(['aid', parm['aid'][0]]))
        if parm.get('cid'):
            qs.append('='.join(['cid', parm['cid'][0]]))
        if parm.get('vt'):
            qs.append('='.join(['vt', parm['vt'][0]]))
        qs.append('#column')
        api = '?'.join([uri, '&'.join(qs)])
        contents = []
        dedupe = set()
        conts = Reqs.mobile_req(api)
        if conts:
            conts = json.loads(conts.content)
            for cont in conts:
                item = defaultdict(dict)
                if cont['picurl'] not in dedupe:
                    item[str(conts.index(cont))]['img'] = cont['picurl']
                    contents.append(item)
                    dedupe.add(cont['picurl'])
                if cont['intro'] and cont['intro'] not in dedupe:
                    item = defaultdict(dict)
                    item[str(conts.index(cont))]['img_info'] = cont['intro']
                    contents.append(item)
                    dedupe.add(cont['intro'])
        return contents

    @staticmethod
    def cont_format(node):
        contents = []
        dedupe = set()

        for child in node.iter():
            item = defaultdict(dict)

            print 'Tag', child.tag, 'ATTR', child.attrib

            # tags filter
            if 'class' in child.attrib and child.attrib['class'] == 'weiboCard':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'userAction':
                continue
            if 'class' in child.attrib and child.attrib['class'] == 'read-more':
                break
            if 'class' in child.attrib and child.attrib['class'] == 'hotSearch':
                break
            if 'class' in child.attrib and child.attrib['class'] == 'load-more':
                break
            if 'class' in child.attrib and child.attrib['class'] == 'article-module hot':
                break

            if child.tag == 'img':
                img = child.get('src')
                if img and img not in dedupe:
                    item[str(len(contents))]['img'] = img
                    contents.append(item)
                    dedupe.add(img)
                    txt = child.get('alt')
                    txt = txt.strip() if txt else None
                    if txt and txt not in dedupe:
                        item = defaultdict(dict)
                        item[str(len(contents))]['img_info'] = txt
                        contents.append(item)
                        dedupe.add(txt)
                continue

            if 'class' in child.attrib and child.attrib['class'] == 'imgMessage':
                txt = child.text
                txt = txt.strip() if txt else None
                if txt and txt not in dedupe:
                    item[str(len(contents))]['img_info'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                    continue

            if child.tag == 'p':
                txt = child.text_content()
                txt = txt.strip() if txt else None
                if txt and txt not in dedupe:
                    item[str(len(contents))]['txt'] = txt
                    contents.append(item)
                    dedupe.add(txt)
                    continue

            # this is a table
            if child.tag == 'table' and u'\u7edf\u8ba1' in contents[-1]:
                tb = etree.tostring(child)
                tb = tb.replace('\n', '')
                contents.append(tb)
                continue

        return contents or []

    @staticmethod
    def next_page(url):
        # Even more than two pages, just need to request the API one time
        # next_url = '?'.join([url, 'pageAction=%s' % str(1)])
        # print 'next_url: ', next_url
        # cont = Reqs.mobile_req_txt(next_url)
        cont = None

        if 'detail-i' in url:
            docid = url.split('detail-i')[-1].split('.')[0]
            next_url = 'http://interface.sina.cn/wap_api/wap_get_article_info.d.json?docID=' + docid + '&page=2'
            print 'next_url: ', next_url
            cont = Reqs.mobile_req(next_url)

        if cont:
            try:
                cont = json.loads(cont.content)
            except ValueError:
                cont = None
            try:
                cont = cont['content']
                cont = soup.fromstring(cont)
                cont = [tag.text_content().replace(u'\u005b\u5fae\u535a\u005d', '') for tag in cont.iter('p')]
                cont = [tag for tag in cont if tag and tag != '\n']
                result = []
                for c in cont:
                    item = defaultdict(dict)
                    if c.startswith('http:'):
                        item[str(cont.index(c))]['img'] = c
                    else:
                        item[str(cont.index(c))]['txt'] = c
                        result.append(item)
                cont = result
            except KeyError:
                cont = []
        # print 'cont:', cont
        return cont or []