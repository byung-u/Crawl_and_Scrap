#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from urllib.request import urlretrieve, Request, urlopen
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup

def replace_all(text):
    rep = { "&lt": "", "&amp": "", "&apos": "", "&quot": "",
            ";": "", "<b>": "", "</b>": "", "&gt": "", "‘": "",
            "’": "", u"\xa0": u"", "“": "", "”": "",
            }
    for i, j in rep.items():
        text = text.replace(i, j)
    return text


def main():
    req_url = u'https://openapi.naver.com/v1/search/news.xml?query=' + quote('XXXXXX') + '&display=100&start=1&sort=date'
    request = Request(req_url)
    request.add_header('X-Naver-Client-Id', 'xxxxxxxxxxxxxxxxxxxx')
    request.add_header('X-Naver-Client-Secret', 'xxxxxxxxxx')
    response = urlopen(request)
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        data = response_body.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')

        msg = [0, 0, 0, 0]
        for i, s in enumerate(soup.find_all(['link', 'title', 'description', 'pubdate'])):
            if i < 5:
                continue
            if i % 4 == 1:  # desc
                msg.append(replace_all(s.text))
            elif i % 4 == 2:  # date Fri, 14 Apr 2017
                msg.append(replace_all(s.text))
                write_msg = '%s\n%s\n%s' % (msg[2], msg[1], msg[0])
                del msg[:]
            elif i % 4 == 3:  # title
                msg.append(replace_all(s.text))
            elif i % 4 == 0:  # url
                msg.append(replace_all(s.text))
    else:
        print('[NAVER news] Error Code: %d', rescode)


if __name__ == '__main__':
    main()
