"""brute_web_crawler web scrawling command line tool."""
# -*- coding: utf-8 -*-
import cgitb
import json
import logging
import os
import time
from datetime import datetime, timedelta
from envparse import env
from pymongo import MongoClient
from random import choice
from requests import codes, get, post
from twython import Twython, TwythonError
from urllib.request import getproxies

# gmail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# custom
from brute_web_crawler import defaults
from brute_web_crawler.crawl_daum import UseDaum
from brute_web_crawler.crawl_etc import ETC
from brute_web_crawler.crawl_github import UseGithub
from brute_web_crawler.crawl_korea import UseDataKorea
from brute_web_crawler.crawl_naver import UseNaver
from brute_web_crawler.crawl_tech_blog import TechBlog

cgitb.enable(format='text')
USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
                'Safari/536.5'), )


class BW:  # Brute Web crawler
    def __init__(self):
        self.mongodb_check_and_init()

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
        self.apt_svc_key = os.environ.get('DATA_APT_API_KEY')
        try:
            self.apt_dong = env('REALESTATE_DONG', cast=list)
        except:
            pass
        self.apt_district_code = env('REALESTATE_DISTRICT_CODE', cast=list)
        # self.apt_trade_apt = os.environ.get('DATA_GO_KR', 'apt', raw=True)
        # self.apt_trade_size = os.environ.get('DATA_GO_KR', 'size', raw=True)

        self.rate_of_process_key = os.environ.get('RATE_OF_PROCESS_KEY')
        self.area_dcd = os.environ.get('ROP_AREA_DCD')
        self.keyword = os.environ.get('ROP_KEYWORD')

        now = datetime.now()
        self.current_date = '%4d%02d%02d' % (now.year, now.month, now.day)
        log_path = '%s/log' % (os.getenv("HOME"))
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        log_file = '%s/bw_%s.log' % (log_path, self.current_date)
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

    def mongodb_check_and_init(self):
        self.db_client = MongoClient('localhost', 27017)
        self.db = self.db_client.post_tweet
        self.db_collections = self.db.sent_msg

        exp = datetime.now() - timedelta(days=60)  # store data for 60 days
        expire_date = '%04d%02d%02d' % (exp.year, exp.month, exp.day)
        self.db_collections.remove({'post_time': {'$lt': expire_date}})

    def is_already_sent(self, name, url):
        colls = self.db_collections.find({'$and': [{'name': name}, {'url': url}]})
        if colls.count() > 0:
            self.logger.info('[Already Sent] %s', url)
            return True  # already sent

        try:
            self.db_collections.insert_one({'name': name, 'url': url, 'post_time': self.current_date})
        except BaseException as e:
            self.logger.error('DB insert failed, [%s]:%s %s',  name, url, e)
        return False

    def post_tweet(self, post_msg, subject='None'):
        if post_msg is None:
            self.logger.info('[%s] no posting message', subject)
            return
        try:
            self.twit_post += 1
            if self.twit_post >= self.twit_post_limit:
                self.logger.error([self.twit_post], 'post failed, try after 15 minute')
                time.sleep(960)  # 15 * 60 sec + 60

            post_msg = self.check_max_tweet_msg(post_msg)
            self.twitter.update_status(status=post_msg)
            self.logger.info('Tweet: %s [%d/180]', post_msg, self.twit_post)
        except TwythonError as e:
            self.logger.error('TwythonError: %s [%s]', e, post_msg)

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

    def get_proxies(self):
        proxies = getproxies()
        filtered_proxies = {}
        for key, value in proxies.items():
            if key.startswith('http'):
                if not value.startswith('http'):
                    filtered_proxies[key] = 'http://%s' % value
                else:
                    filtered_proxies[key] = value
        return filtered_proxies

    # Referrence from
    # https://github.com/gleitz/howdoi/blob/master/howdoi/howdoi.py
    # http://docs.python-requests.org/en/master/user/advanced/
    def request_and_get(self, url, name):
        try:
            r = get(url, headers={'User-Agent': choice(USER_AGENTS)}, proxies=self.get_proxies(), verify=False)
            if r.status_code != codes.ok:
                self.logger.error('[%s] request error, code=%d', name, r.status_code)
                return None
            return r
        except:
            self.logger.error('[%s] connect fail', name)
            return None


