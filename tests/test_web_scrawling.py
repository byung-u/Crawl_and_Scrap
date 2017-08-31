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

        url = 'http://d2.naver.com/d2.atom'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

        url = 'http://nuli.navercorp.com/sharing/blog/main'
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

    def test_spoqa(self):
        url = 'https://spoqa.github.io/index.html'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_kakao(self):
        url = 'http://tech.kakao.com'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_lezhin(self):
        url = 'http://tech.lezhin.com'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_ridi(self):
        url = 'https://www.ridicorp.com/blog/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_whatap(self):
        url = 'http://tech.whatap.io/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_woowa(self):
        url = 'http://woowabros.github.io'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_skplanet(self):
        url = 'http://readme.skplanet.com/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_daliworks(self):
        url = 'http://techblog.daliworks.net/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_devpools(self):
        url = 'http://devpools.kr/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_dramacompany(self):
        url = 'http://blog.dramancompany.com/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_goodoc(self):
        url = 'http://dev.goodoc.co.kr/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_netmanias(self):
        url = 'http://www.netmanias.com/ko/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_tyle(self):
        url = 'https://blog.tyle.io/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_realm(self):
        url = 'https://academy.realm.io/kr/'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_tta(self):
        url = 'http://www.tta.or.kr/news/tender.jsp'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

    def test_kostat(self):
        url = 'http://kostat.go.kr/portal/korea/kor_nw/2/1/index.board'
        r = get(url)
        self.assertIs(r.status_code, codes.ok)

if __name__ == '__main__':
    unittest.main()
