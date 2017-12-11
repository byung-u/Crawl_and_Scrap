#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
from bs4 import BeautifulSoup
from requests import get

import urllib.request

from datetime import datetime
from selenium import webdriver
# from seleniumrequests import Chrome


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def naver_post(token, title, content):
    header = "Bearer " + token  # Bearer 다음에 공백 추가
    url = "https://openapi.naver.com/blog/writePost.json"
    title = urllib.parse.quote(title)
    contents = urllib.parse.quote(content)
    data = "title=" + title + "&contents=" + contents
    request = urllib.request.Request(url, data=data.encode("utf-8"))
    request.add_header("Authorization", header)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)


def get_naver_token():
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    driver = webdriver.Chrome(chromedriver_path)
    # driver = webdriver.PhantomJS()
    driver.implicitly_wait(3)
    driver.get('https://nid.naver.com/nidlogin.login')

    nid = os.environ.get('NAVER_ID')
    npw = os.environ.get('NAVER_PAW')
    driver.find_element_by_name('id').send_keys(nid)

    driver.find_element_by_name('pw').send_keys(npw)
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

    client_id = os.environ.get('NAVER_BLOG_CLIENT_ID')
    client_secret = os.environ.get('NAVER_BLOG_CLIENT_SECRET')
    state = "REWERWERTATE"
    redirect = os.environ.get('NAVER_BLOG_REDIRECT')
    req_url = 'https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=%s&redirect_uri=%s&state=%s' % (client_id, redirect, state)

    driver.get(req_url)
    ##########################
    # XXX: 최초 1회 수행해서 동의 해야함
    # driver.find_element_by_xpath('//*[@id="confirm_terms"]/a[2]').click()
    ##########################
    redirect_url = driver.current_url
    temp = re.split('code=', redirect_url)
    code = re.split('&state=', temp[1])[0]
    driver.quit()
    print(redirect_url)
    print(code)

    url = 'https://nid.naver.com/oauth2.0/token?'
    data = 'grant_type=authorization_code' + '&client_id=' + client_id + '&client_secret=' + client_secret + '&redirect_uri=' + redirect + '&code=' + code + '&state=' + state

    request = urllib.request.Request(url, data=data.encode("utf-8"))
    request.add_header('X-Naver-Client-Id', client_id)
    request.add_header('X-Naver-Client-Secret', client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    token = ''
    if rescode == 200:
        response_body = response.read()
        js = json.loads(response_body.decode('utf-8'))
        token = js['access_token']
    else:
        print("Error Code:" + rescode)

    if len(token) == 0:
        return None
    print(token)
    return token


def get_naver_celeb():
    result = '<font color="blue">[Naver에서 가장 많이 본 연예뉴스]</font><br>'
    url = 'http://entertain.naver.com/home'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    cnt = 0
    for section in soup.find_all(match_soup_class(['home_hit_grid'])):
        for home in section.find_all(match_soup_class(['rank_news_ct'])):
            href = home.a['href']
            temp = home.find('a', attrs={'class': 'title'})
            title = temp.text.strip()
            temp = home.find('a', attrs={'class': 'summary'})
            summary = ''
            try:
                summary = temp.text.strip()
            except AttributeError:
                pass
            # print(href, title, summary)
            for img in home.find_all('img'):
                thumbnail = img['data-src']
                break

            temp = '<a href="%s" target="_blank"><strong>%d. %s</strong></a><br>%s<br><center><a href="%s" target="_blank"> <img border="0" src="%s" width="150" height="150"></a></center><br>' % (
                   href, cnt + 1, title, summary, href, thumbnail)
            result = '%s<br>%s' % (result, temp)
            cnt += 1
            if cnt == 10:  # 1~5, 5~10(연예), 11~15(audio), 15~20(video)
                return result

    return result


def get_daum_celeb():
    result = '<font color="blue">[Daum에서 가장 많이 본 연예뉴스]</font><br>'
    url = 'http://media.daum.net/entertain'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for section in soup.find_all(match_soup_class(['section_manyhits'])):
        thumbnail = ''
        for l in section.find_all(match_soup_class(['link_cont'])):
            try:
                href = l['href']
            except TypeError or KeyError:
                continue
            for img in l.find_all('img'):
                thumbnail = (img['src'])
                break
            # print(href)
            # print(thumbnail)
            title = l.text.strip().split('\n')
            # print(title[0], ' '.join(title[1:]))
            temp = '<a href="%s" target="_blank"><strong>%s. %s</strong></a><br><center><a href="%s" target="_blank"> <img border="0" src="%s" width="150" height="150"></a></center><br>' % (
                   href, title[0], ' '.join(title[1:]), href, thumbnail)
            result = '%s<br>%s' % (result, temp)
    return result


def get_nate_celeb(cur_time):
    result = '<font color="blue">[Nate에서 가장 많이 본 연예뉴스]</font><br>'
    url = 'http://news.nate.com/rank/interest?sc=ent&p=day&date=%s' % cur_time
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    cnt = 1
    for rank in soup.find_all(match_soup_class(['postRankSubjectList'])):
        for mlt in rank.find_all(match_soup_class(['mlt01'])):
            for img in mlt.find_all('img'):
                thumbnail = (img['src'])
                break
            href = mlt.a['href']
            temp = mlt.text.strip().replace('\t', '')
            title = temp.split('\n')
            # print(title, href, thumbnail)
            temp = '<a href="%s" target="_blank"><strong>%s. %s</strong><br></a><br>%s<br><center><a href="%s" target="_blank"> <img border="0" src="%s" width="150" height="150"></a></center><br>' % (
                   href, cnt, title[0], ' '.join(title[1:]), href, thumbnail)
            result = '%s<br>%s' % (result, temp)
            cnt += 1
    return result


def get_entertainment(cur_time):
    result = ''

    content = get_naver_celeb()
    result = '%s<br>%s' % (result, content)
    content = get_daum_celeb()
    result = '%s<br>%s' % (result, content)
    content = get_nate_celeb(cur_time)
    result = '%s<br>%s' % (result, content)

    return result


def get_hani_car():
    result = '<font color="blue">[한겨례 자동차 뉴스]</font><br>'
    base_url = 'http://www.hani.co.kr'
    url = 'http://www.hani.co.kr/arti/economy/car/home01.html'
    r = get(url)
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for article in soup.find_all(match_soup_class(['article-area'])):
        href = '%s%s' % (base_url, article.a['href'])
        article = article.text.strip().split('\n')
        # print(href, article[0])
        result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, href, article[0])
    return result