def find_tech_blogs(bw):
    t = TechBlog(bw)

    t.awskr(bw)
    t.boxnwhisker(bw)
    t.daliworks(bw)
    t.devpools(bw)
    t.dramancompany(bw)
    t.goodoc(bw)
    t.kakao(bw)
    t.lezhin(bw)
    t.linchpinsoft(bw)
    t.naver(bw)
    t.naver_nuli(bw)
    t.netmanias(bw)
    t.ridi(bw)
    t.skplanet(bw)
    t.spoqa(bw)
    t.tosslab(bw)
    t.tyle(bw)
    t.whatap(bw)
    t.woowabros(bw)


def deprecated(bw, run_type):
    if run_type is False:
        return

    # Popular twitter keyword search
    try:
        timeline_pop = bw.twitter.search(
            q='python', result_type='popular', count=1)
        bw.post_with_raw_timeline(timeline_pop)
    except TwythonError as e:
        bw.logger.error('TwythonError %s', e)

    E = ETC(bw)
    naver_popular_news = E.get_naver_popular_news(bw)
    if (type(naver_popular_news) is list) and (len(naver_popular_news) > 0):
        bw.send_gmail('Naver popular news', naver_popular_news)

    rd = E.get_realestate_daum(bw)
    if (type(rd) is list) and (len(rd) > 0):
        bw.send_gmail('Daum realestate', rd)

    n = UseNaver(bw)
    naver_news = n.search_today_information_and_technology(bw)
    if (type(naver_news) is list) and (len(naver_news) > 0):
        bw.send_gmail('NAVER IT news', naver_news)


def finding_and_mail(bw):
    E = ETC(bw)
    rmk = E.get_realestate_mk(bw)
    if (type(rmk) is list) and (len(rmk) > 0):
        bw.send_gmail('MBN realestate', rmk)

    nate_rank_news = E.search_nate_ranking_news(bw)
    if (type(nate_rank_news) is list) and (len(nate_rank_news) > 0):
        bw.send_gmail('NATE IT news rank', nate_rank_news)

    daum = UseDaum(bw)
    daum_blog = daum.request_search_data(bw, req_str="마포")
    if (type(daum_blog) is list) and (len(daum_blog) > 0):
        bw.send_gmail('Daum Blogs', daum_blog)


def finding_and_tweet(bw):
    # Tech
    find_tech_blogs(bw)

    g = UseGithub(bw)
    g.get_repo(bw, lang='python', min_star=3, past=1)
    g.get_repo(bw, lang='javascript', min_star=3, past=1)
    g.get_repo(bw, lang=None, min_star=3, past=1)  # all languages

    E = ETC(bw)
    E.search_stackoverflow(bw, "activity", "python")
    E.search_stackoverflow(bw, "activity", "javascript")
    E.search_stackoverflow(bw, "activity", "racket")

    E.get_hacker_news(bw)
    E.get_rfc_draft_list(bw)
    E.get_raspberripy_news(bw)

    # Exhibition
    E.get_onoffmix(bw)
    E.get_coex_exhibition(bw)
    E.get_national_museum_exhibition(bw)

    # ETC
    dg = UseDataKorea(bw)
    dg.get_molit_news(bw)   # 국토교통부
    dg.get_kostat_news(bw)  # 통계청
    dg.get_tta_news(bw)     # 한국정보통신기술협회
    dg.realstate_trade(bw)
    dg.realstate_rent(bw)

    E.get_recruit_people_info(bw)  # 모니터링 요원 모집공고ㅓ
    E.get_rate_of_process_sgx(bw)  # 공정률 확인


def main():
    bw = BW()  # Brute Webcrawler

    finding_and_tweet(bw)
    finding_and_mail(bw)
    deprecated(bw, False)


if __name__ == '__main__':
    main()
