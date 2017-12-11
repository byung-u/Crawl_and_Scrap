#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup, CData
from requests import get, codes
from random import choice

from pytz import timezone
from datetime import datetime, timedelta
from googletrans import Translator

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko  ) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/  19.0.1084.46'
                'Safari/536.5'), )

def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match

def hacker_news():
    url = 'https://news.ycombinator.com/news?p=3'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(match_soup_class(['athing'])):
        # print(len(f.text), f.text)
        hk_text = f.text.strip()
        for s in f.find_all(match_soup_class(['storylink'])):
            hk_url = s['href']
            break
        hk_result = '%s\n%s' % (f.text, hk_url)
        if len(hk_result) > 140:
            remain_text_len = 140 - len(hk_url) - 5
            hk_text = '%s...' % hk_text[:remain_text_len]
            hk_result = '%s\n%s' % (hk_text, hk_url)
            print('[long]', hk_result)
        else:
            print('[normal]', hk_result)
def dart_fss():
    url = 'http://dart.fss.or.kr/api/search.xml?auth=7281755ea82558ed48977e09111f334e1b7becb8&crp_cd=078000'
    r = get(url)
    # soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    soup = BeautifulSoup(r.content.decode('utf8', 'replace'), 'html.parser')


def mbn_news():
    url = 'http://news.mk.co.kr/newsList.php?sc=30000020'
    r = get(url)
    if r.status_code != codes.ok:
        print('[MBN Realesate] request error')
        return None

    # 아, 인코딩이 너무 다르다..
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    for f in soup.find_all(match_soup_class(['art_list'])):
        rmk_result = '%s\n%s' % (f.a['title'], f.a['href'])
        print(rmk_result)

def openbooks():  # 열린책들
    url = 'http://www.openbooks.co.kr/html/open/world_02.html?page=2'
    r = get(url)
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    # for p in soup.find_all(match_soup_class([''])):
    for table in soup.find_all('table' ):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td'):
                print(td)
        # body > div > table:nth-child(4) > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(5) > td > table > tbody > tr:nth-child(10) > td > table:nth-child(1) > tbody > tr:nth-child(9) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(1) > td:nth-child(2) > a > span
    # for p in soup.find_all(match_soup_class(['new_list', 'new_name'])):

# korea governments list
def main2():
    url = 'http://www.molit.go.kr/USR/NEWS/m_71/lst.jsp'
    r = get(url)
    if r == codes.ok:
        print(r, codes.ok)
    else:
        print('what the')
    return
    soup = BeautifulSoup(r.text, 'html.parser')
    for ll in soup.find_all('tbody'):
        #print(ll.a['href'])
        #print(ll.text)
        #print('---')
        for tr in ll.find_all('tr'):
            try:
                tr.a['href']
            except TypeError:
                continue
            href = 'http://www.molit.go.kr/USR/NEWS/m_71/%s' % tr.a['href']
            print(href)
            print(tr.a.text)
            print('---')


def main3():
    base_url = 'http://www.tta.or.kr/news/'
    url = 'http://www.tta.or.kr/news/tender.jsp'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #s_container > div.scontent > div.content > table > tbody > tr:nth-child(2) > td.t_left > a
    sessions = soup.select('div > table > tbody > tr > td > a')
    for s in sessions:
        # print(s)
        result_url = '%s%s' % (base_url, s['href'])
        print(s.text.strip(), result_url)


def main4():
    base_url = 'http://kostat.go.kr'
    url = 'http://kostat.go.kr/portal/korea/kor_nw/2/1/index.board'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #ct_board > fieldset > table > tbody > tr:nth-child(1) > td.title > a
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        # print(s)
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)


def main6(): # 식약처
    base_url = 'http://www.mfds.go.kr'
    url = 'http://www.mfds.go.kr/index.do?mid=675'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)


    url = 'http://www.mfds.go.kr/index.do?mid=676'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)


def main9(): # 문화재청
    base_url = 'http://www.cha.go.kr'
    url = 'http://www.cha.go.kr/newsBbz/selectNewsBbzList.do?sectionId=b_sec_1&mn=NS_01_02_01'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        print(s)
        continue
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)

    url = 'http://www.cha.go.kr/newsBbz/selectNewsBbzList.do?sectionId=b_sec_1&mn=NS_01_02_02'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)

