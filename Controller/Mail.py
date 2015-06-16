# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/12
"""

import smtplib
from email.mime.text import MIMEText
from Dates.Dates import Dates

mailto_list = ["475897864@qq.com"]
mail_host = "smtp.qq.com"
mail_user = "1804615553@qq.com"
mail_pass = "Jiu4aini58"
mail_postfix = "qq.com"


def send_mail(cont_dict):
    cont_dict = sorted(cont_dict.iteritems(), key=lambda d: d[0], reverse=False)
    me = "Spider"+"<"+mail_user+"@"+mail_postfix+">"
    cont_dict = ["<li>" + str(item[0]) + " : " + str(item[1]) + "</li>" for item in cont_dict]
    cont_dict = "<ul>\n" + "<li>Time : " + Dates.time() + "</li>" + '\n'.join(cont_dict) + "\n</ul>"
    msg = MIMEText(cont_dict, _subtype='html', _charset='utf8')
    msg['Subject'] = "Spider Status"
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user, mail_pass)
        s.sendmail(me, mailto_list, msg.as_string())
        s.close()
        print "发送成功"
        return True
    except Exception, e:
        print "发送失败"
        print str(e)
        return False
