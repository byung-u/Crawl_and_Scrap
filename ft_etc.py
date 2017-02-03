#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from requests import get
from time import gmtime, strftime

from ft_naver import UseNaver
from ft_sqlite3 import UseSqlite3

MAX_TWEET_MSG = 140


def check_duplicate(etc_type, etc_info):
    s = UseSqlite3()  # TODO: move to caller

    ret = s.already_sent_etc(etc_type, etc_info)
    if ret:
        print('already exist: ', etc_type, etc_info)
        return False

    s.insert_etc(etc_type, etc_info)
    return True


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
        if check_duplicate('coex', short_url) is False:
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
        if check_duplicate('stackoverflow', short_url) is False:
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