def main8():
    base_url = 'http://www.ftc.go.kr/news/ftc/'
    url = 'http://www.ftc.go.kr/news/ftc/reportboList.jsp'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        print(s)
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)

    url = 'http://www.ftc.go.kr/news/ftc/reportheList.jsp'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)
'''
<a class="attach-file hangul"
    href="/common/board/Download.do?bcIdx=1003171&amp;cbIdx=86&amp;streFileNm=06f0bee2-909a-4220-850d-f6475a1553fc.hwp"
    title="파일 다운로드">
<img alt="첨부파일 한글파일" src="/images/smba/icon_fileHan.png"/></a>

<class 'bs4.element.Tag'>
<a href="#view" onclick="doBbsFView('86','1003157','16010100','1003157');return false;"
title="4719번글">
										 액셀러레이터도 선배 벤처와 함께 펀드 조성 가능
								</a>
'''
def main8():
    url = 'http://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=86'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        if s.get('onclick') is None:
            continue
        idx = s.get('onclick').replace("'", '').split(',')[1]
        result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=86&bcIdx=%s&parentSeq=%s' % (idx, idx)
        print(s.text.strip(), result_url)

    url = 'http://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=87'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        if s.get('onclick') is None:
            continue
        idx = s.get('onclick').replace("'", '').split(',')[1]
        result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=87&bcIdx=%s&parentSeq=%s' % (idx, idx)
        print(s.text.strip(), result_url)


def main10(): # 
    url = 'http://www.molit.go.kr/USR/tender/m_83/lst.jsp'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for ll in soup.find_all('tbody'):
        for tr in ll.find_all('tr'):
            try:
                tr.a['href']
            except TypeError:
                continue
            href = 'http://www.molit.go.kr/USR/tender/m_83/%s' % tr.a['href'][1:]
            print(href)
            print(tr.a.text)
        

def main11(): # 문화재청
    base_url = 'http://www.cha.go.kr'
    url = 'http://www.cha.go.kr/tenderBbz/selectTenderBbzList.do?mn=NS_01_05'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
                continue
        print(s.text.strip(), result_url)


def main12():
    url = 'http://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=81'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        if s.get('onclick') is None:
            continue
        idx = s.get('onclick').replace("'", '').split(',')[1]
        result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=81&bcIdx=%s&parentSeqa%s' % (idx, idx)
        # result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=86&bcIdx=%s&parentSeq=%s' % (idx, idx)
        print(s.text.strip(), result_url)


def main13():
    url = 'http://www.msit.go.kr/web/msipContents/contents.do?mId=NDU1'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > div > ul > li > a')
    for s in sessions:
        print(s.text.strip(), s['href'])
    #    idx = s.get('onclick').replace("'", '').split(',')[1]
    #    result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=81&bcIdx=%s&parentSeqa%s' % (idx, idx)
    #    # result_url = 'http://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=86&bcIdx=%s&parentSeq=%s' % (idx, idx)
    #    print(s.text.strip(), result_url)

def main14():
    base_url = 'https://www.kisa.or.kr/'
    url = 'https://www.kisa.or.kr/notice/bid_List.jsp'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        result_url = '%s%s' % (base_url, s['href'])
        if len(s.text.strip()) == 0:
            continue
        print(s.text.strip(), result_url)


def main15():
    base_url = 'https://www.kisa.or.kr/'
    url = 'http://www.nia.or.kr/site/nia_kor/ex/bbs/List.do?cbIdx=78336'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > ul > li > a')
    #sub_contentsArea > div.board_type01 > ul > li:nth-child(1) > a > span.subject.searchItem
    for s in sessions:
        if s.get('onclick') is None:
            continue
        idx = s.get('onclick').replace("'", '').split(',')[1]

        result_url = 'http://www.nia.or.kr/site/nia_kor/ex/bbs/View.do?cbIdx=78336&bcIdx=%s&parentSeq=%s' % (idx, idx)
        title = s.text.replace('\r\n', '').split()
        print(' '.join(title[:-5]), result_url)

        # print(s.text.strip(), s.get('onclick'))
def main16():
    base_url = 'http://www.kdata.or.kr/board'
    url = 'http://www.kdata.or.kr/board/notice_01.html'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > a')
    for s in sessions:
        result_url = '%s/%s' % (base_url, s['href'])
        print(s.text.strip(), result_url)

