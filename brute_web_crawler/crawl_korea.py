#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import re

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get


class UseDataKorea:  # www.data.go.kr
    def __init__(self, bw):
        pass

    def realstate_trade(self, bw):
        now = datetime.now()
        time_str = '%4d%02d' % (now.year, now.month)

        for district_code in bw.apt_district_code:
            request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                          bw.apt_trade_url, district_code, time_str, bw.apt_svc_key)
            self.request_realstate_trade(bw, request_url)

    def request_realstate_trade(self, bw, request_url):

        req = urllib.request.Request(request_url)
        try:
            res = urllib.request.urlopen(req)
        except UnicodeEncodeError:
            bw.logger.error('[OpenAPI] UnicodeEncodeError')
            return -1

        data = res.read().decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        if (soup.resultcode.string != '00'):
            bw.logger.error('[OpenAPI] %s', soup.resultmsg.string)
            return -1

        items = soup.findAll('item')
        for item in items:
            item = item.text
            item = re.sub('<.*?>', ' ', item)
            info = item.split()
            if info[3] not in bw.apt_dong:
                continue
            # if info[5].find(bw.apt_trade_apt) == -1:
            #     continue
            ret_msg = '%s %s(%sm²) %s층 %s만원 준공:%s 거래:%s년%s월%s일\n#매매' % (
                      info[3], info[4], info[7],
                      info[10], info[0], info[1],
                      info[2], info[5], info[6])

            if bw.is_already_sent('KOREA', ret_msg):
                continue
            bw.post_tweet(ret_msg, 'Realestate')

    def realstate_rent(self, bw):
        now = datetime.now()
        time_str = '%4d%02d' % (now.year, now.month)

        for district_code in bw.apt_district_code:
            request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                          bw.apt_rent_url, district_code, time_str, bw.apt_svc_key)
            self.request_realstate_rent(bw, request_url)

    def request_realstate_rent(self, bw, request_url):
        req = urllib.request.Request(request_url)
        try:
            res = urllib.request.urlopen(req)
        except UnicodeEncodeError:
            bw.logger.error('[OpenAPI] UnicodeEncodeError')
            return -1

        data = res.read().decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        if (soup.resultcode.string != '00'):
            bw.logger.error('[OpenAPI] %s', soup.resultmsg.string)
            return -1

        items = soup.findAll('item')
        for item in items:
            item = item.text
            item = re.sub('<.*?>', ' ', item)
            info = item.split()
            if info[2] not in bw.apt_dong:
                continue
            # if info[5].find(bw.apt_trade_apt) == -1:
            #     continue
            ret_msg = '%s %s(%sm²) %s층 %s만원(%s) 준공:%s 거래:%s년%s월%s일\n#전월세' % (
                      info[2], info[4], info[8], info[11],
                      info[3], info[6], info[0],
                      info[1], info[5], info[7])

            if bw.is_already_sent('KOREA', ret_msg):
                continue
            bw.post_tweet(ret_msg, 'Realestate')

    def get_molit_news(self, bw):  # 국토교통부 보도자료
        url = 'http://www.molit.go.kr/USR/NEWS/m_71/lst.jsp'
        r = bw.request_and_get(url, 'molit')
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
                if bw.is_already_sent('KOREA', href):
                    bw.logger.info('Already sent: %s', href)
                    continue
                short_url = bw.shortener_url(href)
                if short_url is None:
                    short_url = href
                ret_msg = '%s\n%s\n#molit' % (short_url, tr.a.text)
                ret_msg = bw.check_max_tweet_msg(ret_msg)
                bw.post_tweet(ret_msg, 'molit')

    def get_tta_news(self, bw):  # 한국정보통신기술협회 입찰공고
        base_url = 'http://www.tta.or.kr/news/'
        url = 'http://www.tta.or.kr/news/tender.jsp'
        r = bw.request_and_get(url, 'TTA')
        if r is None:
            return
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # s_container > div.scontent > div.content > table > tbody > tr:nth-child(2) > td.t_left > a
        sessions = soup.select('div > table > tbody > tr > td > a')
        for sess in sessions:
            result_url = '%s%s' % (base_url, sess['href'])
            if bw.is_already_sent('KOREA', result_url):
                bw.logger.info('Already sent: %s', result_url)
                continue
            short_url = bw.shortener_url(result_url)
            if short_url is None:
                short_url = result_url
            ret_msg = '%s\n%s\n#TTA' % (short_url, sess.text.strip())
            bw.post_tweet(ret_msg, 'TTA')
