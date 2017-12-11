# -*- coding: utf-8 -*-
import json
import urllib.request
import re
import sys

from bs4 import BeautifulSoup
from requests import get, codes
from twython import TwythonError
from searcher.google_sheet import append_google_sheet


def search_webs(s):
    for key in s.keys:
        get_daum(s, key)
        # get_daum_agora(s, key)  # pretty shit...
        get_naver(s, key)
        get_today_humor(s, key)
        get_nate_pann(s, key)
        get_twitter_search(s, key)
        get_dcinside(s, key)
        get_ilbe(s, key)
        get_bobedream(s, key)
        get_insoya(s, key)
        get_clien(s, key)
        # get_ppomppu(s, key)  # don't know about encoding


def get_clien(s, key):
    date_regex = re.compile(r'^\d+:\d+')
    for i in range(1, 10):  # 10 page search
        url = 'http://www.clien.net/cs2/bbs/board.php?bo_table=kin&page=%d' % i
        r = get(url)
        if r.status_code != codes.ok:
            s.logger.error('[CLIEN] request error')
            return None

        soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
        url, user_id, post_date = None, None, None
        for ps in soup.find_all(s.match_soup_class(['mytr'])):
            for td in ps.find_all('td'):
                try:
                    td.a['href']
                    title = td.a.text
                    if title.find(key) > 0:
                        url = 'http://www.clien.net/cs2/%s' % td.a['href'][3:]
                        if url.startswith('http://www.clien.net/cs2/bbs/board.php?bo_table=kin&sca='):
                            url = None
                except TypeError:
                    pass

                if user_id is None:
                    spans = td.find_all('span', attrs={'class': 'member'})
                    for span in spans:
                        user_id = span.text
                else:
                    span = td.find('span')
                    matched = date_regex.match(span.text)
                    if matched:
                        post_date = s.today
                    else:
                        if span.text == '12-30':  # TODO : need to better way
                            post_date = '%s-%s' % (s.last_year, span.text)
                        elif span.text == '12-31':  # TODO : need to better way
                            post_date = '%s-%s' % (s.last_year, span.text)
                        else:
                            post_date = '%s-%s' % (s.this_year, span.text)

                    if url is not None:
                        append_google_sheet(s, user_id, url, title, post_date, '클리앙')
                    url, user_id, post_date = None, None, None


def get_insoya(s, key):
    for i in range(1, 5):  # 5 page search
        url = 'http://www.insoya.com/bbs/zboard.php?id=talkmaple&page=%d&divpage=15' % i

        r = get(url)
        if r.status_code != codes.ok:
            s.logger.error('[INSOYA] request error')
            return None

        soup = BeautifulSoup(r.text, 'html.parser')
        url, user_id, post_date, title = None, None, None, None
        for td in soup.find_all('td'):
            try:
                td.a['href']
                title = td.a.string
                if title is not None and title.find(key) > 0:
                    url = td.a['href']

                if (url is not None and
                        url.startswith('zboard.php?id=talkmaple')):
                    url = 'http://www.insoya.com/bbs/%s' % url
                    # print(url)
            except TypeError:
                spans = td.find_all('span', attrs={'class': 'memberSelect'})
                for span in spans:
                    if url is None:
                        break
                    user_id = span.string
                    # print(user_id)
                txt = str(td)
                if txt.startswith('<td class="eng w_date">'):
                    if url is not None:
                        w_date = str(td.text).split()
                        post_date = '20%s' % w_date[0].replace('.', '-')
                        # print(user_id, url, title, post_date)
                        append_google_sheet(s, user_id, url, title, post_date, '인소야닷컴')
                    url, user_id, post_date, title = None, None, None, None


