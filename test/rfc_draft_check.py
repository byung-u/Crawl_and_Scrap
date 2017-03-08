#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from requests import get


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def main():
    # root_url = 'http://goodmonitoring.com'
    url = 'https://www.rfc-editor.org/current_queue.php'
    r = get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup)
    rfc_draft_msg = []
    
    for n in soup.find_all(match_soup_class(['narrowcolumn'])):
        # print(len(n.text), n.text)
        for tr in n.find_all('tr'):
            try:
                tr.a['href']
            except TypeError:
                continue
            cnt = 0
            for td in tr.find_all('td'):
                if cnt == 0:
                    if td.text.find('AUTH48-DONE') == -1:
                        break
                    else:
                        state = td.text
                elif cnt == 3:
                    title = td.text.split()
                    version = title[0].split('-')
                    #print(version[-1])
                    for b in tr.find_all('b'):
                        #print('b:', b.a['href'])
                        rfc_draft = '[%s]\n%s(ver:%s)\n%s' % (
                                state.strip(),
                                '-'.join(version[1:-1]), 
                                version[-1], 
                                b.a['href'],
                                )
                        rfc_draft_msg.append(rfc_draft)
                cnt += 1
    #print(rfc_draft_msg)                            
    for i in range(len(rfc_draft_msg)):
        print(len(rfc_draft_msg[i]), rfc_draft_msg[i])


if __name__ == '__main__':
    main()
