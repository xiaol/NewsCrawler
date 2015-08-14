# -*- coding: utf-8 -*-

from scrapyd_api import ScrapydAPI

print '.'*60
scrapyd = ScrapydAPI('http://localhost:6888')
list_projects = scrapyd.list_projects()
print list_projects

for project in list_projects:
    if project == 'default':
        continue
    print '.'*60
    list_spiders = scrapyd.list_spiders(project)
    print 'project:', project
    print 'totals: ', len(list_spiders)
    for spider in list_spiders:
        print 'spider:', spider
    status = scrapyd.list_jobs(project)
    running_spider = status['running']
    print 'runs: ', len(running_spider)
    print 'running spider:'
    for spider in running_spider:
        print spider


