#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime


class UseSqlite3:
    def __init__(self, mode='etc'):
        self.conn = sqlite3.connect('sent_msg.db')
        self.c = self.conn.cursor()

        if mode == 'naver':
            self.c.execute('''
            CREATE TABLE IF NOT EXISTS sent_msg_naver (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "news" text,
            "update_time" datetime
            )''')
        elif mode == 'github':
            self.c.execute('''
            CREATE TABLE IF NOT EXISTS sent_msg_github (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "url" text,
            "update_time" datetime
            )''')
        else:  # etc
            self.c.execute('''
            CREATE TABLE IF NOT EXISTS sent_msg_etc (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "etc_type" text,
            "etc_info" text,
            "update_time" datetime
            )''')
        self.delete_expired_tuple(mode)
        self.conn.commit()

    def delete_expired_tuple(self, mode):
        now = datetime.now()
        # 2016-12-26 05:01:26
        time_str = '%4d-%02d-%02d %02d:%02d:%02d' % (
                now.year, now.month, now.day, now.hour, now.minute, now.second)
        if now.month < 3:
            time_str = '%4d-%02d-%02d %02d:%02d:%02d' % (
                    now.year-1, now.month+10, now.day,
                    now.hour, now.minute, now.second)
        else:
            time_str = '%4d-%02d-%02d %02d:%02d:%02d' % (
                    now.year, now.month-2, now.day,
                    now.hour, now.minute, now.second)
        if mode == 'naver':
            delete_query = """
            DELETE FROM sent_msg_naver WHERE update_time < '%s'""" % time_str
        elif mode == 'github':
            delete_query = """
            DELETE FROM sent_msg_github WHERE update_time < '%s'""" % time_str
        else:  # etc
            delete_query = """
            DELETE FROM sent_msg_etc WHERE update_time < '%s'""" % time_str
        print(delete_query)
        self.c.execute(delete_query)

    def already_sent_naver(self, news):
        if news is None:
            return False  # ignore

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
            return False  # ignore

        query = 'SELECT * FROM sent_msg_github WHERE url="%s"' % url
        self.c.execute(query)
        data = self.c.fetchone()
        if data is None:
            return False
        else:
            return True

    def already_sent_etc(self, etc_type, etc_info):
        if (etc_type is None) or (etc_info is None):
            return False

        etc_info = etc_info.replace("\"", "'")
        query = '''
        SELECT * FROM sent_msg_etc WHERE etc_type="%s" and etc_info="%s"''' % (
                etc_type, etc_info)
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

    def insert_etc(self, etc_type, etc_info):
        query = '''INSERT INTO sent_msg_etc VALUES
        (NULL, "%s", "%s", CURRENT_TIMESTAMP)''' % (etc_type, etc_info)
        self.c.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()