def get_bobedream(s, key):
    for i in range(1, 10):  # 5 page search
        url = 'http://www.bobaedream.co.kr/list?code=freeb&s_cate=&maker_no=&model_no=&or_gu=10&or_se=desc&s_selday=&pagescale=30&info3=&noticeShow=&s_select=&s_key=&level_no=&vdate=&type=list&page=%d' % i

        r = get(url)
        if r.status_code != codes.ok:
            s.logger.error('[BOBEDREAM] request error')
            return None

        soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
        url, user_id, post_date, title = None, None, None, None
        for td in soup.find_all('td'):
            try:
                td.a['href']
                title = td.a.text
                if (title.find(key) > 0):
                    url = td.a['href']
            except TypeError:
                txt = str(td)
                if txt.startswith('<td class="date">'):
                    if (td.text.find(':') > 0):
                        post_date = s.today
                    else:
                        if s.today[5:] == '12-31':  # TODO : need to better way
                            post_date = '%s-%s' % (s.last_year, td.text.replace('/', '-'))
                        elif s.today[5:] == '12-30':  # TODO : need to better way
                            post_date = '%s-%s' % (s.last_year, td.text.replace('/', '-'))
                        else:
                            post_date = '%s-%s' % (s.this_year, td.text.replace('/', '-'))
                    # print(url, user_id, post_date, title)
                    if (url is not None and
                            not url.startswith('http://www.bobaedream.co.kr') and
                            not url.endswith('%2Flist%3Fcode%3Dfreeb')):  # ignore ad and popular
                        url = 'http://www.bobaedream.co.kr%s' % url
                        append_google_sheet(s, user_id, url, title, post_date, '보배드림')
                    url, user_id, post_date, title = None, None, None, None
                else:
                    spans = td.find_all('span', attrs={'class': 'author'})
                    for span in spans:
                        user_id = span.string


def get_ilbe(s, key):
    url = 'https://www.ilbe.com/?act=IS&where=document&is_keyword=%s' % key
    r = get(url)
    if r.status_code != codes.ok:
        s.logger.error('[ILGANBEST] request error')
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    for sre in soup.find_all(s.match_soup_class(['searchResult'])):
        for li in sre.find_all('li'):
            ilbe = li.address.text.split('|')
            # print('User ID: ', ilbe[0])
            # print('post_date: ', ilbe[1].split()[0])
            append_google_sheet(s, ilbe[0], li.a['href'], 'no title',
                                ilbe[1].split()[0], '일간베스트')


def get_dcinside(s, key):
    url = 'http://search.dcinside.com/post/q/%s' % key
    r = get(url)
    if r.status_code != codes.ok:
        s.logger.error('[DCINSIDE] request error')
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    for thumb in soup.find_all(s.match_soup_class(['thumb_list'])):
        for thumb_txt in thumb.find_all(s.match_soup_class(['thumb_txt'])):
            post_date = thumb_txt.span.string.split()
            append_google_sheet(s, '직접채워야함', thumb_txt.a['href'],
                                'no title', post_date[0].replace('.', '-'),
                                'DCINSIDE')


def get_nate_pann(s, key):
    url = 'http://pann.nate.com/search?searchType=A&q=%s' % key
    r = get(url)
    if r.status_code != codes.ok:
        s.logger.error('[Nate] request error')
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    for srch in soup.find_all(s.match_soup_class(['srch_list'])):
        rows = srch.findChildren(['dt', 'dl'])
        for row in rows:
            cells = row.findChildren('dt')
            for cell in cells:
                info = row.text.strip().split('\n')
                title = info[0]
                date = info[-1].replace('.', '-')
                user_id, post_date = get_nate_id_and_date(date, info[-2])
                if user_id is None or post_date is None:
                    continue
                append_google_sheet(s, user_id, row.a['href'], title, post_date,
                                    'NATE', '판')


def get_nate_id_and_date(date, user_info):
    if len(date) == len('17-03-23'):
        post_date = '20%s' % date
        return user_info, post_date
    else:
        u1 = re.search('(.*)이야기(.*) ', date)
        if u1 is not None:  # 10대 이야기I__D17-03-23 02:18
            u2 = re.search('(.*)-(.*)-(.*)', u1.group(2))  # I__D17-03-23
            user_id_year = (u2.group(1))  # I__D17
            user_id = user_id_year[:-2]   # I__D
            year = user_id_year[-2:]      # 17
            post_date = '20%s-%s-%s' % (year, u2.group(2), u2.group(3))
            return user_id, post_date
        else:  # 아이디17-03-23 00:10
            u2 = re.search('(.*)-(.*)-(.*) ', date)  # 아이디17-03-23
            user_id_year = (u2.group(1))  # 아이디17
            user_id = user_id_year[:-2]   # 아이디
            year = user_id_year[-2:]  # 17
            post_date = '20%s-%s-%s' % (year, u2.group(2), u2.group(3))
            return user_id, post_date
    return None, None


