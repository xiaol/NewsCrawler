# -*- coding: utf-8 -*-

# Scrapy settings for NewsCrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'NewsCrawler'

SPIDER_MODULES = ['NewsCrawler.spiders']
NEWSPIDER_MODULE = 'NewsCrawler.spiders'

# For ban
DOWNLOAD_DELAY = 2

RANDOMIZE_DOWNLOAD_DELAY = True

COOKIES_ENABLES = False

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'NewsCrawler.useragent.RotateUserAgentMiddleware': 400
}

EXTENSIONS = {'scrapy.contrib.feedexport.FeedExporter': None}

ITEM_PIPELINES = {
    'NewsCrawler.pipelines.ListPipeline': 200,
    'NewsCrawler.pipelines.ContentPipeline': 201,
}

SLYDUPEFILTER_ENABLED = False
CSV_EXPORT_FIELDS = None

CONCURRENT_ITEMS = 100
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 0
DEPTH_LIMIT = 0
DEPTH_PRIORITY = 0
DNSCACHE_ENABLED = True


# Docker & Scrapyjs
# DOWNLOADER_MIDDLEWARES = {
#     'scrapyjs.SplashMiddleware': 725,
#     }
#
# DUPEFILTER_CLASS = 'scrapyjs.SplashAwareDupeFilter'
# SPLASH_URL = 'http://localhost:8050/'