def get_nocut_car():
    result = '<font color="blue">[노컷뉴스 자동차 뉴스]</font><br>'
    base_url = 'http://www.nocutnews.co.kr'
    url = 'http://www.nocutnews.co.kr/news/list?c1=203&c2=209&ltype=1'
    r = get(url)
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    news = soup.find(match_soup_class(['newslist']))
    for dt in news.find_all('dt'):
        href = '%s%s' % (base_url, dt.a['href'])
        result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, href, dt.text.strip())
    return result


def get_nate_car():
    result = '<font color="blue">[네이트 자동차 뉴스]</font><br>'
    url = 'http://auto.nate.com/'
    r = get(url)
    # soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    soup = BeautifulSoup(r.text, 'html.parser')
    for news in soup.find_all(match_soup_class(['broadcast_webzine01_list'])):
        for li in news.find_all('li'):
            href = li.a['href']
            result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, href, li.text.strip())
    return result


def get_car(cur_time):
    result = ''

    content = get_hani_car()
    result = '%s<br>%s' % (result, content)
    content = get_nocut_car()
    result = '%s<br>%s' % (result, content)
    content = get_nate_car()
    result = '%s<br>%s' % (result, content)

    return result


def hyundai_curture_center():
    result = '<strong><font color="blue">[현대백화점 문화센터 추천강좌]</font></strong><br><br>'
    base_url = 'https://www.ehyundai.com'
    lcode = {'압구정본점': '210',
             '무역센터점': '220',
             '천호점': '260',
             '신촌점': '270',
             '미아점': '410',
             '목동점': '420',
             '부천중동점': '430',
             '킨텍스점': '450',
             '부산점': '240',
             '울산동구점': '250',
             '울산점': '290',
             '대구점': '460',
             '충청점': '470',
             '판교점': '480',
             '디큐브시티(신도림)점': '490',
             '가든파이브(송파)점': '750', }
    result = '%s<pre>' % result
    cnt = 1
    for location, code in lcode.items():
        part_url = 'http://www.ehyundai.com/newCulture/CT/CT010200_L.do?stCd=%s' % code
        result = '%s<a href="%s" target="_blank">%d. %s</a><br>' % (result, part_url, cnt, location)
        cnt += 1
    result = '%s</pre>' % result

    for location, code in lcode.items():
        result = '%s<br><br><font color="red">[%s]</font><br>' % (result, location)
        url = 'http://www.ehyundai.com/newCulture/CT/CT010200_L.do?stCd=%s' % code
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for best in soup.find_all(match_soup_class(['best_lecturelist'])):
            for li in best.find_all('li'):
                href = '%s%s' % (base_url, li.a['href'])
                date = li.find('span', attrs={'class': 'date'})
                fee = li.find('span', attrs={'class': 'fee'})
                result = '%s<br><strong><a href="%s" target="_blank">%s</a></strong><br>%s<br>%s<br>' % (
                         result, href, li.a.text.strip(), date.text, fee.text)
    return result


