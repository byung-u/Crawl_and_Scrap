#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from datetime import date


def datetime():
    d = date.today()
    print(d.strftime("%a, %0d %b %Y"))
    print('Mon, 05 Jun 2017')


def environ():
    dong = os.environ.get('REALESTATE_DONG')
    print(dong, type(dong))
    dong = os.environ.get('REALESTATE_DONG').replace(' ', '').split(',')
    for d in dong:
        print(d)
    # print(dong, type(dong))

import logging

def logging_test():
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('[%(levelname)8s] %(message)s')
    ch.setFormatter(formatter)
    
    logging.basicConfig(filename='example.log', 
                        format='[%(asctime)s] (%(levelname)8s) %(message)s',
                        datefmt='%I:%M:%S',
                        level=logging.INFO)
    
    
    logger = logging.getLogger('simple_example')
    logger.addHandler(ch)
    
    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    

def check_max_tweet_msg(msg):
    msg_encode = msg.encode('utf-8')
    msg_len = len(msg_encode)
    if msg_len > 140:
        over_len = msg_len - 140 + 3  # 3 means '...'
        msg_encode = msg_encode[0:(msg_len-over_len)]
        msg = '%s...' % msg_encode.decode("utf-8", "ignore")
    return msg


def message_len_check():
    m1 = 'test'
    m2 = 'Attempt to read and parse a list of filenames, returning a list of filenames which were successfully parsed. If filenames is a string, it is treated as a single filename. If a file named in filenames cannot be opened, that file will be ignored. This is designed so that you can specify a list of potential configuration file locations (for example, the current directory, the user’s home directory, and some system-wide directory), and all existing configuration files in the list will be read. If none of the named files exist, the ConfigParser instance will contain an empty dataset. An application which requires initial values to be loaded from a file should load the required file or files using read_file() before calling read() for any optional files'
    m3 = '친근한 관광도시 조성에 박차를 가하겠다는 박 구청장은  강조했다. 마포구는 교육문화사업에도 역량을 집결하고 있다. 간략히 제시코자 한다. 빠르게 진행되는 4차 산업혁명시대를 이끌어갈 인재 양성과 꿈과 끼가 넘치는 청소년들의 꿈이 실현될 수 있도록 돕고자 한다. 그 일환으로 마포중앙도서관 및 청소년교육센터가 옛 구청사 부지에 올해 10월 준공을 앞뒀다. 중앙도서관, 청소년교육센터, 근린생활시설, 공영주차장 등의 하드웨어와 ICT(정보통신기술)시대에 부응하는 시설이다.'

    m = check_max_tweet_msg(m1)
    print(len(m), m)
    m = check_max_tweet_msg(m2)
    print(len(m), m)
    m = check_max_tweet_msg(m3)
    print(len(m), m)
    print(len(m.encode('utf-8')))

    # m4 = '[HackerNews]\nRank:50. Prenda Saga Update: John Steele Pleads Guilty, Admits Entire Scheme (popehat.com)\nhttp://me2.do/Fh3XsJ6l'
    m4 = '[HackerNews]\nRank:46. Snap Tumbles Below IPO Opening Price as Analysts Say Sell (bloomberg.com)\nhttp://me2.do/GyvBERjQ'

    print(len(m4))



def create_new(file_name, out_file_name):
    fw = open(out_file_name, 'w')
    with open(file_name) as f:
        for idx, line in enumerate (f):
            if idx % 2 == 0:
                fw.write(line)
    f.closed
    fw.close()

def regex_test():
    item = '<거래금액>    72,200<건축년도>2005<년>2017<법정동> 상암동<아파트>상암월드컵파크7단지<월>8<일>21~31<전용면적>84.74<지번>1660<지역코드>11440<층>7'
    item = re.sub('<.*?>', ' ', item)
    info = item.split()
    print(info)

def env_parse():
    foo = env('REALESTATE_DONG', cast=list)
    print(foo, type(foo))

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def check_and_parsing(s):
    rep = { "&lt": "", "&amp": "", "&apos": "", "&quot": "",
            ";": "", "<b>": "", "</b>": "", "&gt": "", "‘": "", "’": "", u"\xa0": u"",
            "“": "",
            "”": "",
            }
    soup = BeautifulSoup(s, 'html.parser')
    d = date.today()
    today_str = d.strftime("%a, %0d %b %Y")
    msg = []
    for i, s in enumerate(soup.find_all(['link', 'title', 'description', 'pubdate'])):
        if i < 3:
            continue
        if (i - 3) % 4 == 0:  # title
            print([i], 'title', s.text)
            msg.append(replace_all(s.text, rep))
        elif (i - 3) % 4 == 1:  # url
            print([i], 'url', s.text)
            msg.append(replace_all(s.text, rep))
        elif (i - 3) % 4 == 2:  # desc
            print([i], 'desc', s.text)
            msg.append(replace_all(s.text, rep))
            # if s.text.startswith(today_str):
            #     print('------>> ', msg)
            # print('[1]', msg[0])
            # print('[2]', msg[1])
            # print('[3]', msg[2])
            # print('[4]', msg[3])
            del msg[:]
        elif (i - 3) % 4 == 3:  # date
            print([i], 'date', s.text)
            msg.append(replace_all(s.text, rep))

def main():
    s = "javascript:myBagCheck('0001', '49', '0092', '4', this);"
    temp = s.split("'")
    print(temp[1])
    print(temp[3])
    print(temp[5])
    print(temp[7])



if __name__ == '__main__':
    main()
