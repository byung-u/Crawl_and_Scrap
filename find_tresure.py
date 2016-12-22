#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import datetime
import sqlite3

from twython import Twython
from github import Github


class FTbot:  # Find Tresure 보물찾기 봇
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

    def post_tweet(self, post_msg):
        if post_msg is not None:
            self.twitter.update_status(status=post_msg)
        else:
            raise 'no messeage for posting'


class UseSqlite3:
    def __init__(self):
        self.conn = sqlite3.connect('sent_msg.db')
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS sent_msg (url text)')
        self.conn.commit()

    def already_sent(self, url):
        if url is None:
            return True  # ignore

        query = 'SELECT * FROM sent_msg WHERE url="%s"' % url
        self.c.execute(query)
        data = self.c.fetchone()
        if data is None:
            return False
        else:
            return True

    def insert_url(self, url):

        query = 'INSERT INTO sent_msg VALUES ("%s")' % url
        self.c.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()


class UseGithub:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.readfp(open('./ft.ini'))  # fix file path
        self.github_id = self.config.get('GITHUB', 'id')
        self.github_pw = self.config.get('GITHUB', 'pw')
        self.github_client_id = self.config.get('GITHUB', 'client_id')
        self.github_client_secret = self.config.get('GITHUB', 'client_secret')
        self.github_no_login = Github()

    def login(self):
        return Github(self.github_id, self.github_pw)

    def get_check_options(self, past=2, stars=0):
        check_date = datetime.datetime.now() - datetime.timedelta(days=past)
        date_range = '>=%s' % check_date.strftime('%Y-%m-%d')
        star_range = '>%s' % stars
        return date_range, star_range

    def get_new_github_repo(self, search_lang='all', search_star=0):
        date_range, star_range = self.get_check_options(stars=search_star)
        # https://developer.github.com/v3/search/#search-repositories
        # https://developer.github.com/v3/#rate-limiting
        repos = self.github_no_login.search_repositories(
                "github",
                created=date_range,
                stars=star_range,
                sort="stars",
                order="desc",
                language=search_lang
        )

        send_msg = []
        s = UseSqlite3()
        for repo in repos:
            print(repo)
            ret = s.already_sent(repo.html_url)
            if ret:
                continue
            else:
                # https://developer.github.com/v3/repos/
                s.insert_url(repo.html_url)
                if search_lang == 'all':
                    msg = '[GITHUB(new) %s]\nstar:%s\nlang:%s\n\n%s\n%s' % (
                            search_lang, repo.stargazers_count,
                            repo.language,
                            repo.html_url, repo.description)
                else:
                    msg = '[GITHUB(new) %s]\nstar:%s\n\n%s\n%s' % (
                            search_lang, repo.stargazers_count,
                            repo.html_url, repo.description)

                if len(msg) > 140:
                    msg = '%s...' % msg[0:137]

                send_msg.append(msg)

        s.close()
        return send_msg


def main():
    g = UseGithub()

    new_github_repo = g.get_new_github_repo('python', 0)
    ft = FTbot()
    for i in range(len(new_github_repo)):
        print(new_github_repo[i])
        ft.post_tweet(new_github_repo[i])


if __name__ == '__main__':
    main()
