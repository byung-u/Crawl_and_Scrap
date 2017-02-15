#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import cgitb
import time
from twython import Twython

from ft_github import UseGithub
from ft_data_go_kr import (UseDataKorea)
from ft_daum import UseDaum
from ft_naver import UseNaver
from ft_sqlite3 import UseSqlite3

from ft_etc import (get_coex_exhibition,
                    search_stackoverflow,
                    search_nate_ranking_news,
                    get_naver_popular_news,
                    get_national_museum_exhibition,
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

    def post_tweet(self, post_msg):
        if post_msg is not None:
            # TODO: print -> logger
            print('Tweet: ', post_msg)
            self.twitter.update_status(status=post_msg)
        else:
            raise 'no messeage for posting'

    def match_soup_class(self, target, mode='class'):
        def do_match(tag):
            classes = tag.get(mode, [])
            return all(c in classes for c in target)
        return do_match


def ft_post_tweet_array(ft, msg):
    for i in range(len(msg)):
        time.sleep(2)
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


def main():
    ft = FTbot()

    g = UseGithub(ft)
    github_post_tweet(ft, g)

    exhibition = get_coex_exhibition(ft)
    ft_post_tweet_array(ft, exhibition)

    so = search_stackoverflow(ft)  # python
    ft_post_tweet_array(ft, so)
    so = search_stackoverflow(ft, "activity", "racket")
    ft_post_tweet_array(ft, so)

    dg = UseDataKorea(ft)
    trade_msg = dg.ft_search_my_interesting_realstate(ft)
    ft_post_tweet_array(ft, trade_msg)

    naver_popular_news = get_naver_popular_news(ft)
    ft_post_tweet_array(ft, naver_popular_news)

    nm = get_national_museum_exhibition(ft)
    ft_post_tweet_array(ft, nm)

    # Send email
    nate_rank_news = search_nate_ranking_news(ft)
    send_gmail(ft, 'NATE IT news rank', nate_rank_news)

    n = UseNaver(ft)
    naver_news = n.search_today_information_and_technology(ft)
    send_gmail(ft, 'NAVER IT news', naver_news)

    daum = UseDaum(ft)
    daum_blog = daum.request_search_data(ft, req_str="마포 자이")
    send_gmail(ft, 'Daum Blogs', daum_blog)

    sqlite3 = UseSqlite3()
    sqlite3.delete_expired_tuple()
    sqlite3.close()


if __name__ == '__main__':
    main()