def main17():
    base_url = 'https://www.kitech.re.kr/bbs'
    url = 'https://www.kitech.re.kr/bbs/page2-1.php'
    # r = get(url, headers={'User-Agent': choice(USER_AGENTS)})
    r = get(url, verify=False)
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')

    for tr in soup.find_all('tr'):
        try:
            tr.a['href']
        except TypeError:
            continue
        # href = 'http://www.molit.go.kr/USR/NEWS/m_71/%s' % tr.a['href']
        # print(href)
        result_url = '%s/%s' % (base_url, tr.a['href'])
        print(tr.a.text)
        print(result_url)

def main18():
    url = 'http://www.nst.re.kr/nst/notice/02_02.jsp'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > ul > li > a')
    for s in sessions:
        title = s.text.replace('\r\n', '').split()
        if len(title) < 6:
            continue
        result_url = '%s%s' % (url, s['href'])
        print(' '.join(title[3:]), result_url)

def main19():
    url = 'http://www.nst.re.kr/nst/notice/02_04.jsp'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > ul > li > a')
    for s in sessions:
        title = s.text.replace('\r\n', '').split()
        if len(title) < 6:
            continue
        result_url = '%s%s' % (url, s['href'])
        print(' '.join(title[3:]), result_url)

def main16():
    msg = 'goo.gl/yajmVc  (변경공고)2018년 한국에너지기술연구원 통합정보시스템 유지관리 용역사업 #정부출(변경공고)2018년 한국에너지기술연구원 통합정정보시스템 유지관리 용역사업 #정부출...보시스템 유지관리 용역사업 #정부출..정보시스템 유지관리 용역사업 #정부출...정보시스템 유지관리 용역사업 #정부출....'
    limit_len = 140
    print(len(msg))
    msg_len = len(msg)
    over_len = msg_len - limit_len + 3 + 2
    msg = msg[:-over_len]
    print(over_len)
    print(len(msg))

def main17():
    '''
    Thema A to J
    거시/금융, 재정/복지, 노동/교육, 국제/무역, 산업조직, 
    경제발전/성장, 북한경제/경제체계, 농업/환경/자원, 지역경제, 기타
    '''
    thema = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    base_url = 'http://www.kdi.re.kr'
    for t in thema:
        url = 'http://www.kdi.re.kr/research/subjects_list.jsp?tema=%s' % t
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        sessions = soup.select('li > div > a')
        # li.Js_AjaxParents:nth-child(1) > div:nth-child(1) > a:nth-child(3)
        for s in sessions:
            result_url = '%s%s' % (base_url, s['href'])
            print(s.text.strip(), result_url)


def rfc_document():
    # root_url = 'http://goodmonitoring.com'
    url = 'https://www.rfc-editor.org/current_queue.php'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup)
    rfc_draft_msg = []
    
    for n in soup.find_all(match_soup_class(['narrowcolumn'])):
        # print(len(n.text), n.text)
        for tr in n.find_all('tr'):
            try:
                tr.a['href']
            except TypeError:
                continue
            cnt = 0
            for td in tr.find_all('td'):
                if cnt == 0:
                    if td.text.find('AUTH48-DONE') == -1:
                        break
                    else:
                        state = td.text
                elif cnt == 3:
                    title = td.text.split()
                    version = title[0].split('-')
                    #print(version[-1])
                    for b in tr.find_all('b'):
                        #print('b:', b.a['href'])
                        rfc_draft = '[%s]\n%s(ver:%s)\n%s' % (
                                state.strip(),
                                '-'.join(version[1:-1]), 
                                version[-1], 
                                b.a['href'],
                                )
                        rfc_draft_msg.append(rfc_draft)
                cnt += 1
    #print(rfc_draft_msg)                            
    for i in range(len(rfc_draft_msg)):
        print(len(rfc_draft_msg[i]), rfc_draft_msg[i])



def tech6():
    url = 'http://d2.naver.com/d2.atom'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for idx, p in enumerate(soup.find_all(['title', 'link'])):
        if idx & 1:
            print(p['href'])
        else:
            print(p.string)


def tech5():
    url = 'http://tech.lezhin.com'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for p in soup.find_all(match_soup_class(['post-item'])):
        desc = p.find(match_soup_class(['post-title']))
        result_url = '%s%s' % (url, p.a['href'])
        print(result_url, desc.string)


