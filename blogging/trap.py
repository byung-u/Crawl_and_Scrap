#!/usr/bin/env python3
import os
import praw
import json
import re

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from googletrans import Translator
from random import choice
from requests import get
from selenium import webdriver
from seleniumrequests import Chrome

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko  ) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/  19.0.1084.46'
                'Safari/536.5'), )


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
    tpw = os.environ.get('TISTORY_PAW')
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
    for s in sessions:
        try:
            span = s.span.text
        except AttributeError:
            continue
        if lt_today != span.split()[1][0:2]:
            continue
        try:
            href = s.a['href']
        except TypeError:
            continue
        # print(href, s.a.text)
        r_article = get(href)
        soup_article = BeautifulSoup(r_article.text, 'html.parser')
        complete_href = ''
        for article in soup_article.find_all(match_soup_class(['article'])):
            for idx, ps in enumerate(article.find_all('p')):
                if idx == 0:
                    summary = ps.text
                elif idx == 1:
                    try:
                        complete_href = ps.a['href']
                    except TypeError:
                        pass
                    break
        ko_title = t.translate(s.a.text, dest='ko').text
        ko_article = t.translate(summary, dest='ko').text
        if len(complete_href) == 0:
            continue
        temp = '<a href="%s" target="_blank"><font color="blue">%s</font></a><br>%s<br><a href="%s" target="_blank"><font color="red">🔗 전체내용 Link</font></a><br><div style="border:1px solid grey"><br>%s<br><br>"%s"</div><br><br>' % (href, s.a.text, summary, complete_href, ko_title, ko_article)
        result = '%s<br>%s' % (result, temp)
    return result


def the_guardian(token, cur_time):
    now = datetime.now() - timedelta(days=1)
    yesterday = '%4d/%s/%02d' % (now.year, now.strftime("%b").lower(), now.day)

    t = Translator()
    url = 'https://www.theguardian.com/business/economics'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > div > ul > li > ul > li > div > div > a')
    for s in sessions:
        href = s['href']
        if href.find(yesterday) == -1:
            continue

        result, text = [], []
        total_len = 0
        request_txt = ''

        title = s.text
        ko_title = t.translate(title, dest='ko').text

        a_r = get(href)
        a_soup = BeautifulSoup(a_r.text, 'html.parser')
        for ca in a_soup.find_all(match_soup_class(['content__article-body'])):
            temp_text = ca.text
            break
        temp = temp_text.split('\n')
        article = [t for t in temp if len(t) > 150]

        for line in article:
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

        content = '<a href="%s" target="_blank"><font color="red">🔗 원본 Link(%s)</font></a><br><br><br>%s<br>' % (href, href, '<br>'.join(result))

        post_title = '[%s] %s(%s)' % (cur_time, ko_title, title)
        tistory_post(token, post_title, content, '766230')


def translate_text(t, article, src='en', dest='ko'):
    result, text = [], []
    total_len = 0
    request_txt = ''
    for line in article:
        total_len += len(line)
        text.append(line)
        if total_len > 4000:
            request_txt = '<br>'.join(text)
            ko_text = t.translate(request_txt, src=src, dest=dest).text
            result.append(ko_text)
            del text[:]
            total_len = 0

    request_txt = '<br>'.join(text)
    ko_text = t.translate(request_txt, dest='ko').text
    result.append(ko_text)
    return '<br>'.join(result)


def nikkei_japan():
    article = []
    t = Translator()
    is_not_done = True
    base_url = 'https://www.nikkei.com'
    url = 'https://www.nikkei.com/access/'

    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    idx = 1
    content = '<a href="%s" target="_blank"><font color="blue">[종합 1~10위]</font></a><br><br>' % url
    # print('종합')
    for item in soup.find_all(match_soup_class(['m-miM32_item'])):
        href = '%s%s' % (base_url, item.a['href'])
        ko_title = t.translate(item.a.text, src='ja', dest='ko').text
        # print([idx], href, ko_text, item.a.text)
        content = '%s<br><strong><a href="%s" target="_blank">%d. %s(%s)</font></a></strong><br>' % (content, href, idx, ko_title, item.a.text)
        idx += 1
        # print([idx], href, item.a.text)
        a_r = get(href)
        a_soup = BeautifulSoup(a_r.text, 'html.parser')
        article = []
        for article_text in a_soup.find_all(match_soup_class(['cmn-article_text'])):
            for ps in article_text.find_all('p'):
                article.append(ps.text)

        result = translate_text(t, article, 'ja', 'ko')
        del article[:]
        content = '%s<br>%s<br>' % (content, result)

        if idx == 11 and is_not_done:
            content = '%s<br><br><a href="%s" target="_blank"><font color="blue">[조간과 석간에서 1~10위]</font></a><br><br>' % (content, url)
            is_not_done = False
            idx = 1

    return content


