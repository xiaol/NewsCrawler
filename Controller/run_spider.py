# -*- coding: utf-8 -*-


from scrapyd_api import ScrapydAPI

scrapyd = ScrapydAPI('http://localhost:6888')
list_projects = scrapyd.list_projects()
print list_projects

for project in list_projects:
    if project == 'default':
        continue
    print '.'*60
    list_spiders = scrapyd.list_spiders(project)
    print 'project:', project
    for spider in list_spiders:
        print 'spider:', spider
    status = scrapyd.list_jobs(project)
    running_jogs = status['running']
    running_spiders = [running_jog['spider'] for running_jog in running_jogs]
    for spider_name in list_spiders:
        if spider_name not in running_spiders:
             job_id = scrapyd.schedule(project, spider_name)
        else:
            print '%s is running.' % spider_name

