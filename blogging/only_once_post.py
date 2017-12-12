#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
from bs4 import BeautifulSoup
from requests import get

from datetime import datetime
from selenium import webdriver
from seleniumrequests import Chrome


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def _get_rfc_info(soup, rfc_num):
    this_msg = False

    for tr in soup.find_all('tr'):
        try:
            href = tr.a['href']
        except TypeError:
            continue
        for idx, td in enumerate(tr.find_all('td')):
            if idx == 0:
                ts = td.text.strip().split()
                try:
                    num = int(ts[1])
                except ValueError:
                    continue
                if num == rfc_num:
                    this_msg = True
            if this_msg:
                if idx == 2:
                    title = td.text
                    return 'RFC %04d: <a href="%s">%s</a>' % (num, href, title.strip())
    return False


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
    driver.quit()
    return token


def get_rfc_list():
    url = 'https://www.rfc-editor.org/search/rfc_search_detail.php?page=All&pubstatus[]=Any&pub_date_type=any&sortkey=Number&sorting=ASC'
    r = get(url)
    content = ''
    soup = BeautifulSoup(r.text, 'html.parser')
    for i in range(1, 8307):  # 8306
        print(i, ' / 8306')
        result = _get_rfc_info(soup, i)
        if result is False:
            content = '%s<br>RFC %04d: N/A ' % (content, i)
        else:
            content = '%s<br>%s' % (content, result)
    return content


def get_project_euler_problems():
    content = ''
    for i in range(1, 14):  # 2017/12/01 (has 13 page)
        url = 'https://projecteuler.net/archives;page=%d' % i
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for grid in soup.find_all(match_soup_class(['grid'])):
            for idx, td in enumerate(grid.find_all('td')):
                if idx % 3 == 0:
                    num = int(td.text)
                    href = 'https://projecteuler.net/problem=%d' % num
                elif idx % 3 == 1:
                    problem = td.text
                elif idx % 3 == 2:
                    temp = '[%04d] <a href= %s>%s</a>' % (num, href, problem)
                    content = '%s<br>%s' % (content, temp)
                    # print(temp)
    return content


def crwal_nexpert_blog():

    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    driver = webdriver.Chrome(chromedriver_path)
    driver.implicitly_wait(3)

    for i in range(1, 700):
        url = 'http://www.nexpert.net/%d' % i
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        print(url, soup.title.string)
    driver.quit()


def get_nextpert_blog():
    content = ''
    with open('nexpert', 'r') as f:
        for line in f:
            info = line.split()
            title = ' '.join(info[3:])
            if len(title) == 0:
                continue
            # print(info[0], title)
            temp = '<a href= %s>%s</a>' % (info[0], title)
            content = '%s<br>%s' % (content, temp)
    return content


def get_korea_sw_corp_rank():
    content = ''
    with open('stock_rank', 'r') as f:
        for line in f:
            info = line.split()
            temp = '[%04d] <a href= %s>%s</a> %s' % (int(info[0]), info[3], info[1], info[2])
            content = '%s<br>%s' % (content, temp)
    return content


def get_world_openbooks(page):
    result = ''
    url = 'http://www.openbooks.co.kr/html/open/world_02.html?open_gl_id=2&PHPSESSID=c27e1668b6b783a8c97f530f51a1e219&page=%d' % page
    r = get(url)
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    href, thumbnail, infos = '', '', []
    for idx, table in enumerate(soup.find_all('table')):
        if idx < 21 or idx > 60:
            continue

        if idx % 4 == 1:
            for idx, tr in enumerate(table.find_all('tr')):
                for img in tr.find_all('img'):
                    if len(thumbnail) == 0:
                        thumbnail = img['src']
                        thumbnail = 'http://www.openbooks.co.kr/%s' % thumbnail[1:]
                        break
                for td in tr.find_all('td'):
                    if len(href) == 0:
                        try:
                            href = td.a['href']
                            href = 'http://www.openbooks.co.kr/html/open/%s' % href
                        except TypeError:
                            pass
                    if idx == 2:
                        if len(infos) == 0:
                            temp = td.text.strip().split('\n')
                            infos = [x for x in temp if x]
                            # print(infos)
                    elif idx == 9:
                        desc = td.text.strip()
                        # print(infos, thumbnail)
                        # print(desc)
                        # print(href)
                        temp = '<a href="%s"><font color="blue">%s</font></a><br>%s 지음, %s, %s, %s<br>%s<br><br><center><a href="%s"> <img src="%s" width="200" height="250"></a></center>' % (href, infos[0], infos[1], infos[2], infos[3], infos[4], desc, href, thumbnail)
                        result = '%s<br>%s' % (result, temp)
                        del infos[:]
                        href = ''
                        thumbnail = ''
                        break
    return result


def naver_webtoon():
    # XXX: image 로딩이 안되서 이상해보임

    result = ""
    base_url = 'http://m.comic.naver.com'
    url = 'http://m.comic.naver.com/webtoon/weekday.nhn?page=1&week=fin&sort=STAR'
    r = get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    toon_url = []
    for f in soup.find_all(match_soup_class(['lst'])):
        href = '%s%s' % (base_url, f.a['href'])
        if href in toon_url:
            continue
        toon_url.append(href)
        # print(f)
        for img in f.find_all('img'):
            thumbnail = img['src']
            title = img['alt']
        author = f.p.text
        spans = f.find_all('span', attrs={'class': 'txt_score'})
        for span in spans:
            point = span.text

        temp = '<font color="red">%s</font><br>%s, ★ %s<br><br><center><a href="%s"> <img border="0" align="middle" src="%s" width="200" height="250"></a></center>' % (title, author, point, href, thumbnail)
        result = '%s<br><br>%s' % (result, temp)
    return result


def main():
    # 765385 coding
    # 765668 IT news
    # 765395 ETC
    now = datetime.now()
    cur_time = '%4d%02d%02d' % (now.year, now.month, now.day)
    token = get_tistory_token()

    # ######### ########## ########## ########## ########## ##########
    # title = 'RFC 문서 목록[Total: 8179 (20171201)]'
    # content = get_rfc_list()

    # title = '시가총액 규모 순서대로 나열한 국내 IT 기업 목록 (2017년 09)'
    # content = get_korea_sw_corp_rank()

    # title = 'Project Euler 문제 목록'
    # content = get_project_euler_problems()

    # content = get_nextpert_blog()
    # title = '[Nexpert]님의 블로그 글 목록'
    # tistory_post(token, title, content, '765385')  # coding
    # ######### ########## ########## ########## ########## ##########

    title = '[%s] 열린책들 세계문학 모음' % cur_time
    content = ''
    for i in range(1, 25):
        res = get_world_openbooks(i)
        content = '%s<br>%s' % (content, res)
    tistory_post(token, title, content, '765395')  # ETC
    return
    # ######### ########## ########## ########## ########## ##########


if __name__ == '__main__':
    main()
