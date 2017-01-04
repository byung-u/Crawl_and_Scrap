#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import time
from twython import Twython

from ft_github import UseGithub
from ft_naver import UseNaver
from ft_etc import get_coex_exhibition, search_stackoverflow


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

    def post_tweet(self, post_msg):
        if post_msg is not None:
            # TODO: print -> logger
            print('Tweet: ', post_msg)
            self.twitter.update_status(status=post_msg)
        else:
            raise 'no messeage for posting'


def ft_post_tweet_array(ft, msg):
    for i in range(len(msg)):
        time.sleep(2)
        ft.post_tweet(msg[i])


def github_post_tweet(ft, g):

    msg = g.get_github_great_repo('hot', 'python', 200)
    if len(msg) > 0:
        ft_post_tweet_array(ft, msg)

    msg = g.get_github_great_repo('new', 'python', 0)
    if len(msg) > 0:
        ft_post_tweet_array(ft, msg)

    msg = g.get_github_great_repo('new', None, 3)  # None -> all language
    if len(msg) > 0:
        ft_post_tweet_array(ft, msg)


def main():
    ft = FTbot()

    g = UseGithub(ft)
    github_post_tweet(ft, g)

    n = UseNaver(ft)
    news = n.search_today_information_and_technology(ft)
    for i in range(len(news)):
        ft.post_tweet(news[i])

    exhibition = get_coex_exhibition(ft)
    ft_post_tweet_array(ft, exhibition)
    so = search_stackoverflow(ft)
    ft_post_tweet_array(ft, so)


if __name__ == '__main__':
    main()