def get_today_humor(s, key):
    url = 'http://www.todayhumor.co.kr/board/list.php?kind=search&keyfield=subject&keyword=%s&Submit.x=0&Submit.y=0&Submit=검색' % key
    r = get(url)
    if r.status_code != codes.ok:
        s.logger.error('[TodayHumor] request error')
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    for l in soup.find_all(s.match_soup_class(['view'])):
        idx = 0
        temp_url = None
        for o in l.find_all('td'):
            idx += 1
            if idx == 1:
                continue
            # print('idx=', idx, '=>', o.text)
            try:
                o.a['href']
                if temp_url is None:
                    temp_url = o.a['href']
                    u = re.search('(.*)&keyfield(.*)', temp_url)
                    if u is None:
                        temp_url = None
                    else:
                        url = 'http://www.todayhumor.co.kr%s' % u.group(1)
            except TypeError:
                pass
            # print('idx=', idx, 'text=', o.text)
            if idx % 7 == 3:
                title = o.text
            if idx % 7 == 4:
                user_id = o.text
            if idx % 7 == 5:
                temp_date = o.text
                temp_date = temp_date.replace('/', '-')
                rm_hm = temp_date.split()  # rm hour, minute
                post_date = '20%s' % rm_hm[0]

                append_google_sheet(s, user_id, url, title, post_date, '오늘의 유머')
                user_id, url, title, post_date = None, None, None, None
                temp_url = None
    return None


def get_ppomppu(s, key):
    url = 'http://www.ppomppu.co.kr/search_bbs.php?keyword=%s' % key
    r = get(url)
    if r.status_code != codes.ok:
        s.logger.error('[Oh_U] request error')
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    # soup = BeautifulSoup(r.content.decode('utf-8r', 'replace'), 'html.parser')
    # soup = BeautifulSoup(r.content.decode('euc-kr', 'ignore'), 'html.parser')
    print(soup)


