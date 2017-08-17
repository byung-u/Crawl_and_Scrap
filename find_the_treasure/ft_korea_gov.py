#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import re

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get, codes

from find_the_treasure.ft_sqlite3 import UseSqlite3
from find_the_treasure.ft_naver import UseNaver


class UseDataKorea:  # www.data.go.kr
    def __init__(self, ft):
        pass

    def ft_search_my_interesting_realestate(self, ft):
        s = UseSqlite3('korea')
        now = datetime.now()
        time_str = '%4d%02d' % (now.year, now.month)

        request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                ft.apt_trade_url,
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

        trade_info = []
        items = soup.findAll('item')
        for item in items:
            item = item.text
            item = re.sub('<.*?>', '|', item)
            info = item.split('|')
            if info[4] != ft.apt_trade_dong:
                continue
            # if info[5].find(ft.apt_trade_apt) == -1:
            #     continue
            ret_msg = '%s %s(%sm²) %s층 %s만원 준공:%s 거래:%s년%s월%s일' % (
                        info[4], info[5], info[8], info[11], info[1],
                        info[2], info[3], info[6], info[7])

            if (s.already_sent_korea(ret_msg)):
                ft.logger.info('Already sent: %s', ret_msg)
                continue
            trade_info.append(ret_msg)

        return trade_info

    def ft_get_molit_news(self, ft):  # 국토교통부 보도자료
        s = UseSqlite3('korea')
        url = 'http://www.molit.go.kr/USR/NEWS/m_71/lst.jsp'
        r = get(url)
        if r.status_code != codes.ok:
            ft.logger.error('[MOLT] request error, code=%d', r.status_code)
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        molt_info = []
        for tbody in soup.find_all('tbody'):
            for tr in tbody.find_all('tr'):
                try:
                    tr.a['href']
                except TypeError:
                    continue
                href = 'http://www.molit.go.kr/USR/NEWS/m_71/%s' % tr.a['href']
                if (s.already_sent_korea(href)):
                    ft.logger.info('Already sent: %s', href)
                    continue
                short_url = ft.shortener_url(href)
                if short_url is None:
                    short_url = href
                ret_msg = '%s\n%s' % (tr.a.text, short_url)
                molt_info.append(ret_msg)

        return molt_info