def tech4():
    url = 'http://tech.kakao.com'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for p in soup.find_all(match_soup_class(['post'])):
        desc = p.find(match_soup_class(['post-title']))
        result_url = '%s%s' % (url, p.a['href'])
        print(p.a['href'], desc.string)

def tech3():
    base_url = 'http://woowabros.github.io'
    url = 'http://woowabros.github.io/index.html'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for l in soup.find_all(match_soup_class(['list'])):
        for lm in l.find_all(match_soup_class(['list-module'])):
            desc = lm.find(match_soup_class(['post-description']))
            if desc is None:
                continue
            print(desc)
            result_url = '%s%s' % (base_url, lm.a['href'])
            if result_url is None or desc.string is None:
                continue
            print(result_url, desc.string)


def tech2():
    base_url = 'https://spoqa.github.io/'
    url = 'https://spoqa.github.io/index.html'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for p in soup.find_all(match_soup_class(['posts'])):
        for auth in p.find_all(match_soup_class(['post-author-info'])):
            post = auth.find(match_soup_class(['post-title']))
            desc = auth.find(match_soup_class(['post-description']))
            result_url = '%s%s' % (base_url, post.a['href'][1:])
            print(result_url, desc.string)
            print(len(result_url) + len(desc.string))

def tech6():
    base_url = 'https://www.ridicorp.com/'

    url = 'https://www.ridicorp.com/blog/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for l in soup.find_all(match_soup_class(['list-item'])):
        desc = l.find(match_soup_class(['desc']))
        result_url = '%s%s' % (base_url, l['href'])
        print(result_url, desc.string)


def tech7():
    base_url = 'http://tech.whatap.io/'

    url = 'http://tech.whatap.io/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # sessions = soup.select('div.secondary > ul > li > a')
    for w in soup.find_all(match_soup_class(['widget_recent_entries'])):
        for a_tag in w.find_all('a'):
            print(a_tag['href'], a_tag.text)

        # desc = l.find(match_soup_class(['desc']))
        # result_url = '%s%s' % (base_url, l['href'])
        # print(result_url, desc.string)


def tech8():
    #post-13732 > header > h1 > a

    url = 'http://readme.skplanet.com/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('header > h1 > a')
    for s in sessions:
        result_url = '%s%s' % (url, s['href'])
        print(s.text.strip(), result_url)
    return
def tech9():

    #post-3579 > div > div > header > h2 > a
    url = 'http://devpools.kr/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > header > h2 > a')
    for s in sessions:
        print(s.text.strip(), s['href'])
    return


def tech10():
    url = 'https://tyle.io/blog'
    r = get(url)
    #posts-list > a:nth-child(4) > span.post-subject
    #posts-list > a:nth-child(1)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > a')
    for s in sessions:
        try:
            desc = s.span.string
            result_url = '%s%s' % (url, s['href'])
            print(result_url, desc)
        except:
            pass
        # print(s.text.strip(), s['href'])
    return
def tech11():
    base_url = 'http://nuli.navercorp.com'
    url = 'http://nuli.navercorp.com/sharing/blog/main'
    r = get(url)
    #showList > ul > li:nth-child(1) > p.list_title > a
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > ul > li > p > a')
    for s in sessions:
        result_url = '%s%s' % (base_url, s['href'])
        print(s.text.strip(), result_url)
    return


def tech12():
    url = 'http://dev.goodoc.co.kr/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('header > h2 > a')
    for s in sessions:
        print(s.text.strip(), s['href'])
    return
def tech13():
    base_url = 'http://www.netmanias.com'
    url = 'http://www.netmanias.com/ko/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # body > div.clo_contents > div > div > div:nth-child(1) > div > div.mpw_frame.mps_netmanias.cmm_transbox > div.mpc_contents > div:nth-child(3) > div:nth-child(2) > div.mlp_contents > div.mlc_memo.cfs_malgun > div.mls_subject > a
    sessions = soup.select('div > div > div > a')
    for s in sessions:
        if s['href'].find('#cmt') != -1:
            continue
        if s['href'].find('&tag') != -1:
            continue
        if s.string is None:
            continue
        if s['href'].find('id=sponsor') != -1:
            continue
        if s['href'].find('id=sitenews') != -1:
            continue
        if s['href'].find('id=qna') != -1:
            continue
        if s['href'].find('no=') == -1:
            continue
            # print(s['href'], s.string)
        result_url = '%s%s' % (base_url, s['href'])
        print(s.text.strip(), result_url)
    return
