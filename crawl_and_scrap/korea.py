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

    def result_tweet(self, bw, msg, result_url, name):
        if bw.is_already_sent('KOREA', result_url):
            bw.logger.info('Already sent: %s', result_url)
            return

        short_url = bw.shortener_url(result_url)
        if short_url is None:
            short_url = result_url

        result = '%s\n%s\n\n#%s' % (msg, short_url, name)
        bw.post_tweet(result, name)
        return

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

            infos = re.split('<', item)
            result = []
            for idx, info in enumerate(infos):
                if idx == 9 or idx == 10:
                    continue
                info = info.replace('>', ' ')
                if len(info) == 0:
                    continue
                info = info.split()
                if idx == 1:
                    price = info[1].split(',')
                    if price[1] == '000':
                        d, m = divmod(int(price[0]), 10)
                        temp = '%d억 %d천' % (d, m)
                        result.append(temp)
                    else:
                        result.append(' '.join(info[1:]))
                else:
                    result.append(' '.join(info[1:]))

            if result[3] not in bw.apt_dong:
                continue
            # if info[4].find(bw.apt_trade_apt) == -1:
            #     continue
            ret_msg = '%s %s %s층(%sm²)\n\n[매매] %s만원\n[준공] %s년\n[거래] %s년 %s월 %s\n' % (
                result[3], result[4], result[8], result[7],
                result[0],
                result[1],
                result[2], result[5], result[6])

            if bw.is_already_sent('KOREA', ret_msg):
                bw.logger.info('Already sent: %s', ret_msg)
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
                bw.logger.info('Already sent: %s', ret_msg)
                continue
            bw.post_tweet(ret_msg, 'Realestate')

    def get_tender_cha(self, bw):  # 문화재청
        base_url = 'http://www.cha.go.kr'
        url = 'http://www.cha.go.kr/tenderBbz/selectTenderBbzList.do?mn=NS_01_05'
        r = bw.request_and_get(url, 'CHA')
        if r is None:
            return

        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '문화재청')

    def get_cha_news(self, bw):  # 문화재청
        base_url = 'http://www.cha.go.kr'
        url = 'http://www.cha.go.kr/newsBbz/selectNewsBbzList.do?sectionId=b_sec_1&mn=NS_01_02_01'
        r = bw.request_and_get(url, 'CHA')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '문화재청(보도)')

        url = 'http://www.cha.go.kr/newsBbz/selectNewsBbzList.do?sectionId=b_sec_1&mn=NS_01_02_02'
        r = bw.request_and_get(url, 'CHA')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '문화재청(해명)')

    def get_ftc_news(self, bw):  # 공정관리위원회
        base_url = 'http://www.ftc.go.kr/news/ftc/'
        url = 'http://www.ftc.go.kr/news/ftc/reportboList.jsp'
        r = bw.request_and_get(url, 'FTC')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '공정위(보도)')

        url = 'http://www.ftc.go.kr/news/ftc/reportheList.jsp'
        r = bw.request_and_get(url, 'FTC')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '공정위(해명)')

    def get_mfds_news(self, bw):  # 식약처
        base_url = 'http://www.mfds.go.kr'
        url = 'http://www.mfds.go.kr/index.do?mid=675'
        r = bw.request_and_get(url, 'MFDS')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '식약처(보도)')

        url = 'http://www.mfds.go.kr/index.do?mid=676'
        r = bw.request_and_get(url, 'MFDS')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '식약처(해명)')

    def get_tender_tta(self, bw):  # 한국정보통신기술협회 입찰공고
        base_url = 'http://www.tta.or.kr/news/'
        url = 'http://www.tta.or.kr/news/tender.jsp'
        r = bw.request_and_get(url, 'TTA')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # s_container > div.scontent > div.content > table > tbody > tr:nth-child(2) > td.t_left > a
        sessions = soup.select('div > table > tbody > tr > td > a')
        for s in sessions:
            # print(s)
            result_url = '%s%s' % (base_url, s['href'])
            # print(s.text.strip(), result_url)
            self.result_tweet(bw, s.text.strip(), result_url, '한국정보통신기술협회')

    def get_tender_molit(self, bw):  # 국토교통부 입찰공고
        url = 'http://www.molit.go.kr/USR/tender/m_83/lst.jsp'
        r = bw.request_and_get(url, 'MOLIT')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for ll in soup.find_all('tbody'):
            for tr in ll.find_all('tr'):
                try:
                    tr.a['href']
                except TypeError:
                    continue
                href = 'http://www.molit.go.kr/USR/tender/m_83/%s' % tr.a['href'][1:]
                self.result_tweet(bw, tr.a.text, href, '국토부')

    def get_molit_news(self, bw):  # 국토교통부 보도자료
        url = 'http://www.molit.go.kr/USR/NEWS/m_71/lst.jsp'
        r = bw.request_and_get(url, 'MOLIT')
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
                self.result_tweet(bw, tr.a.text, href, '국토부')

    def get_noti_mss(self, bw):  # 중소벤처기업부
        url = 'http://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=81'
        r = bw.request_and_get(url, 'MSS')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            if s.get('onclick') is None:
                continue
            idx = s.get('onclick').replace("'", '').split(',')[1]
            result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=81&bcIdx=%s&parentSeqa%s' % (idx, idx)
            self.result_tweet(bw, s.text.strip(), result_url, '중소벤처기업부')

    def get_mss_news(self, bw):  # 중소벤처기업부
        url = 'http://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=86'
        r = bw.request_and_get(url, 'MSS')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            if s.get('onclick') is None:
                continue
            idx = s.get('onclick').replace("'", '').split(',')[1]
            result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=86&bcIdx=%s&parentSeq=%s' % (idx, idx)
            self.result_tweet(bw, s.text.strip(), result_url, '중소벤처기업부(보도)')

        url = 'http://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=87'
        r = bw.request_and_get(url, 'MSS')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            if s.get('onclick') is None:
                continue
            idx = s.get('onclick').replace("'", '').split(',')[1]
            result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=87&bcIdx=%s&parentSeq=%s' % (idx, idx)
            self.result_tweet(bw, s.text.strip(), result_url, '중소벤처기업부(해명)')

    def get_kostat_news(self, bw):  # 통계청

        base_url = 'http://kostat.go.kr'
        url = 'http://kostat.go.kr/portal/korea/kor_nw/2/1/index.board'
        r = bw.request_and_get(url, 'KOSTAT')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        # ct_board > fieldset > table > tbody > tr:nth-child(1) > td.title > a
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            # print(s)
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                    continue
            self.result_tweet(bw, s.text.strip(), result_url, '통계청')

    def get_visit_korea(self, bw):  # 대한민국 구석구석 행복여행
        base_url = 'http://korean.visitkorea.or.kr/kor/bz15/where/festival'
        url = 'http://korean.visitkorea.or.kr/kor/bz15/where/festival/festival.jsp'
        r = bw.request_and_get(url, 'VISIT_KOREA')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for s in soup.find_all(bw.match_soup_class(['item'])):
            if s.h3 is None:
                continue
            result_url = '%s/%s' % (base_url, s.a['href'])
            if bw.is_already_sent('KOREA', result_url):
                bw.logger.info('Already sent: %s', result_url)
                continue
            desc = repr(s.h3)[4: -6]
            for info in s.find_all(bw.match_soup_class(['info2'])):
                for span in info.find_all('span', {'class': 'date'}):
                    short_url = bw.shortener_url(result_url)
                    if short_url is None:
                        short_url = result_url
                    ret_msg = '%s\n%s\n%s\n#visitkorea' % (span.text, desc, short_url)
                    bw.post_tweet(ret_msg, 'VISIT_KOREA')
                    break

    def get_tender_kisa(self, bw):  # 한국인터넷진흥원
        base_url = 'https://www.kisa.or.kr/'
        url = 'https://www.kisa.or.kr/notice/bid_List.jsp'
        r = bw.request_and_get(url, 'KISA')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            if len(s.text.strip()) == 0:
                continue
            self.result_tweet(bw, s.text.strip(), result_url, '한국인터넷진흥원')

    def get_tender_nia(self, bw):  # 한국정보화진흥원
        url = 'http://www.nia.or.kr/site/nia_kor/ex/bbs/List.do?cbIdx=78336'
        r = bw.request_and_get(url, 'NIA')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('div > ul > li > a')
        for s in sessions:
            if s.get('onclick') is None:
                continue
            title = s.text.replace('\r\n', '').split()
            idx = s.get('onclick').replace("'", '').split(',')[1]

            result_url = 'http://www.nia.or.kr/site/nia_kor/ex/bbs/View.do?cbIdx=78336&bcIdx=%s&parentSeq=%s' % (idx, idx)
            self.result_tweet(bw, ' '.join(title[:-5]), result_url, '한국정보화진흥원')

    def get_tender_kdata(self, bw):  # 한국데이터진흥원
        base_url = 'http://www.kdata.or.kr/board'
        url = 'http://www.kdata.or.kr/board/notice_01.html'
        r = bw.request_and_get(url, 'KDATA')
        if r is None:
            return

        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('table > tbody > tr > td > a')
        for s in sessions:
            result_url = '%s/%s' % (base_url, s['href'])
            self.result_tweet(bw, s.text.strip(), result_url, '한국데이터진흥원')

    def get_tender_kitech(self, bw):  # 한국생산기술연구원
        base_url = 'https://www.kitech.re.kr/bbs'
        url = 'https://www.kitech.re.kr/bbs/page2-1.php'
        r = get(url, verify=False)
        if r is None:
            return

        soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
        for tr in soup.find_all('tr'):
            try:
                tr.a['href']
            except TypeError:
                continue
            result_url = '%s/%s' % (base_url, tr.a['href'])
            if bw.is_already_sent('KOREA', result_url):
                bw.logger.info('Already sent: %s', result_url)
                continue
            short_url = bw.shortener_url(result_url)
            if short_url is None:
                short_url = result_url
            ret_msg = '%s\n%s\n#한국생산기술연구원' % (tr.a.text, short_url)
            bw.post_tweet(ret_msg, 'KITECH')

    def get_tender_nst(self, bw):  # 국가과학기술연구회 소관 25개 정부출연연구기관
        url = 'http://www.nst.re.kr/nst/notice/02_02.jsp'
        r = bw.request_and_get(url, 'NST')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('div > ul > li > a')
        for s in sessions:
            title = s.text.replace('\r\n', '').split()
            if len(title) < 6:  # ignore ['통합검색'] /nst/utill/search.jsp
                continue
            result_url = '%s%s' % (url, s['href'])
            # print(' '.join(title[3:]), result_url)
            self.result_tweet(bw, ' '.join(title[3:]), result_url, '정부출연연구기관')

    def get_recruit_nst(self, bw):  # 국가과학기술연구회 소관 25개 정부출연연구기관
        url = 'http://www.nst.re.kr/nst/notice/02_04.jsp'
        r = bw.request_and_get(url, 'NST')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('div > ul > li > a')
        for s in sessions:
            title = s.text.replace('\r\n', '').split()
            if len(title) < 6:  # ignore ['통합검색'] /nst/utill/search.jsp
                continue
            result_url = '%s%s' % (url, s['href'])
            self.result_tweet(bw, ' '.join(title[3:]), result_url, '정부출연연구기관')

    def get_kdi_research(self, bw):  # 한국개발연구원
        '''
        Thema A to J
        거시/금융, 재정/복지, 노동/교육, 국제/무역, 산업조직,
        경제발전/성장, 북한경제/경제체계, 농업/환경/자원, 지역경제, 기타
        '''
        thema = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        base_url = 'http://www.kdi.re.kr'
        for t in thema:
            url = 'http://www.kdi.re.kr/research/subjects_list.jsp?tema=%s' % t
            r = bw.request_and_get(url, 'KDI')
            if r is None:
                continue

            soup = BeautifulSoup(r.text, 'html.parser')
            sessions = soup.select('li > div > a')
            # li.Js_AjaxParents:nth-child(1) > div:nth-child(1) > a:nth-child(3)
            for s in sessions:
                result_url = '%s%s' % (base_url, s['href'])
                self.result_tweet(bw, s.text.strip(), result_url, 'KDI')