def mainichi_daily_top20():
    t = Translator()
    url = 'https://mainichi.jp/ranking/daily/'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = '<a href="%s" target="_blank"><font color="blue">[마이니치신문 조회수 1~20위]</font></a><br><br>' % url
    for i in range(1, 21):  # 1 ~ 20
        class_name = 'rank-%d' % i
        for rank in soup.find_all(match_soup_class([class_name])):
            ko_title = ''
            midashi = rank.find('span', attrs={'class': 'midashi '})
            try:
                title = midashi.text
                ko_title = t.translate(title, src='ja', dest='ko').text
            except AttributeError:
                midashi = rank.find('span', attrs={'class': 'midashi icon_plus'})
                try:
                    title = midashi.text
                    ko_title = t.translate(title, src='ja', dest='ko').text
                except AttributeError:
                    continue
            published = rank.find('p', attrs={'class': 'date'})
            href = rank.a['href']
            # print([i], title)
            # print(published.text)
            # print(rank.a['href'], '\n\n')

            content = '%s<br><strong><a href="%s" target="_blank">%d. %s(%s)</font></a></strong><br>%s<br>' % (content, href, i, ko_title, title, published)
            a_r = get(rank.a['href'])
            a_soup = BeautifulSoup(a_r.text, 'html.parser')
            article = []
            for mt in a_soup.find_all(match_soup_class(['main-text'])):
                # print(mt)
                for txt in mt.find_all('p', attrs={'class': 'txt'}):
                    article.append(txt.text.strip())
            result = translate_text(t, article, 'ja', 'ko')
            del article[:]
            # do not add <br> tag
            if len(result) == 0:
                content = '%s기사내용 숨겨짐(번역불가)<br>' % content
            else:
                content = '%s%s<br><br>' % (content, result)
            break
    return content


def reddit_popular():
    t = Translator()
    result = ''
    client_id = os.environ.get('REDDIT_CLIENT_ID')
    client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
    reddit_id = os.environ.get('REDDIT_ID')
    reddit_pw = os.environ.get('REDDIT_PAW')
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret, password=reddit_pw,
                         user_agent='USERAGENT', username=reddit_id)

    for idx, sub in enumerate(reddit.subreddit('popular').hot(limit=30)):
        ko_title = ''
        try:
            ko_title = t.translate(sub.title, dest='ko').text
        except json.decoder.JSONDecodeError:
            pass
        # print(sub.url, idx + 1, sub.score, sub.title, ko_title)
        temp = '<a href="%s" target="_blank"><strong>[%d위] %s (score: ⬆ %s)</strong></a><pre>%s</pre><br>' % (
               sub.url, idx + 1, sub.title, sub.score, ko_title)
        result = '%s<br>%s' % (result, temp)
    return result


def wired_popular(token, cur_time):
    t = Translator()
    url = 'https://www.wired.com/'
    r = get(url, headers={'User-Agent': choice(USER_AGENTS)})
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > div > div > div > div > aside > div > div > div > ul > li > a')
    for s in sessions:
        article = []
        post_title = ''
        try:
            href = s['href']
            # print(href, s.h5.text)
            ko_title = t.translate(s.h5.text, dest='ko').text
            post_title = '[%s] %s(%s)' % (cur_time, ko_title, s.h5.text.strip())
        except TypeError:
            continue
        a_r = get(href, headers={'User-Agent': choice(USER_AGENTS)})
        a_soup = BeautifulSoup(a_r.text, 'html.parser')
        for body in a_soup.find_all(match_soup_class(['article-body-component'])):
            for body_p in body.find_all('p'):
                if str(body_p).find('p class=') != -1:
                    continue
                article.append(body_p.text)
        if len(article) == 0:
            continue
        result = '<a href="%s" target="_blank"><font color="red">🔗  원문: %s</font></a><br>' % (href, href)
        content = translate_text(t, article)
        result = '%s<br>%s' % (result, content)
        tistory_post(token, post_title, result, '766972')
    return


def main():
    now = datetime.now()
    cur_time = '%4d%02d%02d' % (now.year, now.month, now.day)

    token = get_tistory_token()

    title = '[%s] Reddit에서 인기있는 게시글 (1~30위)' % cur_time
    content = reddit_popular()
    tistory_post(token, title, content, '766775')

    content = nikkei_japan()
    title = '[%s] 니케이신문에서 인기있는 간추린 뉴스(1~10위)' % cur_time
    tistory_post(token, title, content, '766335')

    title = '[%s] 마이니치신문 하루에 가장 많이 조회된 뉴스(1~20위)' % cur_time
    content = mainichi_daily_top20()
    tistory_post(token, title, content, '766335')

    title = '[%s] Linux Today 새로운 소식' % cur_time
    content = linux_today()
    tistory_post(token, title, content, '766104')

    the_guardian(token, cur_time)

    if now.day % 7 == 0 or now.day % 7 == 3:
        wired_popular(token, cur_time)  # twice a week


if __name__ == '__main__':
    main()
