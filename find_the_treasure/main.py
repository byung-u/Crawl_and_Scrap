"""find_the_treasure web scrawling command line tool."""
# -*- coding: utf-8 -*-
import cgitb
import json
import logging
import os
import time
from datetime import datetime
from envparse import env
from requests import codes, get, post
from twython import Twython, TwythonError

# gmail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# custom
from find_the_treasure.ft_github import UseGithub
from find_the_treasure.ft_korea import (UseDataKorea)
from find_the_treasure.ft_daum import UseDaum
from find_the_treasure.ft_naver import UseNaver
from find_the_treasure.ft_sqlite3 import UseSqlite3
from find_the_treasure.ft_tech_blog import TechBlog
from find_the_treasure import defaults

from find_the_treasure.ft_etc import (get_coex_exhibition,
                                      search_stackoverflow,
                                      search_nate_ranking_news,
                                      get_naver_popular_news,
                                      get_national_museum_exhibition,
                                      get_onoffmix,
                                      get_realestate_daum,
                                      get_realestate_mk,
                                      get_rate_of_process_sgx,
                                      get_hacker_news,
                                      get_recruit_people_info,
                                      get_rfc_draft_list,
                                      get_raspberripy_news,
                                      )

cgitb.enable(format='text')


class FTbot:  # Find the Treasure
    def __init__(self):
        self.twit_post_limit = 180  # every 15min, https://dev.twitter.com/rest/public/rate-limiting
        self.twit_post = 0
        self.twitter_app_key = os.environ.get('TWITTER_APP_KEY')
        self.twitter_app_secret = os.environ.get('TWITTER_APP_SECRET')
        self.twitter_access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
        self.twitter_access_secret = os.environ.get('TWITTER_ACCESS_SECRET')
        self.twitter_id = os.environ.get('TWITTER_ID')
        self.twitter = Twython(
            self.twitter_app_key,
            self.twitter_app_secret,
            self.twitter_access_token,
            self.twitter_access_secret
        )

        self.github_id = os.environ.get('GITHUB_ID')
        self.github_p = os.environ.get('GITHUB_PW')
        self.github_client_id = os.environ.get('GITHUB_CLIENT_ID')
        self.github_client_secret = os.environ.get('GITHUB_CLIENT_SECRET')

        self.naver_client_id = os.environ.get('NAVER_CLIENT_ID')
        self.naver_secret = os.environ.get('NAVER_CLIENT_SECRET')

        self.daum_client_id = os.environ.get('DAUM_CLIENT_ID')
        self.daum_secret = os.environ.get('DAUM_CLIENT_SECRET')
        self.daum_app_key = os.environ.get('DAUM_APP_KEY')

        self.chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
        self.google_id = os.environ.get('GOOGOLE_ID')
        self.google_p = os.environ.get('GOOGOLE_PW')
        self.gmail_from_addr = os.environ.get('GOOGOLE_FROM_ADDR')
        self.gmail_to_addr = os.environ.get('GOOGOLE_TO_ADDR')
        self.google_url_api_key = os.environ.get('GOOGOLE_URL_API_KEY')

        self.apt_rent_url = os.environ.get('DATA_APT_RENT_URL')
        self.apt_trade_url = os.environ.get('DATA_APT_TRADE_URL')
        self.apt_trade_svc_key = os.environ.get('DATA_APT_API_KEY')
        self.apt_trade_dong = env('REALESTATE_DONG', cast=list)
        self.apt_trade_district_code = os.environ.get('REALESTATE_DISTRICT_CODE')
        # self.apt_trade_apt = os.environ.get('DATA_GO_KR', 'apt', raw=True)
        # self.apt_trade_size = os.environ.get('DATA_GO_KR', 'size', raw=True)

        self.rate_of_process_key = os.environ.get('RATE_OF_PROCESS_KEY')
        self.area_dcd = os.environ.get('ROP_AREA_DCD')
        self.keyword = os.environ.get('ROP_KEYWORD')

        now = datetime.now()
        log_file = '%s/log/ft_%4d%02d%02d.log' % (
            os.getenv("HOME"), now.year, now.month, now.day)
        # Write file - DEBUG, INFO, WARN, ERROR, CRITICAL
        # Console display - ERROR, CRITICAL
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter('[%(levelname)8s] %(message)s')
        ch.setFormatter(formatter)
        logging.basicConfig(filename=log_file,
                            format='[%(asctime)s] (%(levelname)8s) %(message)s',
                            datefmt='%I:%M:%S',
                            level=logging.INFO)
        self.logger = logging.getLogger('ft_logger')
        self.logger.addHandler(ch)

    def post_tweet(self, post_msg, subject='None'):
        if post_msg is not None:
            try:
                self.twit_post += 1
                if self.twit_post >= self.twit_post_limit:
                    self.logger.error([self.twit_post], 'post failed, try after 15 minute')
                    time.sleep(960)  # 15 * 60 sec + 60

                self.twitter.update_status(status=post_msg)
                self.logger.info('Tweet: %s [%d/180]', post_msg, self.twit_post)
            except TwythonError as e:
                self.logger.error('TwythonError: %s [%s]', e, post_msg)
        else:
            self.logger.info('[%s] no posting message', subject)
            return

    def match_soup_class(self, target, mode='class'):
        def do_match(tag):
            classes = tag.get(mode, [])
            return all(c in classes for c in target)
        return do_match

    def check_max_tweet_msg(self, msg):
        msg_encode = msg.encode('utf-8')
        msg_len = len(msg_encode)
        if msg_len > defaults.MAX_TWEET_MSG:
            over_len = msg_len - defaults.MAX_TWEET_MSG + 3 + 2  # ... + margin
            msg_encode = msg_encode[0:(msg_len - over_len)]
            msg = '%s' % msg_encode.decode("utf-8", "ignore")
            self.logger.info('[Over 140 omitting]%s', msg)
        return msg

    def shortener_url(self, url):
        post_url = 'https://www.googleapis.com/urlshortener/v1/url'
        payload = {'longUrl': url}
        headers = {'content-type': 'application/json'}
        params = {'key': self.google_url_api_key}
        r = post(post_url, data=json.dumps(payload), headers=headers, params=params)
        js = json.loads(r.text)
        return js['id']

    def post_tweet_list(self, msg, subject=None):
        if type(msg) is not list:
            self.logger.error('post_tweet_list failed, [%s] %s', subject, msg)
            return
        if len(msg) <= 0:
            self.logger.error('post_tweet_list failed, [%s] no message', subject)
            return

        for i in range(len(msg)):
            self.post_tweet(msg[i], subject)

    def send_gmail(self, subject, body):

        if type(body) is list:
            send_msg = '\n'.join(body)
        else:
            send_msg = body

        gmail_user = self.google_id
        gmail_pwd = self.google_p
        FROM = self.gmail_from_addr
        TO = self.gmail_to_addr

        msg = MIMEMultipart('alternative')
        msg['From'] = gmail_user
        msg['To'] = 'iam.byungwoo@gmail.com'
        msg['Subject'] = subject
        msg.attach(MIMEText(send_msg, 'plain', 'utf-8'))  # encoding

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, msg.as_string())
            server.quit()
            self.logger.info('[%s] successfully sent the mail' % subject)
        except BaseException as e:
            self.logger.error('failed to send mail: %s', str(e))

    def post_with_raw_timeline(self, timeline):
        dump_tl = json.dumps(timeline)  # dict -> json
        tl = json.loads(dump_tl)
        for i in tl['statuses']:
            result = 'Via @%s, %s' % (i['user']['screen_name'], i['text'])
            if len(result.encode('utf-8')) > defaults.MAX_TWEET_MSG:
                    continue
            self.post_tweet(result, 'raw_timeline')

    def request_and_get(self, url, name):
        try:
            r = get(url)
            if r.status_code != codes.ok:
                self.logger.error('[%s] request error, code=%d', name, r.status_code)
                return None
            return r
        except:
            self.logger.error('[%s] connect fail', name)
            return None


