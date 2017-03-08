"""find_the_treasure web scrawling command line tool."""
# -*- coding: utf-8 -*-
import configparser
import cgitb
import json
import logging
import os
from datetime import datetime
from twython import Twython, TwythonError

from find_the_treasure.ft_github import UseGithub
from find_the_treasure.ft_data_go_kr import (UseDataKorea)
from find_the_treasure.ft_daum import UseDaum
from find_the_treasure.ft_naver import UseNaver
from find_the_treasure.ft_sqlite3 import UseSqlite3
from find_the_treasure import defaults

from find_the_treasure.ft_etc import (get_coex_exhibition,
                                      search_stackoverflow,
                                      search_nate_ranking_news,
                                      get_naver_popular_news,
                                      get_national_museum_exhibition,
                                      get_realestate_daum,
                                      get_realestate_mk,
                                      get_rate_of_process_sgx,
                                      get_hacker_news,
                                      get_recruit_people_info,
                                      get_rfc_draft_list,
                                      )

cgitb.enable(format='text')


class FTbot:  # Find the Treasure
    def __init__(self):
        self.config = configparser.ConfigParser()

        config_file = os.path.expanduser(defaults.CONFIG_FILE_PATH)
        self.config.readfp(open(config_file))

        self.twitter_app_key = self.config.get('TWITTER', 'app_key')
        self.twitter_app_secret = self.config.get('TWITTER', 'app_secret')
        self.twitter_access_token = self.config.get('TWITTER', 'access_token')
        self.twitter_access_secret = self.config.get(
                'TWITTER', 'access_secret')
        self.twitter_id = self.config.get('TWITTER', 'id')
        self.twitter = Twython(
                self.twitter_app_key,
                self.twitter_app_secret,
                self.twitter_access_token,
                self.twitter_access_secret
        )

        self.github_id = self.config.get('GITHUB', 'id')
        self.github_p = self.config.get('GITHUB', 'p_w')
        self.github_client_id = self.config.get('GITHUB', 'client_id')
        self.github_client_secret = self.config.get('GITHUB', 'client_secret')

        self.naver_client_id = self.config.get('NAVER', 'client_id')
        self.naver_secret = self.config.get('NAVER', 'client_secret')

        self.daum_client_id = self.config.get('DAUM', 'client_id')
        self.daum_secret = self.config.get('DAUM', 'client_secret')
        self.daum_app_key = self.config.get('DAUM', 'app_key')

        self.google_id = self.config.get('GOOGLE', 'id')
        self.google_p = self.config.get('GOOGLE', 'p_w')
        self.gmail_from_addr = self.config.get('GOOGLE', 'from_addr')
        self.gmail_to_addr = self.config.get('GOOGLE', 'to_addr')

        self.apt_trade_url = self.config.get('DATA_GO_KR', 'apt_trade_url')
        self.apt_trade_svc_key = self.config.get('DATA_GO_KR', 'apt_rent_key', raw=True)
        self.apt_trade_dong = self.config.get('DATA_GO_KR', 'dong')
        self.apt_trade_district_code = self.config.get('DATA_GO_KR', 'district_code')
        # self.apt_trade_apt = self.config.get('DATA_GO_KR', 'apt', raw=True)
        # self.apt_trade_size = self.config.get('DATA_GO_KR', 'size', raw=True)

        self.rate_of_process_key = self.config.get('DATA_GO_KR', 'rate_of_process_key', raw=True)
        self.area_dcd = self.config.get('DATA_GO_KR', 'area_dcd', raw=True)
        self.keyword = self.config.get('DATA_GO_KR', 'keyword', raw=True)

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
                self.twitter.update_status(status=post_msg)
                self.logger.info('Tweet: %s', post_msg)
            except TwythonError as e:
                self.logger.error('TwythonError: %s', e)
        else:
            self.logger.error('[%s] no messeage for posting', subject)
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
            over_len = msg_len - defaults.MAX_TWEET_MSG + 3  # 3 means '...'
            msg_encode = msg_encode[0:(msg_len-over_len)]
            msg = '%s...' % msg_encode.decode("utf-8", "ignore")
            self.logger.info('[Over 140]%s', msg)
        return msg


def ft_post_tweet_array(ft, msg, subject=None):
    if type(msg) is not list:
        ft.logger.error('ft_post_tweet_array failed, [%s] %s', subject, msg)
        return
    if len(msg) <= 0:
        ft.logger.error('ft_post_tweet_array failed, [%s] no message', subject)
        return

    for i in range(len(msg)):
        ft.post_tweet(msg[i], subject)


