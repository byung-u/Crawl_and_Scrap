#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from requests import get

from ft_naver import UseNaver
from ft_sqlite3 import UseSqlite3

MAX_TWEET_MSG = 140


def check_duplicate(etc_type, etc_info):
    s = UseSqlite3()

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
