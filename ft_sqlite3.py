#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3


class UseSqlite3:
    def __init__(self, mode='github'):
        self.conn = sqlite3.connect('sent_msg.db')
        self.c = self.conn.cursor()

        if mode == 'naver':
            self.c.execute('''
            CREATE TABLE IF NOT EXISTS sent_msg_naver (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "news" text,
            "update_time" datetime
            )''')
        else:  # github
            self.c.execute('''
            CREATE TABLE IF NOT EXISTS sent_msg_github (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "url" text,
            "update_time" datetime
            )''')

        self.conn.commit()

    def already_sent_naver(self, news):
        if news is None:
            return True  # ignore

        news = news.replace("\"", "'")
        query = 'SELECT * FROM sent_msg_naver WHERE news="%s"' % news
        self.c.execute(query)
        data = self.c.fetchone()
        if data is None:
            return False
        else:
            return True

    def already_sent_github(self, url):
        if url is None:
            return True  # ignore

        query = 'SELECT * FROM sent_msg_github WHERE url="%s"' % url
        self.c.execute(query)
        data = self.c.fetchone()
        if data is None:
            return False
        else:
            return True

    def insert_news(self, news):
        news = news.replace("\"", "'")
        query = '''INSERT INTO sent_msg_naver VALUES
        (NULL, "%s", CURRENT_TIMESTAMP)''' % news
        self.c.execute(query)
        self.conn.commit()

    def insert_url(self, url):
        query = '''INSERT INTO sent_msg_github VALUES
        (NULL, "%s", CURRENT_TIMESTAMP)''' % url
        self.c.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()
