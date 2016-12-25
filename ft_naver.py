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
        news = []
        for w in soup.find_all(self.match_find_all(["main_content"], 'id')):
            for r in soup.find_all(self.match_find_all(["_rcount"])):
                res = r.text.splitlines()
                for i in range(len(res)):
                    if len(res[i]) < 15:
                        continue
                    news.append(res[i])

        return news

    def remove_duplicated_it_news(self, news):
        s = UseSqlite3('naver')

        send_msg = []
        for i in range(len(news)):
            ret = s.already_sent_naver(news[i])
            if ret:
                print('already exist: ', news[i])
                continue
            else:
                s.insert_news(news[i])
                news_encode = news[i].encode('utf-8')
                if len(news_encode) > MAX_TWEET_MSG:
                    # Long message just drop.
                    continue
                send_msg.append(news[i])
        return send_msg

    def search_today_information_and_technology(self):
        url = 'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=105'
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        news = self.get_today_information_and_technology(soup)

        return self.remove_duplicated_it_news(news)
