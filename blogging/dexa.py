#!/usr/bin/env python3
import json
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
    response = webdriver.request('POST', 'https://www.tistory.com/apis/post/write', data={"access_token": token, "blogName": "dexa", 'title': title, 'content': content, 'category': category, 'visibility': '3'})
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
    driver.quit()
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


# def market():
#     big_market()
#     costco()
#     emart_traders()
#


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
    result = '%s<br>%s<br>' % (result, ADSENSE_MIDDLE)

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
    result = '%s<br>%s<br>' % (result, ADSENSE_MIDDLE)
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

# https://sacademy.shinsegae.com/sdotcom/web/HP0010P0/HP0010P0.do#none


def mise_dust():
    # https://www.data.go.kr/subMain.jsp#/L3B1YnIvcG90L215cC9Jcm9zTXlQYWdlL29wZW5EZXZEZXRhaWxQYWdlJEBeMDgyTTAwMDAxMzBeTTAwMDAxMzUkQF5wdWJsaWNEYXRhRGV0YWlsUGs9dWRkaTo3MDkxMTBlNy1kN2IxLTQ0MjEtOTBiYS04NGE2OWY5ODBjYWJfMjAxNjA4MDgxMTE0JEBecHJjdXNlUmVxc3RTZXFObz0zMTg2Mzc0JEBecmVxc3RTdGVwQ29kZT1TVENEMDE=
    pass


def vic_market():
    result = '<br>'
    base_url = 'http://company.lottemart.com'
    url = 'http://company.lottemart.com/vc/info/branch.do?SITELOC=DK013'
    # r = get(url, headers={'User-Agent': choice(USER_AGENTS)})
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for i1, vic in enumerate(soup.find_all(match_soup_class(['vicmarket_normal_box']))):
        if i1 != 1:
            continue
        for i2, li in enumerate(vic.find_all('li')):
            if i2 % 5 != 0:
                continue
            for img in li.find_all('img'):
                thumbnail = '%s%s' % (base_url, img['src'])
                break
            button = str(li.button).split("'")
            href = '%s%s' % (base_url, button[1])
            result = '%s<strong><a href="%s" target="_blank">%s<font color="red"></font></a></strong><br>' % (
                     result, href, li.h3.text)
            # print(li.h3.text, thumbnail, href)
            for ul in li.find_all('ul'):
                for li2 in ul.find_all('li'):
                    temp = li2.text.strip().replace('\t', '').replace('\r', '')
                    temp_info = temp.split('\n')
                    infos = [t for t in temp_info if len(t) != 0]
                    result = '%s<br>%s: %s' % (result, infos[0], ' '.join(infos[1:]))
                    # print(infos)
            result = '%s<br><center><a href="%s" target="_blank"> <img border="0" src="%s" width="150" height="150"></a></center><br><br>' % (result, href, thumbnail)
    return result


def join_deny(num):
    if num == '1':
        return '가입 제한없음'
    elif num == '2':
        return '서민전용 가입'
    elif num == '3':
        return '가입 일부제한'
    else:
        return 'Unknown'


def dcls_end_day(day):  # 공시종료일
    if day is None:
        return '공시 종료일 미정'
    else:
        return '공시 종료일 ' + day


def max_limit(money):  # 공시종료일
    if money is None:
        return '한도정보 없음'
    else:
        m = str(money)
        ret = m.endswith('00000000')
        if ret is True:
            return m[0:-8] + '억원'

        ret = m.endswith('0000000')
        if ret is True:
            return m[0:-7] + '천만원'
        else:
            return m + '원'

def fixed_deposit():

    bank_code = {
            '우리은행': '0010001',
            '한국스탠다드차타드은행': '0010002',
            '한국씨티은행': '0010006',
            '대구은행': '0010016',
            '부산은행': '0010017',
            '광주은행': '0010019',
            '제주은행': '0010020',
            '전북은행': '0010022',
            '경남은행': '0010024',
            '중소기업은행': '0010026',
            '한국산업은행': '0010030',
            '국민은행': '0010927',
            '신한은행': '0011625',
            '농협은행': '0013175',
            'KEBKEB하나은행': '0013909',
            '케이뱅크은행': '0014674',
            '수협은행': '0014807',
            '한국카카오은행': '0015130',
            }
    result = '금융감독원의 금융상품통합 비교공시 정보를 바탕으로 작성된 글입니다.<br><br><br>'
    auth_key = os.environ.get('FINLIFE_KEY')

    for bank, code in bank_code.items():
        url = 'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth=%s&topFinGrpNo=020000&pageNo=1&financeCd=%s' % (auth_key, code)
        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        js = json.loads(str(soup))
        result = '%s<h3>%s</h3><br><table border="1" cellspacing="0" cellpadding="3" bordercolor="#  999999" style="border-collapse:collapse">' % (result, bank)
        result = '''%s<tr>
        <th>금융상품,가입방법</th>
        <th>우대조건</th>
        <th>가입대상</th>
        <th>최고한도</th>
        </tr>''' % (result)
        for banks in js['result']['baseList']:
            # print(banks['fin_prdt_nm'])
            result = '%s<tr>' % result
            result = '%s<td><font color="red">%s</font><br><br>➡ %s으로 가입<br>➡ %s<br>➡ %s</td>' % (result, banks["fin_prdt_nm"], banks['join_way'], join_deny(banks['join_deny']), dcls_end_day(banks['dcls_end_day']))
            # result = '%s<td>%s</td>' % (result, banks["join_way"])
            result = '%s<td>%s</td>' % (result, banks["spcl_cnd"].replace('\n', '<br>'))
            # result = '%s<td>%s</td>' % (result, banks['join_member'])
            result = '%s<td>%s</td>' % (result, banks['etc_note'].replace('\n', '<br>'))
            result = '%s<td>%s</td>' % (result, max_limit(banks['max_limit']))
            result = '%s</tr>' % result
        result = '%s</table><br><br><br>' % result
    return result


def main():
    now = datetime.now()
    cur_time = '%4d%02d%02d' % (now.year, now.month, now.day)

    token = get_tistory_token()

    title = '[%s] 정기예금 금리 정보' % cur_time
    content = fixed_deposit()
    tistory_post(token, title, content, '731649')

    return

    title = '[%s] 빅마켓 지점별 휴관일, 영업시간, 주소, 연락처 정보' % cur_time
    content = vic_market()
    tistory_post(token, title, content, '730606')

    title = '[%s] 롯데백화점 각 지점별 문화센터 일정' % cur_time
    content = lotte_curture_center()
    tistory_post(token, title, content, '730606')

    title = '[%s] 현대백화점 각 지점별 문화센터 추천강좌 일정' % cur_time
    content = hyundai_curture_center()
    tistory_post(token, title, content, '730606')
    # content = market()
    # content = mise_dust()


if __name__ == '__main__':
    main()
