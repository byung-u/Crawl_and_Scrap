#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from requests import get, codes

from find_the_treasure.ft_sqlite3 import UseSqlite3


class TechBlog:
    def __init__(self, ft):
        self.sqlite3 = UseSqlite3('tech_blog')

    def create_result_msg(self, ft, result_url, msg, name):
        if self.sqlite3.already_sent_tech_blog(result_url):
            return None

        result_url = ft.shortener_url(result_url)
        self.sqlite3.insert_tech_blog(result_url)

        result = '%s\n%s\n#%s' % (result_url, desc.string)
        result = ft.check_max_tweet_msg(result)

    def kakao(self, ft):
        send_msg = []
        url = 'http://tech.kakao.com'
        r = get(url)
        if r.status_code != codes.ok:
            ft.logger.error('[Tech blog kakao] request error, code=%d', r.status_code)
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for p in soup.find_all(ft.match_soup_class(['post'])):
            desc = p.find(ft.match_soup_class(['post-title']))
            result_url = '%s%s' % (url, p.a['href'])

            result = create_result_msg(ft, result_url, desc.string, 'kakao')
            if result is None:
                continue
            send_msg.append(result)
        return send_msg

    def lezhin(self, ft):
        send_msg = []
        url = 'http://tech.lezhin.com'
        r = get(url)
        if r.status_code != codes.ok:
            ft.logger.error('[Tech blog lezhin] request error, code=%d', r.status_code)
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for p in soup.find_all(ft.match_soup_class(['post-item'])):
            desc = p.find(ft.match_soup_class(['post-title']))
            result_url = '%s%s' % (url, p.a['href'])

            result = create_result_msg(ft, result_url, desc.string, 'lezhin')
            if result is None:
                continue
            send_msg.append(result)
        return send_msg

    def naver(self, ft):
        desc = ""
        send_msg = []
        url = 'http://d2.naver.com/d2.atom'
        r = get(url)
        if r.status_code != codes.ok:
            ft.logger.error('[Tech blog naver] request error, code=%d', r.status_code)
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for idx, p in enumerate(soup.find_all(['title', 'link'])):
            if idx & 1:
                result_url = p['href']

                result = create_result_msg(ft, result_url, desc, 'naver_d2')
                if result is None:
                    continue
                send_msg.append(result)
            else:
                desc = p.string
        return send_msg

    def ridi(self, ft):
        send_msg = []
        base_url = 'https://www.ridicorp.com/'
        url = 'https://www.ridicorp.com/blog/'
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for l in soup.find_all(ft.match_soup_class(['list-item'])):
            desc = l.find(ft.match_soup_class(['desc']))
            result_url = '%s%s' % (base_url, l['href'])
            result = create_result_msg(ft, result_url, desc.string, 'ridicorp')
            if result is None:
                continue
            send_msg.append(result)
        return send_msg

    def spoqa(self, ft):
        send_msg = []
        base_url = 'https://spoqa.github.io/'
        url = 'https://spoqa.github.io/index.html'
        r = get(url)
        if r.status_code != codes.ok:
            ft.logger.error('[Tech blog spoqa] request error, code=%d', r.status_code)
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for p in soup.find_all(ft.match_soup_class(['posts'])):
            for auth in p.find_all(ft.match_soup_class(['post-author-info'])):
                post = auth.find(ft.match_soup_class(['post-title']))
                desc = auth.find(ft.match_soup_class(['post-description']))
                result_url = '%s%s' % (base_url, post.a['href'][1:])
                result = create_result_msg(ft, result_url, desc.string, 'spoqa')
                if result is None:
                    continue
                send_msg.append(result)
        return send_msg

    def whatap(self, ft):
        send_msg = []
        url = 'http://tech.whatap.io/'
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for w in soup.find_all(ft.match_soup_class(['widget_recent_entries'])):
            for a_tag in w.find_all('a'):
                result_url = a_tag['href']
                result = create_result_msg(ft, result_url, a_tag.text, 'whatap')
                if result is None:
                    continue
                send_msg.append(result)
        return send_msg

    def woowabros(self, ft):
        send_msg = []
        base_url = 'http://woowabros.github.io'
        url = 'http://woowabros.github.io/index.html'
        r = get(url)
        if r.status_code != codes.ok:
            ft.logger.error('[Tech blog woowabros] request error, code=%d', r.status_code)
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for l in soup.find_all(ft.match_soup_class(['list'])):
            for lm in l.find_all(ft.match_soup_class(['list-module'])):
                desc = lm.find(ft.match_soup_class(['post-description']))
                result_url = '%s%s' % (base_url, lm.a['href'])
                if result_url is None or desc.string is None:
                    continue
                result = create_result_msg(ft, result_url, desc.string, 'woowabros')
                if result is None:
                    continue
                send_msg.append(result)
        return send_msg
