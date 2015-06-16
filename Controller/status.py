# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/15
"""

import sys
sys.path.insert(0, "..")
sys.path.append("/work/pro/NewsCrawler/")
from InitSetup import Status

if __name__ == '__main__':
    # print Status.get_qlen_by_qname()
    status = Status.get_status()
    for k, v in status.iteritems():
        print k, '------>', v