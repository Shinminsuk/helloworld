# itworld 사이트에 기사리스트를 출력하는 모듈

import requests
import re
import sys
import time
import os
from bs4 import BeautifulSoup

def getPage(url):
    req = requests.get(url)
    req.raise_for_status()
    return BeautifulSoup(req.text, 'html.parser')

#url = 'http://www.itworld.co.kr/t/35/%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%84%BC%ED%84%B0?page=1'
#params = {'page': '1'}
#res = requests.get(url, params = params)

'''
def getPage(url):
    """
    Utilty function used to get a Beautiful Soup object from a given URL
    """

    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    try:
        req = session.get(url, headers=headers)
    except requests.exceptions.RequestException:
        return None
    bs = BeautifulSoup(req.text, 'html.parser')
    return bs
'''



for i in range(1, 2):
    url = f'urls[1:]{i}'
    soup = getPage(url)
    contents = soup.find_all('h4', class_= 'news_list_full_size')
    for content in contents:
        title = content.text
        link = 'http://www.itworld.co.kr/'+content.find('a')['href']
        bs = getPage(link)
        head = bs.find('div', class_='node_body cb').text.strip()[:100] #100글자까지만 가져옴
        print(title.strip())
        print(link)
        print(head)
        print('='*100)