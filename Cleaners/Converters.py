# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/7/5
"""

from langconv import *

def f2j(line):
    # 转换繁体到简体
    try:
        line = Converter('zh-hans').convert(line.decode('utf-8'))
        return line.encode('utf-8')
    except TypeError:
        return None


def j2f(line):
    # 转换简体到繁体
    try:
        line = Converter('zh-hant').convert(line.decode('utf-8'))
        return line.encode('utf-8')
    except TypeError:
        return None