import requests
import re
import sys
import time
import os
from bs4 import BeautifulSoup

# 파일로 저장하는 법 연습하기

def getPage(url, params):
    req = requests.get(url, params = params)
    req.raise_for_status()
    return BeautifulSoup(req.text, 'html.parser')

#url = 'http://www.itworld.co.kr/t/35/%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%84%BC%ED%84%B0?page=1'
#params = {'page': '1'}
#res = requests.get(url, params = params)


for i in range(1, 2):
#    url = f'http://www.itworld.co.kr/t/35/%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%84%BC%ED%84%B0?'
    url = f'http://www.itworld.co.kr/t/34/클라우드?'
    params = { 'page' : i}
    soup = getPage(url, params)
    contents = soup.find_all('h4', class_= 'news_list_full_size')
    for content in contents:
        title = content.text
        link = 'http://www.itworld.co.kr/'+content.find('a')['href']
        bs = getPage(link, '')
        head = bs.find('div', class_='node_body cb').text.strip()[:100]
        print(title.strip())
        print(link)
        print(head)
        print('='*100)