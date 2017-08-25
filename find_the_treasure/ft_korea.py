#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import re

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get, codes

from find_the_treasure.ft_sqlite3 import UseSqlite3


class UseDataKorea:  # www.data.go.kr
    def __init__(self, ft):
        self.sqlite3 = UseSqlite3('korea')

    def request_and_get(self, ft, url, name):
        try:
            r = get(url)
            if r.status_code != codes.ok:
                ft.logger.error('[%s] request error, code=%d', name, r.status_code)
                return None
            return r
        except:
            ft.logger.error('[%s] connect fail', name)
            return None

    def realstate_trade(self, ft):
        now = datetime.now()
        time_str = '%4d%02d' % (now.year, now.month)

        request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (ft.apt_trade_url,
                                                                   ft.apt_trade_district_code,
                                                                   time_str,
                                                                   ft.apt_trade_svc_key)

        req = urllib.request.Request(request_url)
        try:
            res = urllib.request.urlopen(req)
        except UnicodeEncodeError:
            ft.logger.error('[OpenAPI] UnicodeEncodeError')
            return -1

        data = res.read().decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        if (soup.resultcode.string != '00'):
            ft.logger.error('[OpenAPI] %s', soup.resultmsg.string)
            return -1

        items = soup.findAll('item')
        for item in items:
            item = item.text
            print(item)
            item = re.sub('<.*?>', ' ', item)
            info = item.split()
            if info[3] not in ft.apt_trade_dong:
                continue
            # if info[5].find(ft.apt_trade_apt) == -1:
            #     continue
            ret_msg = '%s %s(%sm²) %s층 %s만원 준공:%s 거래:%s년%s월%s일\n#매매' % (
                      info[3], info[4], info[7],
                      info[10], info[0], info[1],
                      info[2], info[5], info[6])

            if (self.sqlite3.already_sent_korea(ret_msg)):
                ft.logger.info('Already sent: %s', ret_msg)
                continue
            ft.post_tweet(ret_msg, 'Realestate')


    def realstate_rent(self, ft):
        now = datetime.now()
        time_str = '%4d%02d' % (now.year, now.month)

        request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (ft.apt_rent_url,
                                                                   ft.apt_trade_district_code,
                                                                   time_str,
                                                                   ft.apt_trade_svc_key)

        req = urllib.request.Request(request_url)
        try:
            res = urllib.request.urlopen(req)
        except UnicodeEncodeError:
            ft.logger.error('[OpenAPI] UnicodeEncodeError')
            return -1

        data = res.read().decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        if (soup.resultcode.string != '00'):
            ft.logger.error('[OpenAPI] %s', soup.resultmsg.string)
            return -1

        items = soup.findAll('item')
        for item in items:
            item = item.text
            item = re.sub('<.*?>', ' ', item)
            info = item.split()
            if info[2] not in ft.apt_trade_dong:
                continue
            # if info[5].find(ft.apt_trade_apt) == -1:
            #     continue
            ret_msg = '%s %s(%sm²) %s층 %s만원(%s) 준공:%s 거래:%s년%s월%s일\n#전월세' % (
                      info[2], info[4], info[8], info[11],
                      info[3], info[6], info[0],
                      info[1], info[5], info[7])

            if (self.sqlite3.already_sent_korea(ret_msg)):
                ft.logger.info('Already sent: %s', ret_msg)
                continue
            ft.post_tweet(ret_msg, 'Realestate')

    def get_molit_news(self, ft):  # 국토교통부 보도자료
        url = 'http://www.molit.go.kr/USR/NEWS/m_71/lst.jsp'
        r = self.request_and_get(ft, url, 'molit')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for tbody in soup.find_all('tbody'):
            for tr in tbody.find_all('tr'):
                try:
                    tr.a['href']
                except TypeError:
                    continue
                href = 'http://www.molit.go.kr/USR/NEWS/m_71/%s' % tr.a['href']
                if (self.sqlite3.already_sent_korea(href)):
                    ft.logger.info('Already sent: %s', href)
                    continue
                short_url = ft.shortener_url(href)
                if short_url is None:
                    short_url = href
                ret_msg = '%s\n%s\n#molit' % (short_url, tr.a.text)
                ret_msg = ft.check_max_tweet_msg(ret_msg)
                ft.post_tweet(ret_msg, 'molit')

    def get_tta_news(self, ft):  # 한국정보통신기술협회 입찰공고
        base_url = 'http://www.tta.or.kr/news/'
        url = 'http://www.tta.or.kr/news/tender.jsp'
        r = self.request_and_get(ft, url, 'TTA')
        if r is None:
            return
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # s_container > div.scontent > div.content > table > tbody > tr:nth-child(2) > td.t_left > a
        sessions = soup.select('div > table > tbody > tr > td > a')
        for sess in sessions:
            result_url = '%s%s' % (base_url, sess['href'])
            if (self.sqlite3.already_sent_korea(result_url)):
                ft.logger.info('Already sent: %s', result_url)
                continue
            short_url = ft.shortener_url(result_url)
            if short_url is None:
                short_url = result_url
            ret_msg = '%s\n%s\n#TTA' % (short_url, sess.text.strip())
            ft.post_tweet(ret_msg, 'TTA')