def tech14():
    url = 'http://techblog.daliworks.net/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #main > div > article:nth-child(3) > h1 > a
    sessions = soup.select('div > article > h1 > a')
    for s in sessions:
        result_url = '%s%s' % (url, s['href'])
        print(s.text.strip(), result_url)


def tech15():
    url = 'http://blog.dramancompany.com/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #masonry > article.post-749.post.type-post.status-publish.format-standard.hentry.category-develop.post-container.masonry-element.col-md-4 > div.post-article.post-title > h2 > a
    sessions = soup.select('div > h2 > a')
    for s in sessions:
        # print(s)
        # # result_url = '%s%s' % (url, s['href'])
        print(s.text.strip(), s['href'])


def tech16():
    url = 'http://www.boxnwhis.kr/'
    r = get(url)
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    # body > section.recent-posts > ol > li:nth-child(5) > h2 > a
    sessions = soup.select('h2 > a')
    for s in sessions:
        # print(s)
        result_url = '%s%s' % (url, s['href'])
        print(s.text.strip(), result_url)
        # print(s.text.strip(), s['href'])

def tech17():
    url = 'http://tosslab.github.io/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # body > div.container > div > section > ul.posts > li:nth-child(2) > h2 > a
    sessions = soup.select('div > div > section > ul > li > h2 > a')
    for s in sessions:
        # print(s)
        result_url = '%s%s' % (url, s['href'])
        print(s.text.strip(), result_url)
        # print(s.text.strip(), s['href'])


def tech18():
    url = 'http://www.linchpinsoft.com/blog/'
    try:
        r = get(url)
    except:
        print('error')
        return
    print(r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    #main > div.posts-box.posts-box-8 > div > div:nth-child(1) > article > div.post-details > h2 > a
    sessions = soup.select('div > h2 > a')
    for s in sessions:
        # print(s)
        # result_url = '%s%s' % (url, s['href'])
        # print(s.text.strip(), result_url)
        print(s.text.strip(), s['href'])


def tech19():
    base_url = 'https://academy.realm.io'
    url = 'https://academy.realm.io/kr/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #tweets-slider-wrap > div > div > div.article.col-xs-12.col-sm-2.card.micro.flex.center.js-post-toggle.slick-slide.slick-current.slick-active > div > div > a.news-headline.col-xs-12.col-sm-11.text-center
    sessions = soup.select('div > div > div > div > a')
    # sessions = soup.select('div > div > a')
    for s in sessions:
        if len(s.text.strip()) < 5:
            continue
        # print(s)
        result_url = '%s%s' % (base_url, s['href'])
        print(s.text.strip(), result_url)
        # print(s.text.strip(), s['href'])
def tech20():
    url = 'http://www.awskr.org/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    print(soup.resultcode)
    return
    #post-9481 > header > h1 > a
    sessions = soup.select('header > h1 > a')
    for s in sessions:
        # print(s)
        # result_url = '%s%s' % (base_url, s['href'])
        # print(s.text.strip(), result_url)
        print(s.text.strip(), s['href'])


def medium_post_search():
    url = 'https://medium.com/topic/popular'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    print(soup)


def medium_post():
    url = 'https://medium.com/personal-growth/the-secret-algorithm-behind-learning-7c6f4eb702df'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    t = Translator()
    print(soup.title)
    for s in soup.find_all(match_soup_class(['section'])):
        line = s.text
        result = t.translate(line, dest='ko')
        print(result.text)


def linux_today():
    tz = timezone('US/Eastern')
    now = datetime.now(tz)
    today = '%02d' % now.day
    url = 'https://www.linuxtoday.com/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > div > div')
    for s in sessions:
        try:
            span = s.span.text
        except:
            continue
        # if today != span.split()[1][0:2]:
        #     continue
        try:
            href = s.a['href']
        except:
            continue
        # print(href, s.a.text)

        r_article = get(href)
        soup_article = BeautifulSoup(r_article.text, 'html.parser')
        for article in soup_article.find_all(match_soup_class(['article'])):
            for idx, ps in enumerate(article.find_all('p')):
                if idx == 0:
                    summary = ps.text
                elif idx == 1:
                    complete_href = ps.a['href']
            print(summary, complete_href)


