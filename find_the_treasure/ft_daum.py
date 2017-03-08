#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import urllib.request
import re
import sys

from bs4 import BeautifulSoup
from requests import get

from find_the_treasure.ft_sqlite3 import UseSqlite3


class UseDaum:
    def __init__(self, ft):
        self.sqlite3 = UseSqlite3('daum')

    def read_other_blog_link(self, ft, url):
        result = []

        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all(ft.match_soup_class(['view'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                result.append(p.text.replace('\n', ' ').strip())
        return result

    def read_daum_blog_link(self, ft, url):
        result = []

        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all(ft.match_soup_class(['article'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                if p.text.find('adsbygoogle') >= 0:
                    continue
                result.append(p.text.strip())

        for a in soup.find_all(ft.match_soup_class(['area_view'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                if p.text.find('adsbygoogle') >= 0:
                    continue
                result.append(p.text.strip())
        return result

    def request_search_data(self, ft, req_str, mode='accu'):
        # https://apis.daum.net/search/blog?apikey={apikey}&q=다음&output=json
        url = 'https://apis.daum.net/search/blog?apikey=%s&q=' % (
                ft.daum_app_key)
        encText = urllib.parse.quote(req_str)
        options = '&result=20&sort=%s&output=json' % mode
        req_url = url + encText + options
        request = urllib.request.Request(req_url)
        try:
            response = urllib.request.urlopen(request)
        except:
            ft.logger.error('[DAUM]search data failed: %s %s', req_str, sys.exc_info()[0])
            return None
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            data = response_body.decode('utf-8')
            res = json.loads(data)

            send_msg_list = []
            # http://xxx.tistory.com
            p = re.compile(r'^http://\w+.tistory.com/\d+')

            for i in range(len(res['channel']['item'])):
                # title = res["channel"]['item'][i]['title']
                if (self.check_daum_duplicate(ft, res["channel"]['item'][i]['link'])):
                    continue  # True
                m = p.match(res["channel"]['item'][i]['link'])
                if m is None:  # other
                    msg = self.read_other_blog_link(ft, res["channel"]['item'][i]['link'])
                else:  # tistory blog
                    msg = self.read_daum_blog_link(ft, res["channel"]['item'][i]['link'])

                send_msg_list.append(res["channel"]['item'][i]['link'])
                send_msg_list.append("\n".join(msg))

            send_msg = "\n".join(send_msg_list)
            return send_msg
        else:
            ft.logger.error("[DAUM] Error Code: %s" + rescode)
            return None

    def check_daum_duplicate(self, ft, blog_url):
        ret = self.sqlite3.already_sent_daum(blog_url)
        if ret:
            ft.logger.info('Already exist: %s', blog_url)
            return True

        self.sqlite3.insert_daum_blog(blog_url)
        return False