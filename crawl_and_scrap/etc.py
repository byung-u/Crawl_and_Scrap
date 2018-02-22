#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sqlite3

from bs4 import BeautifulSoup
from requests import get
from time import gmtime, strftime, time
from random import randrange
from selenium import webdriver

from crawl_and_scrap import defaults


class ETC:
    def __init__(self, bw):
        pass

    def is_exist_interesting_keyword(self, keyword):
        if (keyword.find('마포') >= 0 or
                keyword.find('자이') >= 0 or
                keyword.find('대출') >= 0 or
                keyword.find('부동산') >= 0 or
                keyword.find('규제') >= 0 or
                keyword.find('분양') >= 0):
            return True
        else:
            return False

    def get_wishket(self, bw):
        driver = webdriver.Chrome(bw.chromedriver_path)
        # driver = webdriver.PhantomJS()
        driver.implicitly_wait(3)

        url = 'https://www.wishket.com/project/'
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        short_url = ''
        for p in soup.find_all(bw.match_soup_class(['project-list-box'])):
            for i, div in enumerate(p.find_all('div')):
                if i % 10 == 0:
                    title = div.text
                    try:
                        link = 'https://www.wishket.com/%s' % div.a['href']
                    except KeyError:
                        pass
                    except TypeError:
                        pass
                if i % 10 == 2:
                    if bw.is_already_sent('ETC', link):
                        continue
                    short_url = bw.shortener_url(link)
                    if short_url is None:
                        short_url = ''
                    info = div.text.split(' ')
                    result = '%s\n%s\n%s\n%s\n\n#wishket' % (title, info[1], info[3], short_url)
                    bw.post_tweet(result, 'Wishket')
        driver.quit()

    def get_wadiz(self, bw):
        driver = webdriver.Chrome(bw.chromedriver_path)
        # driver = webdriver.PhantomJS()
        driver.implicitly_wait(3)
        url = 'https://www.wadiz.kr/web/winvest/main'
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        session = soup.select('li > a')
        for idx, s in enumerate(session):
            if s.h4 is None:
                continue
            days = s.find('span', attrs={'class': 'days'})
            if days.text == '성공':
                left_days = '청약 마감'
            else:
                left_days = days.text

            amount = s.find('span', attrs={'class': 'amount'})
            link = 'https://www.wadiz.kr%s' % s['href']
            if bw.is_already_sent('ETC', link):
                continue
            short_url = bw.shortener_url(link)
            if short_url is None:
                short_url = link
            result = '%s\n%s\n%s\n%s\n%s\n\n#wadiz' % (
                     s.h4.text, s.h5.text, amount.text, left_days,
                     short_url)
            bw.post_tweet(result, 'Wadiz')
        driver.quit()

    def get_onoffmix(self, bw):
        driver = webdriver.Chrome(bw.chromedriver_path)
        # driver = webdriver.PhantomJS()
        driver.implicitly_wait(3)

        # 'https://onoffmix.com/event?c=86' 강연
        # 'https://onoffmix.com/event?c=87' 세미나/컨퍼런스
        # 'https://onoffmix.com/event?c=91' 소모임/친목행사
        # 'https://onoffmix.com/event?c=96' 기타
        urls = ['https://www.onoffmix.com/event',
                'https://onoffmix.com/event?c=86',
                'https://onoffmix.com/event?c=87',
                'https://onoffmix.com/event?c=91',
                'https://onoffmix.com/event?c=96', ]
        for url in urls:
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            session = soup.select('div > div.sideLeft > div.contentBox.todayEventArea > ul > li > a')
            for s in session:
                if len(s.text) == 0:
                    # print(s['href'], s.text)
                    continue
                if bw.is_already_sent('ETC', s['href']):
                    continue
                short_url = bw.shortener_url(s['href'])
                if short_url is None:
                    short_url = s['href']

                result = '%s\n%s\n\n#onoffmix' % (s.text, short_url)
                bw.post_tweet(result, 'Onoffmix')
        driver.quit()

    def get_sacticket(self, bw):  # 예술의 전당
        driver = webdriver.Chrome(bw.chromedriver_path)
        # driver = webdriver.PhantomJS()
        driver.implicitly_wait(3)

        url = 'https://www.sacticket.co.kr/SacHome/ticket/reservation'
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for p in soup.find_all(bw.match_soup_class(['ticket_list_con'])):
            for content in p.find_all(bw.match_soup_class(['content'])):
                try:
                    c_info = content.a['onclick'].split("'")
                    page_id = c_info[1]
                    page_type = c_info[3]
                    if page_type == 'E':
                        result_msg = "[전시]"
                        result_url = 'https://www.sacticket.co.kr/SacHome/exhibit/detail?searchSeq=%s' % page_id
                    elif page_type == 'P':
                        result_msg = "[공연]"
                        result_url = 'https://www.sacticket.co.kr/SacHome/perform/detail?searchSeq=%s' % page_id
                    else:
                        continue
                    if bw.is_already_sent('ETC', result_url):
                        continue
                    short_url = bw.shortener_url(result_url)  # append last line of message
                    if short_url is None:
                        short_url = result_url

                    for idx, ca in enumerate(content.find_all('a')):
                        if idx == 0:
                            result_msg = '%s\n%s' % (result_msg, ca.text)
                        elif idx == 1:
                            if ca.text != '무료':
                                result_msg = '%s\n%s' % (result_msg, '유료')
                            else:
                                result_msg = '%s\n%s' % (result_msg, ca.text)
                    for idx, cp in enumerate(content.find_all('p')):
                        if idx > 1:
                            break
                        result_msg = '%s\n%s' % (result_msg, cp.text)
                    result_msg = '%s\n%s' % (result_msg, short_url)
                    bw.post_tweet(result_msg, 'sacticket')
                except KeyError:
                    continue
                except TypeError:
                    continue
        driver.quit()

    def get_coex_exhibition(self, bw):
        url = 'http://www.coex.co.kr/blog/event_exhibition?list_type=list'
        r = bw.request_and_get(url, 'ETC Coex')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        exhibition_url = 'http://www.coex.co.kr/blog/event_exhibition'
        for a in soup.find_all('a', href=True):
            if a['href'].startswith(exhibition_url) is False:
                continue
            exhibition_encode = a.text.encode('utf-8')
            if len(exhibition_encode) < 20:
                # TODO : 다음페이지 ignore -> ?
                continue

            if bw.is_already_sent('ETC', a['href']):
                continue
            short_url = bw.shortener_url(a['href'])
            if short_url is None:
                short_url = a['href']

            exhibition = a.text.splitlines()
            coex_result = '%s\n%s\n\n%s\n%s\n요금:%s' % (
                short_url,
                exhibition[3],
                exhibition[4],
                exhibition[6],
                exhibition[5].lstrip('\\'))
            bw.post_tweet(coex_result, 'Coex')

    """
    sort :
        activity – last_activity_date
        creation – creation_date
        votes – score
        relevance – matches the relevance tab on the site itself

    intitle : search keyword (ex. quick sort)
    """

    def search_stackoverflow(self, bw, sort='activity', lang='python'):
        STACK_EXCHANGE_API_URL = "https://api.stackexchange.com"
        r = get(STACK_EXCHANGE_API_URL + "/search", {
            "order": "desc",
            "sort": sort,
            "tagged": lang,
            "site": "stackoverflow",
            "intitle": lang,
        }).json()

        for i in range(len(r["items"])):
            if r["items"][i]["score"] <= 1:
                continue

            if bw.is_already_sent('ETC', r["items"][i]["link"]):
                continue
            short_url = bw.shortener_url(r["items"][i]["link"])
            if short_url is None:
                short_url = r["items"][i]["link"]

            result = '[▲ %s]\n%s\n%s\n#SO' % (
                r["items"][i]["score"],
                r["items"][i]["title"],
                short_url)
            bw.post_tweet(result, 'Stackoverflow')

    def search_nate_ranking_news(self, bw):
        url = 'http://news.nate.com/rank/interest?sc=its&p=day&date=%s' % (
            strftime("%Y%m%d", gmtime()))

        r = bw.request_and_get(url, 'ETC Nate ranking news')
        if r is None:
            return

        soup = BeautifulSoup(r.text, 'html.parser')
        result_msg = []  # send email
        # Rank 1~5
        for news_rank in soup.find_all(bw.match_soup_class(['mduSubjectList'])):
            result = '%s\n%s\n%s\n\n' % (
                news_rank.em.text,
                news_rank.strong.text,
                news_rank.a['href'])
            result_msg.append(result)

        # Rank 6~30
        i = 6
        for news_rank in soup.find_all(
                bw.match_soup_class(['mduSubject', 'mduRankSubject'])):
            for news in news_rank.find_all('a'):
                result = '%d위\n%s\n%s\n' % (
                    i,
                    news.text,
                    news['href'])
                i += 1
                result_msg.append(result)
        return result_msg

    def get_naver_popular_news(self, bw):
        url = 'http://news.naver.com/main/list.nhn?sid1=001&mid=sec&mode=LSD&date=%s' % bw.current_date
        r = bw.request_and_get(url, 'ETC Naver popular news')
        if r is None:
            return

        result_msg = []  # for send mail
        soup = BeautifulSoup(r.text, 'html.parser')
        for f in soup.find_all(bw.match_soup_class(['type02'])):
            for li in f.find_all('li'):

                if self.is_exist_interesting_keyword(li.a.text) is False:
                    continue
                if bw.is_already_sent('ETC', li.a['href']):
                    continue
                n_result = '%s\n%s' % (li.a.text, li.a['href'])
                result_msg.append(n_result)
        return result_msg

    def get_national_museum_exhibition(self, bw):  # NATIONAL MUSEUM OF KOREA
        MUSEUM_URL = 'https://www.museum.go.kr'

        url = 'https://www.museum.go.kr/site/korm/exhiSpecialTheme/list/current?listType=list'
        r = bw.request_and_get(url, 'ETC National Museum')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for f in soup.find_all(bw.match_soup_class(['list_sty01'])):
            for li in f.find_all('li'):
                p = li.p.text.split()
                period = ''.join(p[:3])
                title = li.a
                ex_url = '%s%s' % (MUSEUM_URL, title['href'])
                exhibition = None
                for img in li.find_all('img', alt=True):
                    exhibition = img['alt']
                if exhibition is None:
                    continue
                if bw.is_already_sent('ETC', ex_url):
                    continue
                nm_short_url = bw.shortener_url(ex_url)
                if nm_short_url is None:
                    nm_short_url = ex_url
                nm_result = '%s\n%s\n%s' % (nm_short_url, period, exhibition)
                bw.post_tweet(nm_result, 'National museum')

    def get_realestate_daum(self, bw):
        url = 'http://realestate.daum.net/news'
        r = bw.request_and_get(url, 'ETC Daum realestate')
        if r is None:
            return None
        rd_result_msg = []
        soup = BeautifulSoup(r.text, 'html.parser')
        for f in soup.find_all(bw.match_soup_class(['link_news'])):
            if self.is_exist_interesting_keyword(f.text) is False:
                continue
            if bw.is_already_sent('ETC', f['href']):
                continue
            rd_result = '%s\n%s' % (f.text, f['href'])
            rd_result_msg.append(rd_result)
        return rd_result_msg

    def get_realestate_mk(self, bw):  # maekyung (MBN)
        url = 'http://news.mk.co.kr/newsList.php?sc=30000020'
        r = bw.request_and_get(url, 'ETC MBN realestate')
        if r is None:
            return None
        rmk_result_msg = []

        soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
        for f in soup.find_all(bw.match_soup_class(['art_list'])):
            mk_title = f.a['title']

            if self.is_exist_interesting_keyword(mk_title) is False:
                continue
            if bw.is_already_sent('ETC', f.a['href']):
                continue
            rmk_result = '%s\n%s' % (f.a['title'], f.a['href'])
            rmk_result_msg.append(rmk_result)
        return rmk_result_msg

    def get_rate_of_process_sgx(self, bw):
        url = 'http://www.khug.or.kr/rateOfBuildingDistributionApt.do?API_KEY=%s&AREA_DCD=%s' % (
            bw.rate_of_process_key, bw.area_dcd)
        r = bw.request_and_get(url, 'ETC rate of proecess')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.find_all('item'):
            if item.addr.text.find(bw.keyword) >= 0:
                msg = '%s(%s)\n%s\n%d' % (
                    item.addr.text, item.tpow_rt.text, item.bsu_nm.text,
                    int(time()))
                bw.post_tweet(msg, 'rate of process')

    def get_hacker_news(self, bw):
        # p=1, rank 16~30, p=2, rank 31~45
        url = 'https://news.ycombinator.com/news?p=0'  # rank 1~15
        r = bw.request_and_get(url, 'ETC Hacker news')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        cnt = 0
        for f in soup.find_all(bw.match_soup_class(['athing'])):
            cnt += 1
            if cnt > 5:  # 5 articles
                break
            hn_text = f.text.strip()
            for s in f.find_all(bw.match_soup_class(['storylink'])):
                hn_url = s['href']
                if bw.is_already_sent('ETC', hn_url):
                    continue
                hn_short_url = bw.shortener_url(hn_url)
                if hn_short_url is None:
                    hn_short_url = hn_url
                result = '%s\nRank:%s\n#hacker_news' % (hn_short_url, hn_text)
                bw.post_tweet(result, 'Hacker news')
                break

    def get_recruit_people_info(self, bw):  # 각종 모집 공고
        root_url = 'http://goodmonitoring.com'
        url = 'http://goodmonitoring.com/xe/moi'
        r = bw.request_and_get(url, 'ETC monitoring')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for f in soup.find_all(bw.match_soup_class(['title'])):
            mozip = f.text.strip()
            if mozip == '제목' or mozip.find('대학생') != -1:
                continue
            else:
                mozip_url = '%s%s' % (root_url, f.a['href'])
                if bw.is_already_sent('ETC', mozip_url):
                    continue
                short_url = bw.shortener_url(mozip_url)
                if short_url is None:
                    short_url = mozip_url
                mz_result = '%s\n%s' % (mozip, short_url)
                bw.post_tweet(mz_result, 'monitoring')

    def _get_rfc_random_info(self, soup, rfc_num):
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
                        return '[RFC %d]\n%s\n%s' % (num, title.strip(), href)
        return False

    def get_rfc_random_title(self, bw):  # get rfc info random
        url = 'https://www.rfc-editor.org/search/rfc_search_detail.php?page=All&pubstatus[]=Any&pub_date_type=any&sortkey=Number&sorting=ASC'
        max_rfc_num = 8179  # 2017/12/01 total results
        rn = randrange(1, max_rfc_num)

        r = get(url)
        r = bw.request_and_get(url, 'ETC RFC')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        result = False
        max_try = 1000
        while result is False and max_try != 0:
            result = self._get_rfc_random_info(soup, rn)
            rn = randrange(1, max_rfc_num)
            max_try -= 1
        bw.post_tweet(result, 'RFC info')

    def get_rfc_draft_list(self, bw):  # get state 'AUTH48-DONE' only
        url = 'https://www.rfc-editor.org/current_queue.php'
        r = bw.request_and_get(url, 'ETC RFC draft')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for n in soup.find_all(bw.match_soup_class(['narrowcolumn'])):
            for tr in n.find_all('tr'):
                try:
                    tr.a['href']
                except TypeError:
                    continue
                cnt = 0
                for td in tr.find_all('td'):
                    if cnt == 0:  # state
                        # AUTH48-DONE = Final approvals are complete
                        if td.text.find('AUTH48-DONE') == -1:
                            break
                        else:
                            state = td.text
                    elif cnt == 3:  # draft name and author, weeks in state/queue
                        title = td.text.split()
                        version = title[0].split('-')
                        for b in tr.find_all('b'):
                            if bw.is_already_sent('ETC', b.a['href']):
                                continue
                            short_url = bw.shortener_url(b.a['href'])
                            rfc_draft = '[%s]\n%s(Ver:%s)\n%s\n#rfc_draft' % (
                                state.strip(),
                                '-'.join(version[1:-1]), version[-1],
                                short_url)

                            if len(rfc_draft) > defaults.MAX_TWEET_MSG:
                                rfc_draft = '[%s]\nVer:%s\n%s\n#rfc_draft' % (
                                    state.strip(), version[-1], short_url)
                            bw.post_tweet(rfc_draft, 'RFC draft')
                    cnt += 1

    def get_raspberripy_news(self, bw):
        url = 'http://lifehacker.com/tag/raspberry-pi'
        r = bw.request_and_get(url, 'ETC Raspberri py news')
        if r is None:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        for l in soup.find_all(bw.match_soup_class(['postlist__item'])):
            if len(l.a.text) == 0:
                continue
            rb_title = l.a.text
            if bw.is_already_sent('ETC', l.a['href']):
                continue
            short_url = bw.shortener_url(l.a['href'])
            if short_url is None:
                short_url = l.a['href']

            rb_news = '%s\n%s\n#lifehacker' % (rb_title, short_url)
            bw.post_tweet(rb_news, 'Raspberri py news')

    def national_treasure_post(self, bw, content, url):
        short_url = bw.shortener_url(url)
        if short_url is None:
            short_url = url

        nt = '%s\n%s' % (content, short_url)
        bw.post_tweet(nt, 'National Treasures')

    def national_treasure_select_k(self, bw, c):
        r = randrange(1, 421)   # 국보
        sr = "SELECT * FROM national_treasure WHERE t_type='국보' AND t_idx='%d'" % r
        c.execute(sr)
        res = c.fetchone()
        if res is None:
            c.execute("SELECT * FROM national_treasure WHERE t_type='국보' AND t_idx LIKE ?", ('%' + r + '%', ))
            res = c.fetchall()
            for r in res:
                self.national_treasure_post(bw, r[1], r[3])
        else:
            self.national_treasure_post(bw, res[1], res[3])

    def national_treasure_select_b(self, bw, c):
        r = randrange(1, 2387)  # 보물
        sr = "SELECT * FROM national_treasure WHERE t_type='보물' AND t_idx='%d'" % r
        c.execute(sr)
        res = c.fetchone()
        if res is None:
            c.execute("SELECT * FROM national_treasure WHERE t_type='보물' AND t_idx LIKE ?", ('%' + r + '%', ))
            res = c.fetchall()
            for r in res:
                self.national_treasure_post(bw, r[1], r[3])
        else:
            self.national_treasure_post(bw, res[1], res[3])

    def national_treasure_select_c(self, bw, c):
        r = randrange(1, 571)   # 천연기념물
        sr = "SELECT * FROM national_treasure WHERE t_type='보물' AND t_idx='%d'" % r
        c.execute(sr)
        res = c.fetchone()
        if res is None:
            c.execute("SELECT * FROM national_treasure WHERE t_type='보물' AND t_idx LIKE ?", ('%' + r + '%',))
            res = c.fetchall()
            for r in res:
                self.national_treasure_post(bw, r[1], r[3])
        else:
            self.national_treasure_post(bw, res[1], res[3])

    def national_treasure_select(self, bw):
        if not (os.path.isfile('$HOME/national_treasure.db')):
            bw.logger.error('No database')
            return

        conn = sqlite3.connect('national_treasure.db')
        c = conn.cursor()

        self.national_treasure_select_k(bw, c)
        self.national_treasure_select_b(bw, c)
        self.national_treasure_select_c(bw, c)
        conn.close()
