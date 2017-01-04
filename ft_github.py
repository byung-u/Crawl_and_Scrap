#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from github import Github
from ft_sqlite3 import UseSqlite3

MAX_TWEET_MSG = 140


class UseGithub:
    def __init__(self, ft):
        self.github_no_login = Github()

    def login(self, ft):
        return Github(ft.github_id, ft.github_p)

    def get_check_options(self, past, stars):
        check_date = datetime.datetime.now() - datetime.timedelta(days=past)
        date_range = '>=%s' % check_date.strftime('%Y-%m-%d')
        star_range = '>%s' % stars
        return date_range, star_range

    def get_github_repos(self, mode, date_range, star_range, lang):
        if mode == 'new':
            repos = self.github_no_login.search_repositories(
                    "github",
                    created=date_range,
                    stars=star_range,
                    sort="stars",
                    order="desc",
                    language=lang,
            )
        else:  # hot
            repos = self.github_no_login.search_repositories(
                    "github",
                    pushed=date_range,
                    stars=star_range,
                    sort="stars",
                    order="desc",
                    language=lang,
            )
        return repos

    def sqlite_repo_process(self, mode, repos):
        s = UseSqlite3('github')
        send_msg = []
        for repo in repos:
            lang = repo.get_languages()
            ret = s.already_sent_github(repo.html_url)
            if ret:
                print('Already sent: ', repo.html_url)
                continue
            else:
                # https://developer.github.com/v3/repos/
                s.insert_url(repo.html_url)
                msg = '[GITHUB(%s) %s]\nstar:%s\n\n%s\n%s' % (
                        mode,
                        list(lang.keys())[0],
                        repo.stargazers_count,
                        repo.html_url,
                        repo.description
                )
                msg_encode = msg.encode('utf-8')
                msg_encode_len = len(msg_encode)
                if msg_encode_len > MAX_TWEET_MSG:
                    over_len = msg_encode_len - MAX_TWEET_MSG
                    msg = '%s...' % msg[0:(len(msg)-over_len)]
                send_msg.append(msg)
        s.close()
        return send_msg

    # Search range yesterday & today just 2 days.
    # If use over 2days, then occur rate-limiting.
    def get_github_great_repo(self, mode='new', lang=None, min_star=0, past=1):

        date_range, star_range = self.get_check_options(past, stars=min_star)

        # https://developer.github.com/v3/search/#search-repositories
        # https://developer.github.com/v3/#rate-limiting
        repos = self.get_github_repos(mode, date_range, star_range, lang)
        if repos is None:
            print('no repos')
            return []

        return self.sqlite_repo_process(mode, repos)
