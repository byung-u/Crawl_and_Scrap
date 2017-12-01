#!/usr/bin/env python3
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get, codes
from selenium import webdriver
from seleniumrequests import Chrome


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def get_realestate_daum():
    url = 'http://realestate.daum.net/news'

    r = get(url)
    if r.status_code != codes.ok:
        print('[daum] request error')
        return None

    result = ""
    news_url = []
    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(match_soup_class(['link_news'])):
        news_url = []
        try:
            href = f['href']
        except:
            continue
        if href in news_url:
            continue
        news_url.append(href)

        title = f.text
        title = title.replace("'", "").replace('"', '').replace('·', ',')
        result = '%s<br><a href="%s">%s<a>' % (result, href, title)
    return result


def get_realestate_mbn():
    result = ""
    url = 'http://news.mk.co.kr/newsList.php?sc=30000020'
    r = get(url)
    if r.status_code != codes.ok:
        print('[mbn] request error')
        return None

    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    news_url = []
    for f in soup.find_all(match_soup_class(['art_list'])):
        if f.a['href'] in news_url:
            continue
        news_url.append(f.a['href'])

        href = f.a['href']
        title = f.a['title']
        title = title.replace("'", "").replace('"', '').replace('·', ',')
        result = '%s<br><a href="%s">%s<a>' % (result, href, title)
    return result


def get_realestate_hankyung():
    result = ""
    url = 'http://land.hankyung.com/'
    r = get(url)
    if r.status_code != codes.ok:
        print('[hankyung] request error')
        return None

    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    news_url = []

    sessions = soup.select('div > h2 > a')
    for s in sessions:
        if s['href'] in news_url:
            continue
        if s['href'] == 'http://www.hankyung.com/news/kisarank/':
            continue
        news_url.append(s['href'])

        href = s['href']
        title = s.text.strip()
        print(title, href)
        title = title.replace("'", "").replace('"', '').replace('·', ',')
        result = '%s<br><a href="%s">%s<a>' % (result, href, title)
    return result


def tistory_post(token, title, content, category):
    webdriver = Chrome()
    response = webdriver.request('POST', 'https://www.tistory.com/apis/post/write', data={"access_token": token, "blogName": "scrapnpost", 'title': title, 'content': content, 'category': category, 'visibility': '2'})
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


def get_financial_einfomax():
    result = ""
    base_url = 'http://news.einfomax.co.kr/news'
    url = 'http://news.einfomax.co.kr/news/articleList.html?sc_section_code=S1N16&view_type=sm'
    r = get(url)
    if r.status_code != codes.ok:
        print('[einfomax] request error')
        return None

    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    news_url = []

    for f in soup.find_all(match_soup_class(['ArtList_Title'])):
        try:
            href = f.a['href']
        except:
            continue
        if href in news_url:
            continue
        news_url.append(href)
        title = f.a.text
        title = title.replace("'", "").replace('"', '').replace('·', ',')
        result = '%s<br><a href="%s/%s">%s<a>' % (result, base_url, href, title)
    return result


def get_financial_chosun():
    result = ""
    url = 'http://biz.chosun.com/index.html'
    r = get(url)
    if r.status_code != codes.ok:
        print('[chosun] request error')
        return None

    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    news_url = []
    for f in soup.find_all(match_soup_class(['mc_art_lst'])):
        for li in f.find_all('li'):
            if li.a['href'].endswith('main_hot3'):
                # 경제, 금융: main_hot1, main_hot2
                break

            try:
                href = li.a['href']
            except:
                continue
            if href in news_url:
                continue
            news_url.append(href)
            title = li.a.text.strip()
            title = title.replace("'", "").replace('"', '').replace('·', ',')
            result = '%s<br><a href="%s">%s<a>' % (result, href, title)
    return result


def get_financial_joins():
    result = ""
    base_url = 'http://news.joins.com'
    url = 'http://news.joins.com/money?cloc=joongang|home|section3'
    r = get(url)
    if r.status_code != codes.ok:
        print('[joins] request error')
        return None

    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    news_url = []
    for f in soup.find_all(match_soup_class(['default_realtime'])):

        for li in f.find_all('li'):
            try:
                href = li.a['href']
            except:
                continue
            if href in news_url:
                continue
            news_url.append(href)
            title = ' '.join(li.text.strip().split()[1:-2])
            title = title.replace("'", "").replace('"', '').replace('·', ',')
            result = '%s<br><a href="%s%s">%s<a>' % (result, base_url, href, title)
    return result


def realestate_news():
    daum_news = get_realestate_daum()
    # print('[DAUm]<br>', daum_news)
    mbn_news = get_realestate_mbn()
    # print('[MBN]<br>', mbn_news)
    hankyung_news = get_realestate_hankyung()
    # print('[HanKyung]<br>', hankyung_news)

    content = '<font color="red">[DAUM]</font>%s<br><br><font color="red">[매일경제]</font>%s<br><br><font color="red">[한국경제]</font>%s<br><br>' % (daum_news, mbn_news, hankyung_news)
    return content


def financial_news():
    einfomax = get_financial_einfomax()
    # print(einfomax)
    chosun = get_financial_chosun()
    # print(chosun)
    joins = get_financial_joins()
    # print(joins)

    content = '<font color="red">[연합인포맥스]</font>%s<br><font color="red">[조선일보]</font>%s<br><font color="red">[중앙일보]</font>%s<br>' % (einfomax, chosun, joins)
    return content


def main():
    now = datetime.now()
    cur_time = '%4d%02d%02d' % (now.year, now.month, now.day)
    token = get_tistory_token()

    title = '[%s] 부동산 뉴스 모음(DAUM, 매일경제, 한국경제)' % cur_time
    content = realestate_news()
    tistory_post(token, title, content, '765348')

    title = '[%s] 경제 금융 뉴스 모음(연합인포맥스, 조선일보, 중앙일보)' % cur_time
    content = financial_news()
    tistory_post(token, title, content, '765357')


if __name__ == '__main__':
    main()