def get_naver(s, key, mode='blog'):
    url = 'https://openapi.naver.com/v1/search/%s?query=' % mode
    encText = urllib.parse.quote(key)
    options = '&display=20&sort=date'
    req_url = url + encText + options
    request = urllib.request.Request(req_url)
    request.add_header('X-Naver-Client-Id', s.naver_client_id)
    request.add_header('X-Naver-Client-Secret', s.naver_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if (rescode != 200):
        s.logger.error('[NAVER] Error Code: %d', rescode)
        return None
    response_body = response.read()
    data = response_body.decode('utf-8')
    js = json.loads(data)
    items = int(js["display"])
    for i in range(0, items):
        # http://blog.naver.com/ecampus_kgu?Redirect=Log&amp;logNo=220965327425
        try:
            get_naver_blog_page_num(js["items"][i]["link"])
            page_num = get_naver_blog_page_num(js["items"][i]["link"])
        except:
            continue
        # http://blog.naver.com/ecampus_kgu
        user_id = get_naver_blog_user_id(js["items"][i]["bloggerlink"])
        if user_id is None:
            continue
        naver_blog_link = '%s/%s' % (js["items"][i]["bloggerlink"], page_num)
        post_date = get_naver_blog_post_date(js["items"][i]["postdate"])
        # print(js["items"][i]["description"])
        title = js["items"][i]["title"]
        append_google_sheet(s, user_id, naver_blog_link, title, post_date,
                            'NAVER', '블로그')
    return


def get_naver_blog_page_num(naver_blog_inner_link):
    temp_link = naver_blog_inner_link.split('=')
    return temp_link[-1]


def get_naver_blog_user_id(naver_blog_link):
    u = re.search(r'^http://blog.naver.com/(.*)', naver_blog_link)
    if u is None:
        print(naver_blog_link)
        return None
    return u.group(1)


def get_naver_blog_post_date(post_date):  # 20170323 -> 2017-03-23
    return '-'.join([post_date[:4], post_date[4:6], post_date[6:]])


def get_daum(s, key, mode='date'):

    # https://apis.daum.net/search/blog?apikey={apikey}&q=다음&output=json
    url = 'https://apis.daum.net/search/blog?apikey=%s&q=' % (s.daum_app_key)
    encText = urllib.parse.quote(key)
    options = '&result=20&sort=%s&output=json' % mode
    req_url = url + encText + options
    request = urllib.request.Request(req_url)
    try:
        response = urllib.request.urlopen(request)
    except:
        s.logger.error('[DAUM]error: %s %s',
                       key, sys.exc_info()[0])
        return None
    rescode = response.getcode()
    if (rescode != 200):
        s.logger.error('[DAUM] Error Code: %d', rescode)
        return None

    # http://xxx.tistory.com
    p1 = re.compile(r'^http://\w+.tistory.com/\d+')
    # http://brunch.co.kr/@xxx/x
    p2 = re.compile(r'^https://brunch.co.kr/\@\w+/\d+')

    response_body = response.read()
    data = response_body.decode('utf-8')
    res = json.loads(data)
    for i in range(len(res['channel']['item'])):
        # title = res["channel"]['item'][i]['title']
        daum_blog_link = res["channel"]['item'][i]['link']
        # TODO : add duplicated check all functions at once.
        # if (s.check_duplicate_item(daum_blog_link, 'daum')):
        #     continue  # True duplicated
        m = p1.match(daum_blog_link)  # http://xxx.tistory.com
        if m:
            user_id = re.search(r'^http://(.*).tistory.com/\d+', daum_blog_link)
            title, post_date = parse_tistory_page(s, daum_blog_link)
            if title is None or post_date is None:
                continue
            append_google_sheet(s, user_id.group(1), daum_blog_link, title, post_date,
                                'DAUM', '블로그')
            continue

        m = p2.match(daum_blog_link)  # http://brunch.co.kr/@xxx/x
        if m:
            user_id = re.search('https://brunch.co.kr/\@(.*)/\d+', daum_blog_link)
            title, post_date = parse_brunch_page(daum_blog_link)
            if title is None or post_date is None:
                continue
            append_google_sheet(s, user_id.group(1), daum_blog_link, title, post_date,
                                'DAUM', '블로그')
            continue
        else:
            s.logger.info('[drop] %s', daum_blog_link)  # drop

    return


def parse_tistory_page(s, daum_blog_link):
    r = get(daum_blog_link)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = None
    for a in soup.find_all(s.match_soup_class(['article'])):
        rows = a.findChildren(['th', 'tr'])

    if rows is None:
        return None, None

    for row in rows:
        cells = row.findChildren('td')
        for cell in cells:
            message = row.text.strip()
            return get_title_and_user_id(s, message.strip('\n'), 'tistory')
    return None, None


def parse_brunch_page(daum_blog_link):
    r = get(daum_blog_link)
    soup = BeautifulSoup(r.text, 'html.parser')
    for a in soup.find_all('meta', property="ks:richscrap"):
        res = json.loads(a['content'])
        return (res['header']['title'], res['header']['date'].replace('.', '-'))


def get_title_and_user_id(s, message, blog_type=None):
    if blog_type == 'tistory':
        temp = message.split()
        p = re.compile(r'^\d+:\d+:\d+')
        m = p.match(temp[-1])
        if m is None:  # ok 'YYYY-MM-DD'
            return' '.join(temp[:-2]), temp[-1].replace('.', '-')
        else:
            return' '.join(temp[:-2]), s.today
    else:
        s.logger.error('invalid blog_type: %s', blog_type)
        return None, None


def get_daum_agora(s, key):

    url = 'http://agora.media.daum.net/nsearch/total?query=%s' % '사람'
    r = get(url)
    if r.status_code != codes.ok:
        s.logger.error('[DAUM AGORA] request error')
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    for sre in soup.find_all(s.match_soup_class(['sResult'])):
        rows = sre.findChildren(['dt', 'dl'])
        for row in rows:
            cells = row.findChildren('dt')
            for cell in cells:
                date = row.find(s.match_soup_class(['date']))
                temp_date = date.text.split(' ')
                post_date = temp_date[0].replace('.', '-')
                if post_date.startswith('2') is False:
                    continue
                for a_tag in row.find_all('a'):
                    user_id = a_tag.text  # last text is user_id, so overwrite.
                # print(row.a.text) # title
                # #print(row.a['href'])  # url
                # print(user_id.strip())
                append_google_sheet(s, user_id.strip(), row.a['href'], 'No title', post_date,
                                    'DAUM', '아고라')


def get_twitter_search(s, key):
    try:
        timeline = s.twitter.search(
            q=key, result_type='popular', count=20)

        dump_tl = json.dumps(timeline)  # dict -> json
        tl = json.loads(dump_tl)
        for i in tl['statuses']:
            for url in i['entities']['urls']:
                post_url = url['url']
                break  # need 1st url
            post_date = get_twitter_post_date(i['created_at'])
            append_google_sheet(s, i['text'], post_url, 'No title', post_date,
                                'TWITTER')
            # print('[USER_CREATED_AT]', i['user']['created_at'])

    except TwythonError as e:
        s.logger.error('TwythonError %s', e)


def get_twitter_post_date(date_str):
    split_date = date_str.split()
    post_date = '%s-%02d-%02d' % (split_date[5],
                                  month_converter(split_date[1]),
                                  int(split_date[2]))
    return post_date


def month_converter(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.index(month) + 1
