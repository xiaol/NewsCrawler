# -*- coding: utf-8 -*-
"""
    Project:
    Purpose: 
    Version:
    Author:  ZG
    Date:    15/6/29
"""

import re
import simplejson as json


from Reqs.Reqs import Reqs


class Weibo(object):

    api = 'http://m.weibo.cn/page/pageJson?containerid=&containerid=100103' \
          'type%3D1%26q%3D{0}&type=all&queryVal={0}&luicode=20000174&title={0}' \
          '&v_p=11&ext=&fid=100103type%3D1%26q%3D{0}&uicode=10000011&page=1'

    @classmethod
    def get_weibo(cls, keyword):
        result = []
        url = cls.api.format(keyword)
        cont = Reqs.pc_req(url)
        if cont:
            cont = cont.content
            try:
                cont = json.loads(cont)
            except TypeError:
                return None

        cards = cont.get('cards')
        for card in cards:
            if card["card_type"] == 16:
                continue

            card_group = card["card_group"]
            for card_group_elem in card_group:
                if "scheme" not in card_group_elem.keys():
                    continue
                url = card_group_elem["scheme"]
                if "mblog" not in card_group_elem.keys():
                    continue
                mblog = card_group_elem["mblog"]
                like_count = mblog["like_count"]
                comments_count = mblog["comments_count"]
                reposts_count = mblog["reposts_count"]

                content = mblog["text"]
                content = cls.trim_bracket(content)

                update_time = mblog["created_at"]
                if "pics" in mblog.keys():
                    pics = mblog["pics"]
                else:
                    pics = []
                img_urls=[]
                for pic in pics:
                    img_urls.append(pic["url"])
                if img_urls:
                    img_url = img_urls[0]
                else:
                    img_url = ""
                user = mblog["user"]
                source_name = user["screen_name"]
                profile_image_url = user["profile_image_url"]
                result.append(
                    {
                        'img_url': img_url,
                        'content': content,
                        'source_name': source_name,
                        'url': url,
                        'updateTime': update_time,
                        'img_urls': img_urls,
                        'profile_image_url': profile_image_url,
                        'like_count': like_count,
                        'comments_count': comments_count,
                        'reposts_count': reposts_count
                    }
                )
        if result:
            result = cls.format_weibo(result)

        return result

    @staticmethod
    def trim_bracket(content):
        bracket_pat = re.compile(r'<.*?>')
        content = re.sub(bracket_pat, "", content)
        return content

    @staticmethod
    def format_weibo(weibos):
        result = []
        for weibo in weibos:
            result.append({
                'user': weibo.get('source_name'),
                'title': weibo.get('content'),
                'url': weibo.get('url'),
                'profileImageUrl': weibo.get('profileImageUrl'),
                'sourceSitename': weibo,
                'img': weibo.get('img_url'),
                'imgs': weibo.get('img_urls'),
                'like_count': weibo.get('like_count'),
                'comments_count': weibo.get('comments_count'),
                'reposts_count': weibo.get('reposts_count'),
            })
        if len(result) > 8:
            return {'weibo': result[0:8]}
        elif result:
            return {'weibo': result}
        else:
            return None
