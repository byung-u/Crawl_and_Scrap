#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get, codes
from time import gmtime, strftime

from ft_defaults import MAX_TWEET_MSG
from ft_naver import UseNaver
from ft_sqlite3 import UseSqlite3


def check_duplicate(etc_type, etc_info):
    s = UseSqlite3('etc')

    etc_info = etc_info.replace('\"', '\'')  # for query failed
    ret = s.already_sent_etc(etc_type, etc_info)
    if ret:
        print('already exist: ', etc_type, etc_info)
        return True

    s.insert_etc(etc_type, etc_info)
    return False


def is_exist_interesting_keyword(keyword):
    if (keyword.find('마포') >= 0 or
            keyword.find('자이') >= 0 or
            keyword.find('대출') >= 0 or
            keyword.find('부동산') >= 0 or
            keyword.find('규제') >= 0 or
            keyword.find('분양') >= 0):
        # print('Got it!:', keyword)
        return True
    else:
        # print('Nope:', keyword)
        return False


def get_coex_exhibition(ft):
    n = UseNaver(ft)
    url = 'http://www.coex.co.kr/blog/event_exhibition?list_type=list'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    result_msg = []
    exhibition_url = 'http://www.coex.co.kr/blog/event_exhibition'
    for a in soup.find_all('a', href=True):
        if a['href'].startswith(exhibition_url) is False:
            continue
        exhibition_encode = a.text.encode('utf-8')
        if len(exhibition_encode) < 20:
            # TODO : 다음페이지 ignore -> ?
            continue

        short_url = n.naver_shortener_url(ft, a['href'])
        if (check_duplicate('coex', short_url)):
            continue

        exhibition = a.text.splitlines()
        result = '%s\n%s\n\n%s\n%s\n요금:%s' % (
                exhibition[3],
                short_url,
                exhibition[4],
                exhibition[6],
                exhibition[5].lstrip('\\'))
        ex_encode = result.encode('utf-8')
        if len(ex_encode) > MAX_TWEET_MSG:
            # one more try
            result = '%s\n%s' % (
                    exhibition[3],
                    exhibition[4])
            ex_encode = result.encode('utf-8')
            if len(ex_encode) > MAX_TWEET_MSG:
                print('over 140char: ', result)
                continue
        result_msg.append(result)

    return result_msg


"""
sort :
    activity – last_activity_date
    creation – creation_date
    votes – score
    relevance – matches the relevance tab on the site itself

intitle : search keyword (ex. quick sort)
"""


def search_stackoverflow(ft, sort='activity', lang='python'):
    n = UseNaver(ft)

    STACK_EXCHANGE_API_URL = "https://api.stackexchange.com"
    r = get(STACK_EXCHANGE_API_URL + "/search", {
        "order": "desc",
        "sort": sort,
        "tagged": lang,
        "site": "stackoverflow",
        "intitle": lang,
    }).json()
    result_msg = []
    for i in range(len(r["items"])):
        if r["items"][i]["score"] <= 1:
            continue

        short_url = n.naver_shortener_url(ft, r["items"][i]["link"])
        if (check_duplicate('stackoverflow', short_url)):
            continue

        result = '[▲ %s]\n%s\n%s\n' % (
                r["items"][i]["score"],
                r["items"][i]["title"],
                short_url)

        so_encode = result.encode('utf-8')
        if len(so_encode) > MAX_TWEET_MSG:
            continue
        result_msg.append(result)
    return result_msg


def search_nate_ranking_news(ft):
    url = 'http://news.nate.com/rank/interest?sc=its&p=day&date=%s' % (
            strftime("%Y%m%d", gmtime()))

    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    result_msg = []
    # Rank 1~5
    for news_rank in soup.find_all(ft.match_soup_class(['mduSubjectList'])):
        result = '%s\n%s\n%s\n\n' % (
            news_rank.em.text,
            news_rank.strong.text,
            news_rank.a['href'],
            )

        result_msg.append(result)

    # Rank 6~30
    i = 6
    for news_rank in soup.find_all(
            ft.match_soup_class(['mduSubject', 'mduRankSubject'])):
        for news in news_rank.find_all('a'):
            result = '%d위\n%s\n%s\n' % (
                i,
                news.text,
                news['href'],
                )
            i += 1
            result_msg.append(result)
    return result_msg


