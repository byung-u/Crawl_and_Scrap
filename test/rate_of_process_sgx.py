#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
from bs4 import BeautifulSoup
from requests import get


def match_soup_class(self, target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def main():
    '''
    01 : Seoul
    02 : Busan
    '''
    config = configparser.ConfigParser()
    config.readfp(open('../ft.ini'))
    rate_of_process_key = config.get('DATA_GO_KR', 'rate_of_process_key', raw=True)
    area_dcd = config.get('DATA_GO_KR', 'area_dcd', raw=True)
    keyword = config.get('DATA_GO_KR', 'keyword', raw=True)

    url = 'http://www.khug.or.kr/rateOfBuildingDistributionApt.do?API_KEY=%s&AREA_DCD=%s' % (
            rate_of_process_key, area_dcd)
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for item in soup.find_all('item'):
        if item.addr.text.find(keyword) >= 0:
            print('주소  :', item.addr.text)
            print('공정률: %s%%' % item.tpow_rt.text)
            print('사업장:', item.bsu_nm.text)
            print('시행사:', item.cust_nm1.text)
            print('시공사:', item.cust_nm2.text)
            print('사업장번호:', item.buno.text)


if __name__ == '__main__':
    main()
