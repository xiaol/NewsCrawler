# -*- coding: utf-8 -*-
# Created by zhange on 15/11/10.
#

import redis
from redis import exceptions
import logging

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = 'ZXIDC_654321'


def from_settings():
    host = REDIS_HOST
    port = REDIS_PORT
    password = REDIS_PASSWORD

    try:
        # pool = redis.ConnectionPool(host=host, port=port)
        # r = redis.Redis(connection_pool=pool)
        r = redis.Redis(host, port, password=password)
        # r = redis.Redis(host=host, port=port)
        info = r.info()
        logging.info("Redis connection created with mode: %s,"
                     " connected_clients: %s" % (info.get("redis_mode"), info.get("connected_clients")))
        return r
    except exceptions.ConnectionError, e:
        logging.error("Redis connection create failed with exception: %s" % e)
        return None