def hackernoon():
    url = 'https://hackernoon.com/latest'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > div > div > div > div > div > div > div > div > div > a')
    # sessions = soup.select('div > div > div > div > div > div > div > div > div > div > div > a > section > div')
    for s in sessions:
        try:
            href = s['href']
        except:
            continue

        r_article = get(href)
        soup_article = BeautifulSoup(r_article.text, 'html.parser')
        for article in soup_article.find_all(match_soup_class(['article'])):
            print(article.p.text)
        break
    #_obv\2e shell\2e _surface_1512624430555 > div > div.container.u-maxWidth1040 > div > div.col.u-xs-size12of12.u-size8of12 > div > div > div > div:nth-child(1) > div > div.postArticle-content > a > section > div.section-content
    # print(soup)


def the_guardian():

    now = datetime.now() - timedelta(days=1)
    yesterday = '%4d/%s/%02d' % (now.year, now.strftime("%b").lower(), now.day)

    # t = Translator()

    url = 'https://www.theguardian.com/business/economics'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > div > ul > li > ul > li > div > div > a')
    for s in sessions:

        result = []
        total_len = 0
        text = []
        request_txt = ''

        href = s['href']
        print(href)
        if href.find(yesterday) == -1:
            print('ignore')
        else:
            print('GReeeeeeeeeeaaaaaaaaaaaaat')
        continue
        title = s.text
        ko_title = t.translate(title, dest='ko').text

        a_r = get(href)
        a_soup = BeautifulSoup(a_r.text, 'html.parser')
        for ca in a_soup.find_all(match_soup_class(['content__article-body'])):
            temp_text = ca.text
            break
        temp = temp_text.split('\n')
        article = [t for t in temp if len(t) > 150]

        for line in article:
            total_len += len(line)
            text.append(line)
            if total_len > 4000:
                request_txt = '<br>'.join(text)
                ko_text = t.translate(request_txt, dest='ko').text
                result.append(ko_text)
                del text[:]
                total_len = 0

        request_txt = '<br>'.join(text)
        ko_text = t.translate(request_txt, dest='ko').text
        result.append(ko_text)


        # print(href, title)
        # TODO:
        break
    #\36 -december-2017 > div > div.fc-container--rolled-up-hide.fc-container__body > div > ul > li:nth-child(3) > ul > li:nth-child(1) > div > div > a
    
def nikkei():
    article = []
    t = Translator()
    base_url = 'https://www.nikkei.com'
    url = 'https://www.nikkei.com/'

    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = ''
    for m in soup.find_all(match_soup_class(['m-miM09'])):
        for idx, atag in enumerate(m.find_all('a')):
            if idx != 0:
                continue

            temp = m.text.split('\n')
            title = [t for t in temp if len(t) > 0]
            print(title[0])
        
            try:
                href = atag['href']
            except TypeError:
                continue
            link = '%s%s' % (base_url, href)
            for img in atag.find_all('img'):
                try:
                    img_link = '%s%s' % (base_url, img['src'])
                    break
                except TypeError:
                    continue

            a_r = get(link)
            a_soup = BeautifulSoup(a_r.text, 'html.parser')
            for article_text in a_soup.find_all(match_soup_class(['cmn-article_text'])):
                for ps in article_text.find_all('p'):
                    if len(ps.text) < 30:  # maybe image comment
                        continue
                    article.append(ps.text)

            result, text = [], []
            total_len = 0
            request_txt = ''
            for line in article:
                total_len += len(line)
                text.append(line)
                if total_len > 4000:
                    request_txt = '<br>'.join(text)
                    ko_text = t.translate(request_txt, src='ja', dest='ko').text
                    result.append(ko_text)
                    del text[:]
                    total_len = 0

            request_txt = '<br>'.join(text)
            ko_text = t.translate(request_txt, dest='ko').text
            result.append(ko_text)
            print(result)
            return

            # print(idx, atag)

    
if __name__ == '__main__':
    nikkei()
    # hackernoon()
    # medium_post_search()
    # medium_post()

    # FINISH
    # linux_today()
    # the_guardian()
