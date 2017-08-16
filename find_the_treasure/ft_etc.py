#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get, codes
from time import gmtime, strftime, time

from find_the_treasure import defaults
from find_the_treasure.ft_naver import UseNaver
from find_the_treasure.ft_sqlite3 import UseSqlite3


def check_duplicate(ft, etc_type, etc_info):
    s = UseSqlite3('etc')

    etc_info = etc_info.replace('\"', '\'')  # for query failed
    ret = s.already_sent_etc(etc_type, etc_info)
    if ret:
        ft.logger.info('Already exist: %s %s', etc_type, etc_info)
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
        return True
    else:
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
        if short_url is None:
            short_url = a['href']
        if (check_duplicate(ft, 'coex', short_url)):
            continue

        exhibition = a.text.splitlines()
        coex_result = '%s\n%s\n\n%s\n%s\n요금:%s' % (
            short_url,
            exhibition[3],
            exhibition[4],
            exhibition[6],
            exhibition[5].lstrip('\\'))
        coex_result = ft.check_max_tweet_msg(coex_result)
        result_msg.append(coex_result)

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
        if short_url is None:
            short_url = r["items"][i]["link"]
        if (check_duplicate(ft, 'stackoverflow', short_url)):
            continue

        so_result = '[▲ %s]\n%s\n%s\n' % (
            r["items"][i]["score"],
            r["items"][i]["title"],
            short_url)
        so_result = ft.check_max_tweet_msg(so_result)
        result_msg.append(so_result)
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
            news_rank.a['href'])

        result_msg.append(result)

    # Rank 6~30
    i = 6
    for news_rank in soup.find_all(
            ft.match_soup_class(['mduSubject', 'mduRankSubject'])):
        for news in news_rank.find_all('a'):
            result = '%d위\n%s\n%s\n' % (
                i,
                news.text,
                news['href'])
            i += 1
            result_msg.append(result)
    return result_msg


def get_naver_popular_news(ft):
    now = datetime.now()
    date = '%4d%02d%02d' % (now.year, now.month, now.day)

    url = 'http://news.naver.com/main/list.nhn?sid1=001&mid=sec&mode=LSD&date=%s' % date
    r = get(url)
    if r.status_code != codes.ok:
        ft.logger.error('[NAVER NEWS] request error, code=%d', r.status_code)
        return

    result_msg = []
    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['type02'])):
        for li in f.find_all('li'):

            if is_exist_interesting_keyword(li.a.text) is False:
                continue
            if (check_duplicate(ft, 'naver', li.a['href'])):
                continue
            n_result = '%s\n%s' % (li.a.text, li.a['href'])
            result_msg.append(n_result)
    return result_msg


def get_national_museum_exhibition(ft):  # NATIONAL MUSEUM OF KOREA
    n = UseNaver(ft)
    MUSEUM_URL = 'https://www.museum.go.kr'
    nm_result_msg = []

    url = 'https://www.museum.go.kr/site/korm/exhiSpecialTheme/list/current?listType=list'
    r = get(url)
    if r.status_code != codes.ok:
        ft.logger.error('[NAVER NEWS] request error, code=%d', r.status_code)
        return

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

            if (check_duplicate(ft, 'national_museum', ex_url)):
                continue
            nm_short_url = n.naver_shortener_url(ft, ex_url)
            if nm_short_url is None:
                nm_short_url = ex_url
            nm_result = '%s\n%s\n%s' % (period, exhibition, nm_short_url)
            nm_result_msg.append(nm_result)
    return nm_result_msg


def get_realestate_daum(ft):
    url = 'http://realestate.daum.net/news'
    r = get(url)
    if r.status_code != codes.ok:
        ft.logger.error(
            '[DAUM Realstate] request error, code=%d', r.status_code)
        return None
    rd_result_msg = []

    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['link_news'])):
        if is_exist_interesting_keyword(f.text) is False:
            continue
        if (check_duplicate(ft, 'realestate_daum', f['href'])):
            continue
        rd_result = '%s\n%s' % (f.text, f['href'])
        rd_result_msg.append(rd_result)
    return rd_result_msg


def get_realestate_mk(ft):  # maekyung (MBN)
    url = 'http://news.mk.co.kr/newsList.php?sc=30000020'
    r = get(url)
    if r.status_code != codes.ok:
        ft.logger.error('[MBN Realesate] request error, code=%d', r.status_code)
        return None
    rmk_result_msg = []

    # 아, 인코딩이 너무 다르다..
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['art_list'])):
        mk_title = f.a['title']

        if is_exist_interesting_keyword(mk_title) is False:
            continue
        if (check_duplicate(ft, 'realestate_mk', f.a['href'])):
            continue
        rmk_result = '%s\n%s' % (f.a['title'], f.a['href'])
        rmk_result_msg.append(rmk_result)
    return rmk_result_msg


