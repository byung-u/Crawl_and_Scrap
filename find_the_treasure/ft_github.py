#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import sys

from find_the_treasure.ft_sqlite3 import UseSqlite3
from github import Github


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
            repos = self.github_no_login.search_repositories("github",
                                                             created=date_range,
                                                             stars=star_range,
                                                             sort="stars",
                                                             order="desc",
                                                             language=lang,)
        else:  # hot
            repos = self.github_no_login.search_repositories("github",
                                                             pushed=date_range,
                                                             stars=star_range,
                                                             sort="stars",
                                                             order="desc",
                                                             language=lang,)
        return repos

    def sqlite_repo_process(self, ft, mode, repos):
        s = UseSqlite3('github')
        for repo in repos:
            try:
                lang = repo.get_languages()
                if len(lang) == 0:
                    continue
                ret = s.already_sent_github(repo.html_url)
                if ret:
                    ft.logger.info('Already sent: %s', repo.html_url)
                    continue
                short_url = ft.shortener_url(repo.html_url)
                # https://developer.github.com/v3/repos/
                s.insert_url(repo.html_url)
                msg = '[%s]\n★ %s\n\n%s\n%s\n#github' % (list(lang.keys())[0],
                                                         repo.stargazers_count,
                                                         short_url,
                                                         repo.description)
                msg = ft.check_max_tweet_msg(msg)
                ft.post_tweet(msg, 'Github')
            except:
                ft.logger.error('[GITHUB] repo_process failed: %s %s',
                                repo, sys.exc_info()[0])
        s.close()

    # Search range yesterday & today just 2 days.
    # If use over 2days, then occur rate-limiting.
    def get_github_great_repo(self, ft, mode='new', lang=None, min_star=0, past=1):

        date_range, star_range = self.get_check_options(past, stars=min_star)

        # https://developer.github.com/v3/search/#search-repositories
        # https://developer.github.com/v3/#rate-limiting
        repos = self.get_github_repos(mode, date_range, star_range, lang)
        if repos is None:
            ft.logger.error('[GITHUB]no repos')
            return []

        return self.sqlite_repo_process(ft, mode, repos)