def db_table_check():
    sqlite3 = UseSqlite3()
    sqlite3.delete_expired_tuple()
    sqlite3.close()


def find_tech_blogs(ft):
    t = TechBlog(ft)

    t.boxnwhisker(ft)
    t.daliworks(ft)
    t.devpools(ft)
    t.dramancompany(ft)
    t.goodoc(ft)
    t.kakao(ft)
    t.lezhin(ft)
    t.linchpinsoft(ft)
    t.naver(ft)
    t.naver_nuli(ft)
    t.netmanias(ft)
    t.ridi(ft)
    t.skplanet(ft)
    t.spoqa(ft)
    t.tosslab(ft)
    t.tyle(ft)
    t.whatap(ft)
    t.woowabros(ft)


def deprecated(ft, run_type):
    if run_type is False:
        return

    # Popular twitter keyword search
    try:
        timeline_pop = ft.twitter.search(
            q='python', result_type='popular', count=1)
        ft.post_with_raw_timeline(timeline_pop)
    except TwythonError as e:
        ft.logger.error('TwythonError %s', e)

    naver_popular_news = get_naver_popular_news(ft)
    if (type(naver_popular_news) is list) and (len(naver_popular_news) > 0):
        ft.send_gmail('Naver popular news', naver_popular_news)

    rd = get_realestate_daum(ft)
    if (type(rd) is list) and (len(rd) > 0):
        ft.send_gmail('Daum realestate', rd)

    n = UseNaver(ft)
    naver_news = n.search_today_information_and_technology(ft)
    if (type(naver_news) is list) and (len(naver_news) > 0):
        ft.send_gmail('NAVER IT news', naver_news)

    dg = UseDataKorea(ft)
    dg.realstate_trade(ft)
    dg.realstate_rent(ft)


