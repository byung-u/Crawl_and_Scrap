#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from find_the_treasure.ft_sqlite3 import UseSqlite3


class TechBlog:
    def __init__(self, ft):
        self.sqlite3 = UseSqlite3('tech_blog')

    def create_result_msg(self, ft, result_url, msg, name):
        if self.sqlite3.already_sent_tech_blog(result_url):
            return None

        self.sqlite3.insert_tech_blog(result_url)
        result_url = ft.shortener_url(result_url)

        result = '%s\n%s\n#%s' % (result_url, msg, name)
        result = ft.check_max_tweet_msg(result)
        return result

    def boxnwhisker(self, ft):
        url = 'http://www.boxnwhis.kr/'
        r = ft.request_and_get(url, 'Tech blog boxnwhisker')
        if r is None:
            return
        soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
        # body > section.recent-posts > ol > li:nth-child(5) > h2 > a
        sessions = soup.select('h2 > a')
        for s in sessions:
            result_url = '%s%s' % (url, s['href'])
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'boxnwhisker')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog boxnwhisker')

    def daliworks(self, ft):
        url = 'http://techblog.daliworks.net/'
        r = ft.request_and_get(url, 'Tech blog daliworks')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # main > div > article:nth-child(3) > h1 > a
        sessions = soup.select('div > article > h1 > a')
        for s in sessions:
            result_url = '%s%s' % (url, s['href'])
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'daliworks')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog daliworks')

    def devpools(self, ft):
        url = 'http://devpools.kr/'
        r = ft.request_and_get(url, 'Tech blog devpools')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('div > div > header > h2 > a')
        for s in sessions:
            result_url = s['href']
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'devpools')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog devpools')

    def dramancompany(self, ft):
        url = 'http://blog.dramancompany.com/'
        r = ft.request_and_get(url, 'Tech blog dramancompany')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # masonry > article.post-749.post.type-post.status-publish.format-standard.hentry.category-develop.post-container.masonry-element.col-md-4 > div.post-article.post-title > h2 > a
        sessions = soup.select('div > h2 > a')
        for s in sessions:
            result_url = s['href']
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'devpools')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog dramancompany')

    def goodoc(self, ft):
        url = 'http://dev.goodoc.co.kr/'
        r = ft.request_and_get(url, 'Tech blog goodoc')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # post-233 > header > h2 > a
        sessions = soup.select('header > h2 > a')
        for s in sessions:
            result_url = s['href']
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'goodoc')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog goodoc')

    def kakao(self, ft):
        url = 'http://tech.kakao.com'
        r = ft.request_and_get(url, 'Tech blog kakao')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for p in soup.find_all(ft.match_soup_class(['post'])):
            desc = p.find(ft.match_soup_class(['post-title']))
            result_url = '%s%s' % (url, p.a['href'])

            result = self.create_result_msg(ft, result_url, desc.string, 'kakao')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog kakao')

    def lezhin(self, ft):
        url = 'http://tech.lezhin.com'
        r = ft.request_and_get(url, 'Tech blog lezhin')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for p in soup.find_all(ft.match_soup_class(['post-item'])):
            desc = p.find(ft.match_soup_class(['post-title']))
            result_url = '%s%s' % (url, p.a['href'])

            result = self.create_result_msg(ft, result_url, desc.string, 'lezhin')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog lezhin')

    def linchpinsoft(self, ft):
        url = 'http://www.linchpinsoft.com/blog/'
        r = ft.request_and_get(url, 'Tech blog linchpinsoft')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # main > div.posts-box.posts-box-8 > div > div:nth-child(1) > article > div.post-details > h2 > a
        sessions = soup.select('div > h2 > a')
        for s in sessions:
            result = self.create_result_msg(ft, s['href'], s.text.strip(), 'linchpinsoft')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog linchpinsoft')

    def naver(self, ft):
        desc = ""
        url = 'http://d2.naver.com/d2.atom'
        r = ft.request_and_get(url, 'Tech blog naver_d2')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for idx, p in enumerate(soup.find_all(['title', 'link'])):
            if idx & 1:
                result_url = p['href']
                result = self.create_result_msg(ft, result_url, desc, 'naver_d2')
                if result is None:
                    continue
                ft.post_tweet(result, 'Tech Blog naver_d2')
            else:
                desc = p.string

    def naver_nuli(self, ft):
        base_url = 'http://nuli.navercorp.com'
        url = 'http://nuli.navercorp.com/sharing/blog/main'
        r = ft.request_and_get(url, 'Tech blog naver_nuli')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # showList > ul > li:nth-child(1) > p.list_title > a
        sessions = soup.select('div > ul > li > p > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'naver_nuli')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog naver_nuli')

    def netmanias(self, ft):
        base_url = 'http://www.netmanias.com'
        url = 'http://www.netmanias.com/ko/'
        r = ft.request_and_get(url, 'Tech blog netmanias')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # body > div.clo_contents > div > div > div:nth-child(1) > div > div.mpw_frame.mps_netmanias.cmm_transbox > div.mpc_contents > div:nth-child(3) > div:nth-child(2) > div.mlp_contents > div.mlc_memo.cfs_malgun > div.mls_subject > a
        sessions = soup.select('div > div > div > a')
        for s in sessions:
            if s.string is None:
                continue
            if s['href'].find('#cmt') != -1:  # ignore comment
                continue
            if s['href'].find('&tag') != -1:  # ignore tag page
                continue
            if s['href'].find('id=sponsor') != -1:  # ignore sponsor page
                continue
            if s['href'].find('id=sitenews') != -1:  # ignore sitenews page
                continue
            if s['href'].find('id=qna') != -1:  # ignore qna page
                continue
            if s['href'].find('no=') == -1:  # ignore subject page
                continue
            result_url = '%s%s' % (base_url, s['href'])
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'netmanias')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog netmanias')

    def ridi(self, ft):
        base_url = 'https://www.ridicorp.com/'
        url = 'https://www.ridicorp.com/blog/'
        r = ft.request_and_get(url, 'Tech blog ridicorp')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for l in soup.find_all(ft.match_soup_class(['list-item'])):
            desc = l.find(ft.match_soup_class(['desc']))
            result_url = '%s%s' % (base_url, l['href'])
            result = self.create_result_msg(ft, result_url, desc.string, 'ridicorp')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog ridi')

    def skplanet(self, ft):
        url = 'http://readme.skplanet.com/'
        r = ft.request_and_get(url, 'Tech blog skplanet')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('header > h1 > a')
        for s in sessions:
            result_url = '%s%s' % (url, s['href'])
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'skplanet')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog skplanet')

    def spoqa(self, ft):
        base_url = 'https://spoqa.github.io/'
        url = 'https://spoqa.github.io/index.html'
        r = ft.request_and_get(url, 'Tech blog spoqa')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for p in soup.find_all(ft.match_soup_class(['posts'])):
            for auth in p.find_all(ft.match_soup_class(['post-author-info'])):
                post = auth.find(ft.match_soup_class(['post-title']))
                desc = auth.find(ft.match_soup_class(['post-description']))
                result_url = '%s%s' % (base_url, post.a['href'][1:])
                result = self.create_result_msg(ft, result_url, desc.string, 'spoqa')
                if result is None:
                    continue
                ft.post_tweet(result, 'Tech Blog spoqa')

    def tosslab(self, ft):
        url = 'http://tosslab.github.io/'
        r = ft.request_and_get(url, 'Tech blog tosslab')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # body > div.container > div > section > ul.posts > li:nth-child(2) > h2 > a
        sessions = soup.select('div > div > section > ul > li > h2 > a')
        for s in sessions:
            result_url = '%s%s' % (url, s['href'])
            result = self.create_result_msg(ft, result_url, s.text.strip(), 'tosslab')
            if result is None:
                continue
            ft.post_tweet(result, 'Tech Blog tosslab')

    def tyle(self, ft):
        url = 'https://blog.tyle.io/'
        r = ft.request_and_get(url, 'Tech blog tyle')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('div > a')
        for s in sessions:
            try:
                desc = s.span.string
                result_url = '%s%s' % (url, s['href'])
                result = self.create_result_msg(ft, result_url, desc, 'tyle')
                if result is None:
                    continue
                ft.post_tweet(result, 'Tech Blog tyle')
            except:
                continue

    def whatap(self, ft):
        url = 'http://tech.whatap.io/'
        r = ft.request_and_get(url, 'Tech blog whatap')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for w in soup.find_all(ft.match_soup_class(['widget_recent_entries'])):
            for a_tag in w.find_all('a'):
                result_url = a_tag['href']
                result = self.create_result_msg(ft, result_url, a_tag.text, 'whatap')
                if result is None:
                    continue
                ft.post_tweet(result, 'Tech Blog whatap')

    def woowabros(self, ft):
        base_url = 'http://woowabros.github.io'
        url = 'http://woowabros.github.io/index.html'
        r = ft.request_and_get(url, 'Tech blog woowabros')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for l in soup.find_all(ft.match_soup_class(['list'])):
            for lm in l.find_all(ft.match_soup_class(['list-module'])):
                desc = lm.find(ft.match_soup_class(['post-description']))
                result_url = '%s%s' % (base_url, lm.a['href'])
                if result_url is None or desc.string is None:
                    continue
                result = self.create_result_msg(ft, result_url, desc.string, 'woowabros')
                if result is None:
                    continue
                ft.post_tweet(result, 'Tech Blog woowabros')