def github_post_tweet(ft, g):

    msg = g.get_github_great_repo(ft, 'hot', 'python', 10)
    ft_post_tweet_array(ft, msg, 'Github')

    msg = g.get_github_great_repo(ft, 'new', 'python', 0)
    ft_post_tweet_array(ft, msg, 'Github')

    msg = g.get_github_great_repo(ft, 'new', None, 3)  # None -> all language
    ft_post_tweet_array(ft, msg, 'Github')


def send_gmail(ft, subject, body):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    if type(body) is list:
        send_msg = '\n'.join(body)
    else:
        send_msg = body

    gmail_user = ft.google_id
    gmail_pwd = ft.google_p
    FROM = ft.gmail_from_addr
    TO = ft.gmail_to_addr

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
        print('[%s] successfully sent the mail' % subject)
    except BaseException as e:
        ft.logger.error('failed to send mail: %s', str(e))


def ft_post_with_raw_timeline(ft, timeline):
    dump_tl = json.dumps(timeline)  # dict -> json
    tl = json.loads(dump_tl)
    for i in tl['statuses']:
        result = 'By @%s, %s' % (i['user']['screen_name'], i['text'])
        if len(result.encode('utf-8')) > defaults.MAX_TWEET_MSG:
                continue
        ft.post_tweet(result, 'raw_timeline')


def finding_about_software(ft):
    g = UseGithub(ft)
    github_post_tweet(ft, g)

    so = search_stackoverflow(ft)  # python
    ft_post_tweet_array(ft, so, 'Stackoverflow')
    so = search_stackoverflow(ft, "activity", "racket")
    ft_post_tweet_array(ft, so, 'Stackoverflow')

    try:
        timeline_pop = ft.twitter.search(
                q='python', result_type='popular', count=5)
        ft_post_with_raw_timeline(ft, timeline_pop)
    except TwythonError as e:
        ft.logger.error('TwythonError %s', e)

    hn = get_hacker_news(ft)
    ft_post_tweet_array(ft, hn, 'Hacker News')

    rfc_draft = get_rfc_draft_list(ft)
    ft_post_tweet_array(ft, rfc_draft, 'RFC DRAFT')


def finding_about_exhibition(ft):
    exhibition = get_coex_exhibition(ft)
    ft_post_tweet_array(ft, exhibition, 'Coex')

    nm = get_national_museum_exhibition(ft)
    ft_post_tweet_array(ft, nm, 'National Museum')


def finding_about_realestate(ft):
    dg = UseDataKorea(ft)
    trade_msg = dg.ft_search_my_interesting_realestate(ft)
    ft_post_tweet_array(ft, trade_msg, 'Realestate korea')

    sgx = get_rate_of_process_sgx(ft)  # sgx: 신/그/자
    ft.post_tweet(sgx, 'rate of process')

    naver_popular_news = get_naver_popular_news(ft)
    if (type(naver_popular_news) is list) and (len(naver_popular_news) > 0):
        send_gmail(ft, 'Naver popular news', naver_popular_news)

    rd = get_realestate_daum(ft)
    if (type(rd) is list) and (len(rd) > 0):
        send_gmail(ft, 'Daum realestate', rd)

    rmk = get_realestate_mk(ft)
    if (type(rmk) is list) and (len(rmk) > 0):
        send_gmail(ft, 'MBN realestate', rmk)

    daum = UseDaum(ft)
    daum_blog = daum.request_search_data(ft, req_str="마포 자이")
    if (type(daum_blog) is list) and (len(daum_blog) > 0):
        send_gmail(ft, 'Daum Blogs', daum_blog)


def finding_about_news(ft):
    # Send email
    nate_rank_news = search_nate_ranking_news(ft)
    if (type(nate_rank_news) is list) and (len(nate_rank_news) > 0):
        send_gmail(ft, 'NATE IT news rank', nate_rank_news)

    n = UseNaver(ft)
    naver_news = n.search_today_information_and_technology(ft)
    if (type(naver_news) is list) and (len(naver_news) > 0):
        send_gmail(ft, 'NAVER IT news', naver_news)


def finding_about_etc(ft):

    recruit_info = get_recruit_people_info(ft)
    ft_post_tweet_array(ft, recruit_info, 'Recruit Info')


def main():
    ft = FTbot()
    sqlite3 = UseSqlite3()

    # Github, Stackoverflow, Twitter
    finding_about_software(ft)
    # Coex, National Museum
    finding_about_exhibition(ft)
    # Data.go.kr, MBN, Naver. Daum
    finding_about_realestate(ft)
    # Nate, Daum
    finding_about_news(ft)
    # etc
    finding_about_etc(ft)

    sqlite3.delete_expired_tuple()
    sqlite3.close()


if __name__ == '__main__':
    main()