def lotte_curture_center():
    result = '<strong><font color="blue">[롯데백화점 문화센터 추천강좌]</font></strong><br><br>'
    lcode = {'본점(명동)': '0001', '잠실점': '0002', '청량리점': '0004',
             '부산본점': '0005', '관악점': '0006', '광주점': '0007',
             '분당점': '0008', '부평점': '0009', '영등포점': '0010',
             '일산점': '0011', '대전점': '0012', '강남점': '0013',
             '포항점': '0014', '울산점': '0015', '동례점': '0016',
             '창원점': '0017', '안양점': '0018', '인천점': '0020',
             '노원점': '0022', '대구점': '0023', '상인점': '0024',
             '전주점': '0025', '미아점': '0026', '센텀시티점': '0027',
             '건대스타시티점': '0028',
             '광복점': '0333', '중동점': '0334', '구리점': '0335',
             '안산점': '0336', '김포공항점': '0340', '평촌점': '0341',
             '수원점': '0349', '마산점': '0354', }

    result = '%s<pre>' % result
    cnt = 1
    for location, code in lcode.items():
        part_url = 'https://culture.lotteshopping.com/CLSS_list.do?taskID=L&pageNo=1&vpStrCd=&vpKisuNo=&vpClassCd=&vpTechNo=&pStrCd=%s&pLarGbn=&pMidGbn=&pClsFee=&pDayGbnAll=&pDayTime=&pStatus=&pKisuValue=C&pClsNm=&pClsNmTemp=&pTechNm=&pTechNmTemp=' % code
        result = '%s<a href="%s" target="_blank">%d. %s</a><br>' % (result, part_url, cnt, location)
        cnt += 1
    result = '%s</pre>' % result
    for location, code in lcode.items():
        result = '%s<br><br><font color="red">[%s]</font><br>' % (result, location)
        url = 'https://culture.lotteshopping.com/CLSS_list.do?taskID=L&pageNo=1&vpStrCd=&vpKisuNo=&vpClassCd=&vpTechNo=&pStrCd=%s&pLarGbn=&pMidGbn=&pClsFee=&pDayGbnAll=&pDayTime=&pStatus=&pKisuValue=C&pClsNm=&pClsNmTemp=&pTechNm=&pTechNmTemp=' % code
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for i1, article in enumerate(soup.find_all(match_soup_class(['article']))):
            if i1 == 0:  # side menu
                continue
            for i2, tr in enumerate(article.find_all('tr')):
                if i2 == 0:  # category
                    continue
                onclick = tr.find('input', {'name': 'chk'}).get('onclick')
                on_split = onclick.split("'")
                href = 'https://culture.lotteshopping.com/CLSS_view.do?taskID=L&pageNo=1&vpStrCd=%s&vpKisuNo=%s&vpClassCd=%s' % (on_split[1], on_split[3], on_split[5])

                for i3, td in enumerate(tr.find_all('td')):
                    info = td.text.strip().split()
                    if i3 == 2:
                        title = ' '.join(info)
                    elif i3 == 3:
                        author = ' '.join(info)
                    elif i3 == 4:
                        date = ' '.join(info)
                    elif i3 == 5:
                        price = ' '.join(info)
                # print(href, title, author, date, price)
                result = '%s<br><strong><a href="%s" target="_blank">%s(%s)</a></strong><br>%s<br>%s<br>' % (
                         result, href, title, author, date, price)
    return result


def main():
    now = datetime.now()
    cur_time = '%4d%02d%02d' % (now.year, now.month, now.day)

    token = get_naver_token()
    if token is None:
        print('get_naver_token failed')
        return

    title = '[%s] 많이 클릭된 연예 뉴스 모음(Naver, Daum, Nate)' % cur_time
    content = get_entertainment(cur_time)
    naver_post(token, title, content)

    title = '[%s] 롯데백화점 각 지점별 문화센터 일정' % cur_time
    content = lotte_curture_center()
    naver_post(token, title, content)

    title = '[%s] 현대백화점 각 지점별 문화센터 추천강좌 일정' % cur_time
    content = hyundai_curture_center()
    naver_post(token, title, content)

    title = '[%s] 자동차 뉴스 모음(한겨례, 노컷뉴스, Nate)' % cur_time
    content = get_car(cur_time)
    naver_post(token, title, content)
    return


if __name__ == '__main__':
    main()