def get_rate_of_process_sgx(ft):
    url = 'http://www.khug.or.kr/rateOfBuildingDistributionApt.do?API_KEY=%s&AREA_DCD=%s' % (
        ft.rate_of_process_key, ft.area_dcd)
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for item in soup.find_all('item'):
        if item.addr.text.find(ft.keyword) >= 0:
            msg = '%s(%s)\n%s\n%d' % (
                item.addr.text, item.tpow_rt.text, item.bsu_nm.text,
                int(time()))
            return msg


def get_hacker_news(ft):
    n = UseNaver(ft)
    hn_result_msg = []

    # p=1, rank 16~30
    # p=2, rank 31~45
    url = 'https://news.ycombinator.com/news?p=0'  # rank 1~15
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    cnt = 0
    for f in soup.find_all(ft.match_soup_class(['athing'])):
        cnt += 1
        if cnt > 5:  # 5 articles
            break
        hn_text = f.text.strip()
        for s in f.find_all(ft.match_soup_class(['storylink'])):
            hn_url = s['href']
            if (check_duplicate(ft, 'hacker_news', hn_url)):
                continue
            hn_short_url = n.naver_shortener_url(ft, hn_url)
            if hn_short_url is None:
                hn_short_url = hn_url
            hn_result = '[HackerNews]\n%s\nRank:%s' % (hn_short_url, hn_text)
            hn_result = ft.check_max_tweet_msg(hn_result)
            hn_result_msg.append(hn_result)
            break

    return hn_result_msg


def get_recruit_people_info(ft):  # 각종 모집 공고
    mz_result_msg = []
    root_url = 'http://goodmonitoring.com'
    url = 'http://goodmonitoring.com/xe/moi'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(ft.match_soup_class(['title'])):
        mozip = f.text.strip()
        if mozip == '제목' or mozip.find('대학생') != -1:
            continue
        else:
            mozip_url = '%s%s' % (root_url, f.a['href'])
            if (check_duplicate(ft, 'recruit_people', mozip_url)):
                continue
            mz_result = '%s\n%s' % (mozip, mozip_url)
            mz_result_msg.append(mz_result)

    return mz_result_msg


def get_rfc_draft_list(ft):  # get state 'AUTH48-DONE' only
    url = 'https://www.rfc-editor.org/current_queue.php'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    rfc_draft_msg = []

    for n in soup.find_all(ft.match_soup_class(['narrowcolumn'])):
        for tr in n.find_all('tr'):
            try:
                tr.a['href']
            except TypeError:
                continue
            cnt = 0
            for td in tr.find_all('td'):
                if cnt == 0:  # state
                    # AUTH48-DONE = Final approvals are complete
                    if td.text.find('AUTH48-DONE') == -1:
                        break
                    else:
                        state = td.text
                elif cnt == 3:  # draft name and author, weeks in state/queue
                    title = td.text.split()
                    version = title[0].split('-')
                    for b in tr.find_all('b'):
                        if (check_duplicate(ft, 'rfc', b.a['href'])):
                            continue
                        rfc_draft = '[%s]\n%s(Ver:%s)\n%s' % (
                            state.strip(),
                            '-'.join(version[1:-1]), version[-1],
                            b.a['href'])

                        if len(rfc_draft) > defaults.MAX_TWEET_MSG:
                            rfc_draft = '[%s]\nVer:%s\n%s' % (
                                state.strip(), version[-1], b.a['href'])

                        rfc_draft_msg.append(rfc_draft)
                cnt += 1
    return rfc_draft_msg


def get_raspberripy_news(ft):

    url = 'http://lifehacker.com/tag/raspberry-pi'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    rb_news_msg = []
    for l in soup.find_all(ft.match_soup_class(['postlist__item'])):
        if len(l.a.text) == 0:
            continue
        rb_title = l.a.text
        rb_url = l.a['href']

        if (check_duplicate(ft, 'raspberripy', rb_url)):
            continue

        rb_news = '%s\n%s' % (rb_title, rb_url)
        if len(rb_news) > defaults.MAX_TWEET_MSG:
            rb_news = '%s' % (rb_url)
        rb_news_msg.append(rb_news)

    return rb_news_msg
