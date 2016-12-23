#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3


class UseSqlite3:
    def __init__(self):
        self.conn = sqlite3.connect('sent_msg.db')
        self.c = self.conn.cursor()
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS sent_msg (
        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        "url" text,
        "update_time" datetime
        )''')
        self.conn.commit()

        self.max_insert_id = 0
        self.c.execute('SELECT MAX(id) FROM sent_msg')
        data = self.c.fetchone()
        if data[0] is not None:
            self.max_insert_id = int(data[0])

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

        self.max_insert_id += 1
        query = 'INSERT INTO sent_msg VALUES (%d, "%s", CURRENT_TIMESTAMP)' % (
                self.max_insert_id, url)
        self.c.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()