def finding_and_mail(ft):
    rmk = get_realestate_mk(ft)
    if (type(rmk) is list) and (len(rmk) > 0):
        ft.send_gmail('MBN realestate', rmk)

    daum = UseDaum(ft)
    daum_blog = daum.request_search_data(ft, req_str="마포")
    if (type(daum_blog) is list) and (len(daum_blog) > 0):
        ft.send_gmail('Daum Blogs', daum_blog)

    nate_rank_news = search_nate_ranking_news(ft)
    if (type(nate_rank_news) is list) and (len(nate_rank_news) > 0):
        ft.send_gmail('NATE IT news rank', nate_rank_news)


def finding_and_tweet(ft):
    # Tech
    find_tech_blogs(ft)

    g = UseGithub(ft)
    g.get_github_great_repo(ft, 'hot', 'python', 10)
    g.get_github_great_repo(ft, 'new', 'python', 0)
    g.get_github_great_repo(ft, 'new', None, 3)  # all languages

    search_stackoverflow(ft, "activity", "python")
    search_stackoverflow(ft, "activity", "racket")

    get_hacker_news(ft)
    get_rfc_draft_list(ft)
    get_raspberripy_news(ft)

    # Exhibition
    get_onoffmix(ft)
    get_coex_exhibition(ft)
    get_national_museum_exhibition(ft)

    # ETC
    dg = UseDataKorea(ft)
    dg.get_molit_news(ft)   # 국토교통부
    dg.get_tta_news(ft)     # 한국정보통신기술협회

    get_recruit_people_info(ft)  # 모니터링 요원 모집공고ㅓ
    get_rate_of_process_sgx(ft)  # 공정률 확인


def main():
    ft = FTbot()

    finding_and_tweet(ft)
    finding_and_mail(ft)
    deprecated(ft, False)

    db_table_check()


if __name__ == '__main__':
    main()
