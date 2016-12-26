#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup
import urllib.request
from requests import get

from ft_sqlite3 import UseSqlite3

MAX_TWEET_MSG = 140


class UseNaver:
    def __init__(self, ft):
        pass

    def request_search_data(self, req_str, mode='blog'):
        url = 'https://openapi.naver.com/v1/search/%s?query=' % mode
        encText = urllib.parse.quote(req_str)
        options = '&display=2&sort=date'
        req_url = url + encText + options
        request = urllib.request.Request(req_url)
        request.add_header('X-Naver-Client-Id', self.naver_client_id)
        request.add_header('X-Naver-Client-Secret', self.naver_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            data = response_body.decode('utf-8')
            print(data)
            return json.loads(data)
        else:
            print("Error Code:" + rescode)
            return None

    def search_url_parse(self, need_parse_url):
        find_question_mark = need_parse_url.split("?")
        find_equal_mark = need_parse_url.split("=")
        result_url = '%s/%s' % (find_question_mark[0], find_equal_mark[-1])
        return result_url

    def search(self, req_str, mode='blog'):
        result = self.request_search_data(req_str, mode)
        if result is None:
            return

        total = (result['display'])
        result_msg = []
        url_list = []
        for i in range(total):
            url = self.search_url_parse(result['items'][i]['link'])
            msg = '%s %s\n\t%s' % (
                    [i+1], url, result['items'][i]['description'])
            url_list.append(url)
            result_msg.append(msg)

        return result_msg, url_list

    def match_find_all(self, target, mode='class'):
        def do_match(tag):
            classes = tag.get(mode, [])
            return all(c in classes for c in target)
        return do_match

    def get_today_information_and_technology(self, soup):
        it_news = {}
        url = 'http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=105'
        for w in soup.find_all(self.match_find_all(["main_content"], 'id')):
            for r in soup.find_all(self.match_find_all(["_rcount"])):
                for a in soup.find_all('a', href=True):
                    if a['href'].startswith(url) is False:
                        continue
                    if len(a.text) < 20:
                        continue
                    it_news[a['href']] = a.text
        return it_news

    def get_today_it_news(self, ft, news):
        s = UseSqlite3('naver')

        send_msg = []
        for news_url, news_desc in news.items():
            ret = s.already_sent_naver(news_url)
            if ret:
                print('already exist: ', news_url)
                continue
            else:
                s.insert_news(news_url)
                news_encode = news_desc.encode('utf-8')
                short_news_url = self.naver_shortener_url(ft, news_url)
                if len(news_encode) + len(short_news_url) > MAX_TWEET_MSG:
                    continue  # Long message just drop.

                send = '%s\n%s' % (news_desc.strip(), short_news_url.strip())
                send_msg.append(send)
        return send_msg

    def search_today_information_and_technology(self, ft):
        url = 'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=105'
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        news = self.get_today_information_and_technology(soup)

        return self.get_today_it_news(ft, news)

    def naver_shortener_url(self, ft, input_url):
        encText = urllib.parse.quote(input_url)
        data = "url=" + encText
        short_url = "https://openapi.naver.com/v1/util/shorturl"
        request = urllib.request.Request(short_url)
        request.add_header("X-Naver-Client-Id", ft.naver_client_id)
        request.add_header("X-Naver-Client-Secret", ft.naver_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read()
            res = json.loads(response_body.decode('utf-8'))
            return res['result']['url']
        else:
            print("Error Code:" + rescode)
            return None
