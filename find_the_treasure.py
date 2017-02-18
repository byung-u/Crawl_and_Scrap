#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import cgitb
import json
import time
from twython import Twython, TwythonError

from ft_github import UseGithub
from ft_data_go_kr import (UseDataKorea)
from ft_daum import UseDaum
from ft_defaults import MAX_TWEET_MSG
from ft_naver import UseNaver
from ft_sqlite3 import UseSqlite3

from ft_etc import (get_coex_exhibition,
                    search_stackoverflow,
                    search_nate_ranking_news,
                    get_naver_popular_news,
                    get_national_museum_exhibition,
                    get_realestate_daum,
                    get_realestate_mk,
                    get_rate_of_process_sgx,
                    get_hacker_news,
                    )

cgitb.enable(format='text')


class FTbot:  # Find the Treasure 보물찾기 봇
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.readfp(open('./ft.ini'))  # fix file path
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
        self.apt_trade_apt = self.config.get('DATA_GO_KR', 'apt', raw=True)
        self.apt_trade_size = self.config.get('DATA_GO_KR', 'size', raw=True)

        self.rate_of_process_key = self.config.get('DATA_GO_KR', 'rate_of_process_key', raw=True)
        self.area_dcd = self.config.get('DATA_GO_KR', 'area_dcd', raw=True)
        self.keyword = self.config.get('DATA_GO_KR', 'keyword', raw=True)

    def post_tweet(self, post_msg):
        if post_msg is not None:
            # TODO: print -> logger
            print('Tweet: ', post_msg)
            try:
                self.twitter.update_status(status=post_msg)
            except TwythonError as e:
                print(e)
        else:
            raise 'no messeage for posting'

    def match_soup_class(self, target, mode='class'):
        def do_match(tag):
            classes = tag.get(mode, [])
            return all(c in classes for c in target)
        return do_match


def ft_post_tweet_array(ft, msg):
    for i in range(len(msg)):
        time.sleep(1)
        ft.post_tweet(msg[i])


def github_post_tweet(ft, g):

    msg = g.get_github_great_repo('hot', 'python', 10)
    if len(msg) > 0:
        ft_post_tweet_array(ft, msg)

    msg = g.get_github_great_repo('new', 'python', 0)
    if len(msg) > 0:
        ft_post_tweet_array(ft, msg)

    msg = g.get_github_great_repo('new', None, 3)  # None -> all language
    if len(msg) > 0:
        ft_post_tweet_array(ft, msg)


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
        print("failed to send mail", str(e))


def ft_post_with_raw_timeline(ft, timeline):
    dump_tl = json.dumps(timeline)  # dict -> json
    tl = json.loads(dump_tl)
    for i in tl['statuses']:
        result = 'By @%s, %s' % (i['user']['screen_name'], i['text'])
        if len(result.encode('utf-8')) > MAX_TWEET_MSG:
                continue
        ft.post_tweet(result)


def finding_about_software(ft):
    g = UseGithub(ft)
    github_post_tweet(ft, g)

    so = search_stackoverflow(ft)  # python
    ft_post_tweet_array(ft, so)
    so = search_stackoverflow(ft, "activity", "racket")
    ft_post_tweet_array(ft, so)

    try:
        timeline_pop = ft.twitter.search(q='python', result_type='popular', count=5)
        ft_post_with_raw_timeline(ft, timeline_pop)
    except TwythonError as e:
        print(e)

    try:
        timeline_new = ft.twitter.search(q='python', result_type='recent', count=5)
        ft_post_with_raw_timeline(ft, timeline_new)
    except TwythonError as e:
        print(e)

    hn = get_hacker_news(ft)
    ft_post_tweet_array(ft, hn)


def finding_about_exhibition(ft):
    exhibition = get_coex_exhibition(ft)
    ft_post_tweet_array(ft, exhibition)

    nm = get_national_museum_exhibition(ft)
    ft_post_tweet_array(ft, nm)


def finding_about_realestate(ft):
    dg = UseDataKorea(ft)
    trade_msg = dg.ft_search_my_interesting_realstate(ft)
    ft_post_tweet_array(ft, trade_msg)

    naver_popular_news = get_naver_popular_news(ft)
    ft_post_tweet_array(ft, naver_popular_news)

    rd = get_realestate_daum(ft)
    ft_post_tweet_array(ft, rd)

    rmk = get_realestate_mk(ft)
    ft_post_tweet_array(ft, rmk)

    daum = UseDaum(ft)
    daum_blog = daum.request_search_data(ft, req_str="마포 자이")
    if len(daum_blog) > 0:
        send_gmail(ft, 'Daum Blogs', daum_blog)

    sgx = get_rate_of_process_sgx(ft)
    ft.post_tweet(sgx)


def finding_about_news(ft):
    # Send email
    nate_rank_news = search_nate_ranking_news(ft)
    if len(nate_rank_news) > 0:
        send_gmail(ft, 'NATE IT news rank', nate_rank_news)

    n = UseNaver(ft)
    naver_news = n.search_today_information_and_technology(ft)
    if len(naver_news) > 0:
        send_gmail(ft, 'NAVER IT news', naver_news)


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

    sqlite3.delete_expired_tuple()
    sqlite3.close()


if __name__ == '__main__':
    main()
