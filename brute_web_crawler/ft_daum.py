#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import urllib.request
import re
import sys

from bs4 import BeautifulSoup


class UseDaum:
    def __init__(self, bw):
        pass

    def read_other_blog_link(self, bw, url):
        result = []

        r = bw.request_and_get(url, 'Daum blog link')
        if r is None:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all(bw.match_soup_class(['view'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                result.append(p.text.replace('\n', ' ').strip())
        return result

    def read_daum_blog_link(self, bw, url):
        result = []

        r = bw.request_and_get(url, 'Daum blog link')
        if r is None:
            return None

        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all(bw.match_soup_class(['article'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                if p.text.find('adsbygoogle') >= 0:
                    continue
                result.append(p.text.strip())

        for a in soup.find_all(bw.match_soup_class(['area_view'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                if p.text.find('adsbygoogle') >= 0:
                    continue
                result.append(p.text.strip())
        return result

    def request_search_data(self, bw, req_str, mode='accu'):
        # https://apis.daum.net/search/blog?apikey={apikey}&q=다음&output=json
        url = 'https://apis.daum.net/search/blog?apikey=%s&q=' % (bw.daum_app_key)
        encText = urllib.parse.quote(req_str)
        options = '&result=20&sort=%s&output=json' % mode
        req_url = url + encText + options
        request = urllib.request.Request(req_url)
        try:
            response = urllib.request.urlopen(request)
        except:
            bw.logger.error('[DAUM]search data failed: %s %s', req_str, sys.exc_info()[0])
            return None
        rescode = response.getcode()
        if rescode != 200:
            bw.logger.error("[DAUM] Error Code: %s" + rescode)
            return None
        response_body = response.read()
        data = response_body.decode('utf-8')
        res = json.loads(data)

        send_msg_list = []
        # http://xxx.tistory.com
        p = re.compile(r'^http://\w+.tistory.com/\d+')

        for i in range(len(res['channel']['item'])):
            url = res['channel']['item'][i]['link']
            # title = res["channel"]['item'][i]['title']
            if bw.is_already_sent('DAUM', url):
                continue  # True
            m = p.match(url)
            if m is None:  # other
                msg = self.read_other_blog_link(bw, url)
            else:  # tistory blog
                msg = self.read_daum_blog_link(bw, url)

            if msg is None:
                continue
            send_msg_list.append(url)
            send_msg_list.append("\n".join(msg))

        send_msg = "\n".join(send_msg_list)
        return send_msg
