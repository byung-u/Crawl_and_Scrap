#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import urllib.request
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver


def main():
    driver = webdriver.Chrome('/Users/xxxxxxxx/lib/chromedriver')
    driver.implicitly_wait(3)
    driver.get('https://nid.naver.com/nidlogin.login')
    driver.find_element_by_name('id').send_keys('xxxxx')
    driver.find_element_by_name('pw').send_keys('xxxxxxxx')
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

    driver.get('https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=Bs48Suex7StHMRgDYx4m&redirect_uri=http://sfixer.tistory.com&state=xxxxxxxxxxxxxxcU')
    # driver.find_element_by_xpath('//*[@id="confirm_terms"]/a[2]').click()
    redirect_url = driver.current_url

    temp = re.split('code=', redirect_url)
    cs = re.split('&state=', temp[1])
    code = cs[0]
    state = cs[1]
    print(code, state)

    req_url = 'https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id=Bs48xxxxxStHxxxxxx4m&client_secret=e9xxxxxxxV&code=%s&state=%s' % (code, state)
    driver.get(req_url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    js = json.loads(soup.text)
    token = js['access_token']
    header = "Bearer " + token  # Bearer 다음에 공백 추가
    clubid = "xxxxx958"  # 카페의 고유 ID값
    menuid = "1"  # (상품게시판은 입력 불가)
    url = "https://openapi.naver.com/v1/cafe/" + clubid + "/menu/" + menuid + "/articles"
    subject = urllib.parse.quote('OK 된다.')
    content = urllib.parse.quote("[content] 네이버 cafe api test python")
    data = urlencode({'subject': subject, 'content': content}).encode()
    request = urllib.request.Request(url, data=data)
    request.add_header("Authorization", header)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)


if __name__ == '__main__':
    main()
