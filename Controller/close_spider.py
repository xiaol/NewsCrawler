# -*- coding: utf-8 -*-


import os
import sys
import time
from scrapyd_api import ScrapydAPI


def kill_process_by_name(name):
    cmd = "ps -e | grep %s" % name
    f = os.popen(cmd)
    txt = f.readlines()
    if len(txt) == 0:
        print "no process \"%s\"!!" % name
        return
    else:
        for line in txt:
            colum = line.split()
            pid = colum[0]
            cmd = "kill -9 %d" % int(pid)
            rc = os.system(cmd)
            if rc == 0:
                print "exec \"%s\" success!!" % cmd
            else:
                print "exec \"%s\" failed!!" % cmd
        return
if __name__ == '__main__':

    scrapyd = ScrapydAPI('http://localhost:6888')
    list_projects = scrapyd.list_projects()
    print list_projects

    for project in list_projects:
        if project == 'default':
            continue
        print '.' * 60
        list_spiders = scrapyd.list_spiders(project)
        print 'project:', project
        for spider in list_spiders:
            print 'spider:', spider
        status = scrapyd.list_jobs(project)
        running_jogs = status['running']
        running_spiders = [running_jog['spider'] for running_jog in running_jogs]
        print 'running_spiders:', running_spiders

        for running_jog in running_jogs:
            jog_id = running_jog['id']
            a = scrapyd.cancel(u'NewsCrawler', jog_id)
            print running_jog['spider'] + ' closing!'
