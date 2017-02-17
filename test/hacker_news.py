#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from requests import get


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def main():
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


if __name__ == '__main__':
    main()
