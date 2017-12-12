#!/usr/bin/env python3
import os
import json
import re
import sys

from bs4 import BeautifulSoup
from googletrans import Translator
from selenium import webdriver
from seleniumrequests import Chrome
import urllib.request


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


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


def tistory_post(token, title, content, category, blog_name='trab'):
    webdriver = Chrome()
    response = webdriver.request('POST', 'https://www.tistory.com/apis/post/write', data={"access_token": token, "blogName": blog_name, 'title': title, 'content': content, 'category': category, 'visibility': '3'})
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


def statement_on_crypto():
    t = Translator()
    article = []
    with open('statement_on_crypto') as f:
        for line in f:
            article.append(line)
    f.closed
    return translate_text(t, article, 'en', 'ko')


def korea_childcare_center():
    result = ''
    f = open('childcare_center.text', 'r')
    soup = BeautifulSoup(f, 'html.parser')
    # for i1, table in enumerate(soup.find_all('table')):
    for table in soup.find_all('table'):
        for i1, tr in enumerate(table.find_all('tr')):
            for i2, td in enumerate(tr.find_all('td')):
                # print([i1, i2], td)
                if i1 == 0 and i2 == 0:
                    if td.text.strip() == '사이트명':
                        return result
                    result = '%s<br><br><br><strong><font color="red">%s</font></strong><br>' % (
                             result, td.text.strip())
                elif i2 % 2 == 0:
                    try:
                        href = td.a['href']
                        result = '%s<br><strong>%s</strong><a href="%s" target="_blank">(%s)</a>' % (result, td.text.strip(), href, href)
                        # print(href, td.text.strip())
                    except TypeError:
                        break
                else:
                    result = '%s, %s' % (result, td.text.strip())
                    # print(td.text.strip())
    result = '%s<br><br><br>' % result
    return result


def korea_childcare_center_etc():
    result = '<strong><font color="red">보육, 특수교육관련 기관, 단체, 학회 웹사이트</font></strong><br><br>'
    f = open('childcare_center_etc.text', 'r')
    soup = BeautifulSoup(f, 'html.parser')
    for table in soup.find_all('table'):
        for i1, tr in enumerate(table.find_all('tr')):
            for i2, td in enumerate(tr.find_all('td')):
                if (i1 == 0 and i2 == 0) or (i1 == 0 and i2 == 1):
                    continue
                elif i2 % 2 == 0:
                    # print([i1, i2], td)
                    try:
                        href = td.a['href']
                        result = '%s<br><strong>%s</strong><a href="%s" target="_blank">(%s)</a>' % (result, td.text.strip(), href, href)
                        # print(href, td.text.strip())
                    except TypeError:
                        break
    result = '%s<br><br><br>' % result
    return result


if __name__ == '__main__':
    # title = '[20171022] 스타트업의 시대가 끝난 이후(After the end of the startup era)'
    # content = startup_era_end()

    # title = '[20171211] 암호화폐, 초기 코인 공개에 대한 성명(Statement on Cryptocurrencies and Initial Coin Offerings)'
    # result = '<a href="https://www.sec.gov/news/public-statement/statement-clayton-2017-12-11" target="_blank">원본: https://www.sec.gov/news/public-statement/statement-clayton-2017-12-11</a> [참고용어] Initial Public Offering은 기업공개<br><br>'
    # content = statement_on_crypto()
    # result = '%s<br>%s' % (result, content)
    # tistory_post(token, title, result, '766214')  # trab 기타 지난 과거 글

    # title = '[20171212] 전국 육아종합지원센터 웹사이트, 연락처 정보'
    # content = korea_childcare_center()
    # tistory_post(token, title, content, '252369', 'makpum')

    # token = get_tistory_token()
    # title = '[20171212] 기타 보육관련 웹사이트, 연락처 정보'
    # content = korea_childcare_center_etc()
    # tistory_post(token, title, content, '252369', 'makpum')

    token = get_naver_token()
    if token is None:
        print('get_naver_token failed')
        sys.exit(1)

    title = '[20171212] 전국 육아종합지원센터 웹사이트, 연락처 정보'
    content = korea_childcare_center()
    naver_post(token, title, content)

    title = '[20171212] 기타 보육관련 웹사이트, 연락처 정보'
    content = korea_childcare_center_etc()
    naver_post(token, title, content)
