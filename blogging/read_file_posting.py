#!/usr/bin/env python3
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from googletrans import Translator
from requests import get
from selenium import webdriver
from seleniumrequests import Chrome


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def tistory_post(token, title, content, category):
    webdriver = Chrome()
    response = webdriver.request('POST', 'https://www.tistory.com/apis/post/write', data={"access_token": token, "blogName": "trab", 'title': title, 'content': content, 'category': category, 'visibility': '3'})
    webdriver.quit()
    print(response)


def get_tistory_token():
    # http://www.tistory.com/guide/api/index
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    driver = webdriver.Chrome(chromedriver_path)
    driver.implicitly_wait(3)
    driver.get('https://www.tistory.com/auth/login?redirectUrl=http%3A%2F%2Fwww.tistory.com%2F')
    # <input type="email" id="loginId" name="loginId" class="tf_g" value="" placeholder="이메일 아이디" required="">
    tid = os.environ.get('TISTORY_ID')
    tpw = os.environ.get('TISTORY_PW')
    driver.find_element_by_name('loginId').send_keys(tid)
    # <input type="password" id="loginPw" name="password" class="tf_g" placeholder="비밀번호" required="">
    driver.find_element_by_name('password').send_keys(tpw)
    driver.find_element_by_xpath('//*[@id="authForm"]/fieldset/div/button').click()

    client_id = os.environ.get('TISTORY_CLIENT_ID')
    redirect = os.environ.get('TISTORY_REDIRECT')

    req_url = 'https://www.tistory.com/oauth/authorize/?client_id=%s&redirect_uri=%s&response_type=token' % (client_id, redirect)
    driver.get(req_url)

    ################################################################################
    # XXX: 중요
    # 티스토리는 브라우져 인증이 필요함
    # 맨처음 시도할 때는 아래의 코드의 주석을 풀고 한번 해줘야함
    # driver.find_element_by_xpath('//*[@id="contents"]/div[4]/button[1]').click()
    ################################################################################
    redirect_url = driver.current_url
    print(redirect_url)
    temp = re.split('access_token=', redirect_url)
    token = re.split('&state=', temp[1])[0]
    return token


def linux_today():
    result = ''
    yesterday = datetime.now() - timedelta(days=1)
    # lt_cur_time = '%4d%02d%02d' % (yesterday.year, yesterday.month, yesterday.day)
    lt_today = '%02d' % yesterday.day  # laughly time difference Korea and USA
    t = Translator()

    url = 'https://www.linuxtoday.com/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('table > tbody > tr > td > div > div')
    import sys
    for s in sessions:
        try:
            span = s.span.text
        except AttributeError:
            continue
        if lt_today != span.split()[1][0:2]:
            continue
        try:
            href = s.a['href']
        except AttributeError:
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
                    break
        ko_title = t.translate(s.a.text, dest='ko').text
        ko_article = t.translate(summary, dest='ko').text
        temp = '<a href="%s" target="_blank"><font color="blue">%s</font></a><br>%s<br><a href="%s" target="_blank"><font color="red">🔗 전체내용 Link</font></a><br><div style="border:1px solid grey"><br>%s<br><br>"%s"</div><br><br>' % (href, s.a.text, summary, complete_href, ko_title, ko_article)
        result = '%s<br>%s' % (result, temp)
    return result


def startup_era_end():
    t = Translator()

    total_len = 0
    text = []
    request_txt = ''
    result = []
    with open('startup_is_end') as f:
        for line in f:
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
    f.closed

    return '<br>'.join(result)


if __name__ == '__main__':
    title = '[20171022] 스타트업의 시대가 끝난 이후(After the end of the startup era)'
    content = startup_era_end()
    token = get_tistory_token()
    tistory_post(token, title, content, '766214')
