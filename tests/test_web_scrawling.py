import unittest

from datetime import datetime
from requests import get, codes
from time import gmtime, strftime


class TestUrlConn(unittest.TestCase):

    def test_coex(self):
        url = 'http://www.coex.co.kr/blog/event_exhibition?list_type=list'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_daum(self):
        url = 'http://realestate.daum.net/news'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_good_monitoring(self):
        url = 'http://goodmonitoring.com/xe/moi'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_hacker_news(self):
        url = 'https://news.ycombinator.com/news?p=0'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_mk(self):
        url = 'http://news.mk.co.kr/newsList.php?sc=30000020'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_molit(self):
        url = 'http://www.molit.go.kr/USR/NEWS/m_71/lst.jsp'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_nate(self):
        url = 'http://news.nate.com/rank/interest?sc=its&p=day&date=%s' % (strftime("%Y%m%d", gmtime()))
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_national_museum(self):
        url = 'https://www.museum.go.kr/site/korm/exhiSpecialTheme/list/current?listType=list'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_naver(self):
        now = datetime.now()
        date = '%4d%02d%02d' % (now.year, now.month, now.day)
        url = 'http://news.naver.com/main/list.nhn?sid1=001&mid=sec&mode=LSD&date=%s' % date
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

        url = 'http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=105'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_raspberripy(self):
        url = 'http://lifehacker.com/tag/raspberry-pi'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_rfc_draft(self):
        url = 'https://www.rfc-editor.org/current_queue.php'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_tech_blog(self):
        url = 'https://spoqa.github.io/index.html'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

        url = 'http://tech.kakao.com'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

        url = 'http://tech.lezhin.com'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

        url = 'http://d2.naver.com/d2.atom'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

        url = 'https://www.ridicorp.com/blog/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

        url = 'http://woowabros.github.io'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)


if __name__ == '__main__':
    unittest.main()
