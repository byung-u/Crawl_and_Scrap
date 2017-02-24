#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import re

from bs4 import BeautifulSoup
from datetime import datetime
from ft_sqlite3 import UseSqlite3


class UseDataKorea:  # www.data.go.kr
    def __init__(self, ft):
        pass

    def ft_search_my_interesting_realstate(self, ft):
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
            print('[ERR] UnicodeEncodeError')
            return -1

        data = res.read().decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')
        if (soup.resultcode.string != '00'):
            print('[ERR]', soup.resultmsg.string)
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
                print('Already sent: ', ret_msg)
                continue
            s.insert_trade_info(ret_msg)
            trade_info.append(ret_msg)

        return(trade_info)