def get_naver_popular_news(ft):
    now = datetime.now()
    date = '%4d%02d%02d' % (now.year, now.month, now.day)

    url = 'http://news.naver.com/main/list.nhn?sid1=001&mid=sec&mode=LSD&date=%s' % date
    r = get(url)
    if r.status_code != codes.ok:
        print('request error, code=%d' % r.status_code)
        return

    n = UseNaver(ft)
    result_msg = []

    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['type02'])):
        for li in f.find_all('li'):

            if is_exist_interesting_keyword(li.a.text) is False:
                continue
            if (check_duplicate('naver', li.a.text)):
                continue
            short_url = n.naver_shortener_url(ft, li.a['href'])
            result = '%s\n%s' % (li.a.text, short_url)

            n_encode = result.encode('utf-8')
            if len(n_encode) > MAX_TWEET_MSG:
                result = short_url
            result_msg.append(result)
    return result_msg


def get_national_museum_exhibition(ft):  # NATIONAL MUSEUM OF KOREA
    n = UseNaver(ft)
    MUSEUM_URL = 'https://www.museum.go.kr'
    nm_result_msg = []

    url = 'https://www.museum.go.kr/site/korm/exhiSpecialTheme/list/current?listType=list'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['list_sty01'])):
        for li in f.find_all('li'):
            p = li.p.text.split()
            period = ''.join(p[:3])
            title = li.a
            ex_url = '%s%s' % (MUSEUM_URL, title['href'])
            exhibition = None
            for img in li.find_all('img', alt=True):
                exhibition = img['alt']
            if exhibition is None:
                continue

            if (check_duplicate('national_museum', ex_url)):
                continue
            nm_short_url = n.naver_shortener_url(ft, ex_url)
            nm_result = '%s\n%s\n%s' % (period, exhibition, nm_short_url)
            nm_result_msg.append(nm_result)
    return nm_result_msg


def get_realestate_daum(ft):
    n = UseNaver(ft)
    url = 'http://realestate.daum.net/news'
    r = get(url)
    if r.status_code != codes.ok:
        print('request error, code=%d' % r.status_code)
        return None
    rd_result_msg = []

    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['link_news'])):
        if is_exist_interesting_keyword(f.text) is False:
            continue
        rd_url = f['href']
        if (check_duplicate('realestate_daum', f.text)):
            continue
        rd_short_url = n.naver_shortener_url(ft, rd_url)
        rd_result = '%s\n%s' % (f.text, rd_short_url)
        rd_result_msg.append(rd_result)
    return rd_result_msg


def get_realestate_mk(ft):  # maekyung (MBN)
    n = UseNaver(ft)
    url = 'http://news.mk.co.kr/newsList.php?sc=30000020'
    r = get(url)
    if r.status_code != codes.ok:
        print('request error, code=%d' % r.status_code)
        return None
    rmk_result_msg = []

    # 아, 인코딩이 너무 다르다..
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'))
    for f in soup.find_all(ft.match_soup_class(['art_list'])):
        mk_title = f.a['title']

        if is_exist_interesting_keyword(mk_title) is False:
            continue
        rmk_url = f.a['href']
        if (check_duplicate('realestate_mk', mk_title)):
            continue

        rmk_short_url = n.naver_shortener_url(ft, rmk_url)
        rmk_result = '%s\n%s' % (f.a['title'], rmk_short_url)
        rmk_result_msg.append(rmk_result)
    return rmk_result_msg


def get_rate_of_process_sgx(ft):
    url = 'http://www.khug.or.kr/rateOfBuildingDistributionApt.do?API_KEY=%s&AREA_DCD=%s' % (
            ft.rate_of_process_key, ft.area_dcd)
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for item in soup.find_all('item'):
        if item.addr.text.find(ft.keyword) >= 0:
            msg = '%s(%s)\n%s' % (item.addr.text, item.tpow_rt.text, item.bsu_nm.text)
            return msg


def get_hacker_news(ft):  # not popular rank 61~90
    n = UseNaver(ft)
    hn_result_msg = []

    url = 'https://news.ycombinator.com/news?p=3'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['athing'])):
        hn_text = f.text.strip()
        for s in f.find_all(ft.match_soup_class(['storylink'])):
            hn_url = s['href']
            hn_short_url = n.naver_shortener_url(ft, hn_url)
            break
        hn_result = '%s\n%s' % (f.text, hn_short_url)
        if len(hn_result) > MAX_TWEET_MSG:
            remain_text_len = MAX_TWEET_MSG - len(hn_short_url) - 5
            hn_text = '%s...' % hn_text[:remain_text_len]
            hn_result = '%s\n%s' % (hn_text, hn_short_url)

        if (check_duplicate('hacker_news', hn_short_url)):
            continue
        hn_result_msg.append(hn_result)
    return hn_result_msg
