#멀티캠퍼스 사이트의 과정링크를 가지고 도서 포함 목록을 추출함
#multicampusbooks_src.txt에 과정링크가 있어야 함
# 환급여부와 가격 추가 

from bs4 import BeautifulSoup     
from selenium import webdriver
import os
import pandas as pd
import time
import xlwt
from urllib.parse import urlparse 
from urllib.request import urlopen, urlretrieve

# with open('multicampusbooks.txt', 'r') as f: # txt파일에 링크주소를 기입
#     urls = f.readlines()
# urls = [line.rstrip('\n') for line in urls]  # 엔터로 된 파일을 리스트로 만들기

#2번 방법
dirs = '..\\complete\\'
txtname = 'multicampusbooks_src.txt'
csvname = 'multicampusbooks.csv'  # 판다스로 저장할 때
xlsname = 'multicampusbooks.xls' # 판다스로 저장할 떄
urls = open( dirs + txtname , 'r').read().split('\n')

#3번 방법
#urls = [line.rstrip('\n') for line in open('multicampusbooks.txt', 'r')]

#단순방법
#urls = ['http://el.multicampus.com/pls/cyber/zm_preview.show?p_subj=CG2451',
#       'http://el.multicampus.com/pls/cyber/zm_preview.show?p_subj=A39721']

# 셀레니움 사용

path = "c:/doit/chromedriver_win32/chromedriver.exe"
driver = webdriver.Chrome(path)


# 사전 셋팅
no = 0
no2 = 0
titles = []
urlsrc = []
book_titles = []
authors = []
booklinks = []
prices = []
hangubs = []

# 셀레니움 사용하여 루프
for url in urls :  # 구간 설정
#for url in urls[:len(urls)-1] : # 텍스트 파일 마지막이 엔터가 있으면 리스트 에러가 나서 마지막 줄은 안불러오는 걸로

    try : 
        driver.get(url) #링크명
        time.sleep(3) 
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h2').text  #과목명
        elements = soup.find('div', class_='txt')
        booktitle = elements.find('dt').text # 도서명
        price = soup.select_one('#wrap_new > div.study-info > div.info > table > tbody > tr:nth-child(2) > td:nth-child(2)').text
        hangub = soup.select_one('#wrap_new > div.study-info > div.info > table > tbody > tr:nth-child(2) > td:nth-child(4)').text
        ele1 = elements.find('dd').text
        ele2 = ele1.strip().split('\n')
        author = ele2[0].split(':')[1] #저자명
        # 판다스 정리를 위해 리스트로 어팬드
        titles.append(title)
        prices.append(price)
        urlsrc.append(url)
        book_titles.append(booktitle)
        authors.append(author)
        hangubs.append(hangub)
        #booklinks.append()  #예스24 링크 생성후
        no += 1 
        print('저장완료 : ', no)
        
    except :
        print('This page is missing something! Continuing.')
        no2 += 1
    
    
# 판다스 셋팅하기     
multi_book = pd.DataFrame()
multi_book['과목명'] = titles
multi_book['가격'] = prices
multi_book['링크'] = urlsrc
multi_book['도서명'] = book_titles
multi_book['저자'] = authors
multi_book['환급여부'] = hangubs
#multi_book['도서검색'] = booklinks

# csv 형태로 저장하기
#multi_book.to_csv('multicampusbooks.csv',encoding="utf-8-sig")  # csv 파일 인코딩은 'utf-8-sig' 인 것에 유의
#print(" csv 파일 저장 경로: %s" %fc_name)
# 최초 생성 이후 mode는 append
savename = dirs+csvname
if not os.path.exists(savename):
    multi_book.to_csv(savename, index=False, mode='w', encoding='utf-8-sig')
else:
    multi_book.to_csv(savename, index=False, mode='a', encoding='utf-8-sig', header=False)


# 엑셀 형태로 저장하기
import xlwt   # pip install xlwt 실행 후 수행
multi_book.to_excel(dirs+xlsname)

# csv 저장파일 확인하기 
#data = pd.read_csv(savename_csv)
#print(data)
    
#print('저장완료: ', no, '저장실패 : ' , no2, '저장경로: ', savename)
print(f'저장완료: {no}  저장실패 : {no2} 저장경로: {savename}')