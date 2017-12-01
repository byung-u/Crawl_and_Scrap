#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import sys

from github import Github


class UseGithub:
    def __init__(self, bw):
        self.github_no_login = Github()

    def login(self, bw):
        return Github(bw.github_id, bw.github_p)

    def get_check_options(self, past, stars):
        check_date = datetime.datetime.now() - datetime.timedelta(days=past)
        date_range = '>=%s' % check_date.strftime('%Y-%m-%d')
        star_range = '>%s' % stars
        return date_range, star_range

    def search_repo(self, date_range, star_range, lang):
        return self.github_no_login.search_repositories("github",
                                                        created=date_range,
                                                        stars=star_range,
                                                        sort="stars",
                                                        order="desc",
                                                        language=lang,)

    def post_repo(self, bw, repos):
        for repo in repos:
            try:
                lang = repo.get_languages()
                if len(lang) == 0:
                    continue
                if bw.is_already_sent('GITHUB', repo.html_url):
                    continue
                short_url = bw.shortener_url(repo.html_url)
                # https://developer.github.com/v3/repos/
                msg = '[%s]\n★ %s\n%s\n%s\n\n#github' % (list(lang.keys())[0],
                                                         repo.stargazers_count,
                                                         repo.description,
                                                         short_url)
                bw.post_tweet(msg, 'Github')
            except:
                bw.logger.error('[GITHUB] repo_process failed: %s %s %s\n %s',
                                repo, sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

    # Search range yesterday & today just 2 days.
    # If use over 2days, then occur rate-limiting.
    def get_repo(self, bw, lang=None, min_star=0, past=1):

        date_range, star_range = self.get_check_options(past, stars=min_star)

        # https://developer.github.com/v3/search/#search-repositories
        # https://developer.github.com/v3/#rate-limiting
        repos = self.github_no_login.search_repositories("github",
                                                         created=date_range,
                                                         stars=star_range,
                                                         sort="stars",
                                                         order="desc",
                                                         language=lang, )
        if repos is None:
            bw.logger.error('[GITHUB]no repos')
            return []
        return self.post_repo(bw, repos)
