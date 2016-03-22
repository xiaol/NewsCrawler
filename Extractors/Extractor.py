# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/8
"""


class Extractor(object):

    @classmethod
    def get_list(cls, root, xp):
        urls = root.xpath(xp)
        urls = [(i.text_content().replace('\n', ' ').strip(), i.get('href')) for i in urls]
        return urls or []

    @classmethod
    def get_ment_by_names(cls, root, names):
        for name in names:
            sel = '//*[@name="%s"]' % name
            ment = root.xpath(sel)
            if len(ment):
                return ment[0]
        return None

    @classmethod
    def get_ment_by_attrs(cls, root, attrs):
        for attr in attrs:
            if 'attr' in attr:
                sel = '//*[@%s="%s"]' % (attr['attr'], attr['value'])
                ment = root.xpath(sel)
                if len(ment):
                    return ment[0]
        return None

    @classmethod
    def get_ment_by_tags(cls, root, tags):
        for tag in tags:
            sel = '//%s' % tag
            ment = root.xpath(sel)
            if len(ment):
                return ment[0]
        return None

    @classmethod
    def get_ment_by_xps(cls, root, xps):
        for xp in xps:
            ment = root.xpath(xp)
            if len(ment):
                return ment[0].text_content()
        return None
