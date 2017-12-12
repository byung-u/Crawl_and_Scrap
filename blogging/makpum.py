#!/usr/bin/env python3
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime
from requests import get
from selenium import webdriver
from seleniumrequests import Chrome

ADSENSE_MIDDLE = '''<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- insert middle -->
<ins class="adsbygoogle"
     style="display:inline-block;width:728px;height:90px"
     data-ad-client="ca-pub-2477248594987452"
     data-ad-slot="3727980969"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>'''


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def tistory_post(token, title, content, category):
    webdriver = Chrome()
    response = webdriver.request('POST', 'https://www.tistory.com/apis/post/write', data={"access_token": token, "blogName": "makpum", 'title': title, 'content': content, 'category': category, 'visibility': '3'})
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


def main():
    now = datetime.now()
    cur_time = '%4d%02d%02d' % (now.year, now.month, now.day)

    # token = get_tistory_token()

    # title = '[%s] TEST' % cur_time
    # tistory_post(token, title, content, '252369')  # 국내

    # title = '[%s] TEST' % cur_time
    # tistory_post(token, title, content, '268755')  # 해외


if __name__ == '__main__':
    main()
