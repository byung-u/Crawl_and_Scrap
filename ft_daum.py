#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import urllib.request
import re

from bs4 import BeautifulSoup
from requests import get

# from ft_sqlite3 import UseSqlite3


class UseDaum:
    def __init__(self, ft):
        pass

    def match_soup_find_all(self, target, mode='class'):
        def do_match(tag):
            classes = tag.get(mode, [])
            return all(c in classes for c in target)
        return do_match

    def read_other_blog_link(self, url):
        result = []

        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # print(soup)
        print('\n\n', url)
        for a in soup.find_all(self.match_soup_find_all(['view'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                result.append(p.text.replace('\n', ' ').strip())
        # for i in range(len(result)):
        #    print([i], result[i].strip())
        return result

    def read_daum_blog_link(self, url):
        result = []

        r = get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # print(soup)
        # print('\n\n', url)
        for a in soup.find_all(self.match_soup_find_all(['article'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                if p.text.find('adsbygoogle') >= 0:
                    continue
                result.append(p.text.strip())

        for a in soup.find_all(self.match_soup_find_all(['area_view'])):
            for p in soup.find_all('p'):
                if len(p.text.strip()) == 0:
                    continue
                if p.text.find('adsbygoogle') >= 0:
                    continue
                result.append(p.text.strip())
        return result

    def request_search_data(self, ft, req_str, mode='accu'):
        # https://apis.daum.net/search/blog?apikey={apikey}&q=다음&output=json
        url = 'https://apis.daum.net/search/blog?apikey=%s&q=' % (
                ft.daum_app_key)
        encText = urllib.parse.quote(req_str)
        options = '&result=20&sort=%s&output=json' % mode
        req_url = url + encText + options
        request = urllib.request.Request(req_url)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            data = response_body.decode('utf-8')
            res = json.loads(data)

            send_msg_list = []
            # http://xxx.tistory.com
            p = re.compile(r'^http://\w+.tistory.com/\d+')

            for i in range(len(res['channel']['item'])):
                # title = res["channel"]['item'][i]['title']
                m = p.match(res["channel"]['item'][i]['link'])
                if m is None:  # other
                    msg = self.read_other_blog_link(
                            res["channel"]['item'][i]['link'])
                else:  # tistory blog
                    msg = self.read_daum_blog_link(
                            res["channel"]['item'][i]['link'])

                send_msg_list.append(res["channel"]['item'][i]['link'])
                send_msg_list.append("\n".join(msg))

            send_msg = "\n".join(send_msg_list)
            send_msg = ''' %s ''' % send_msg
            self.send_gmail(ft, req_str, send_msg)
        else:
            print("Error Code:" + rescode)
            return None

    def send_gmail(self, ft, title, body):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        gmail_user = ft.google_id
        gmail_pwd = ft.google_p
        FROM = ft.google_from_addr
        TO = ft.google_to_addr

        msg = MIMEMultipart('alternative')
        msg['From'] = gmail_user
        msg['To'] = ft.google_to_addr
        msg['Subject'] = title
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, msg.as_string())
            server.quit()
            print('successfully sent the mail')
        except BaseException as e:
            print("failed to send mail", str(e))

        # request_search_data(self.ft, "신촌그랑자이", 'blog')
        # request_search_data(self.ft, "유아전집 4살", 'blog')
