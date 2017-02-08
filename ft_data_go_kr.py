#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import urllib.request
import re

from bs4 import BeautifulSoup
from datetime import datetime
from ft_sqlite3 import UseSqlite3


class UseDataKorea:  # www.data.go.kr
    def __init__(self):
        config = configparser.ConfigParser()
        config.readfp(open('./ft.ini'))
        self.url = config.get('DATA_GO_KR', 'apt_trade_url')
        self.svc_key = config.get('DATA_GO_KR', 'apt_rent_key', raw=True)
        self.dong = config.get('DATA_GO_KR', 'dong')
        self.district_code = config.get('DATA_GO_KR', 'district_code')
        self.apt = config.get('DATA_GO_KR', 'apt', raw=True)

    def ft_search_my_interesting_realstate(self):
        s = UseSqlite3('korea')
        now = datetime.now()
        time_str = '%4d%02d' % (now.year, now.month)

        request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                self.url, self.district_code, time_str, self.svc_key)

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
            if info[4] != self.dong:
                continue
            # if info[5].find(self.apt) == -1:
            #     continue
            ret_msg = '%s\n %s(%sm²) %s층\n %s만원\n 준공:%s 거래:%s년%s월%s일' % (
                        info[4], info[5], info[8], info[11], info[1],
                        info[2], info[3], info[6], info[7])

            if (s.already_sent_korea(ret_msg)):
                print('Already sent: ', ret_msg)
                continue
            s.insert_trade_info(ret_msg)
            trade_info.append(ret_msg)

        return(trade_info)
