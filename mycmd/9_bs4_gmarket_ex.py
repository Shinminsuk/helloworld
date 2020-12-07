# gmarket 사이트 가격정보

import requests
import re
import sys
import time
import os
from bs4 import BeautifulSoup
import pandas as pd
import xlwt

#q = input('검색할 문자는? : ')
query_txt = '닌텐도 스위치 본체'

# url 사전 설정을 위한 헤더 파라미터 설정
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
params = { 'q' : query_txt, 'channel' : 'user', 'eventCategory' : 'SRP', 
          'sorter' : 'scoreDesc', 'listSize' : '36', 'isPriceRange' : 'false'}

gparams = { 'keyword' : query_txt, 'k' : '1'}

# 파일이름, 경로지정을 위한 설정
f_dir = 'c:\\doit\\data\\'
now = time.localtime()
s = '%04d-%02d-%02d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)

os.makedirs(f_dir+s+'-'+query_txt)
os.chdir(f_dir+s+'-'+query_txt)

ff_name=f_dir+s+'-'+query_txt+'\\'+s+'-'+query_txt+'.txt'
fc_name=f_dir+s+'-'+query_txt+'\\'+s+'-'+query_txt+'.csv'
fx_name=f_dir+s+'-'+query_txt+'\\'+s+'-'+query_txt+'.xls'

# 함수로 만들기 para미터 주기 연습 필요
def getPage(url):
    req = requests.get(url)
    res.raise_for_status()
    return BeautifulSoup(req.text, 'html.parser')

#print 된 출력을 txt 파일로 저장하기위한 설정
#orig_stdout = sys.stdout
#f = open(f_name , 'a' , encoding='UTF-8')
#sys.stdout = f
#time.sleep(1)

# 검색어를 지마켓사이트에서 범위페이지에서 검색해서 리스트로 저장
#url = "https://browse.gmarket.co.kr/search?p={}".format(i)
url = "https://browse.gmarket.co.kr/search?"

if 'gmarket' in url:
    params = gparams
else : 
    params = params

res = requests.get(url, headers=headers, params = params)
res.raise_for_status()
soup = BeautifulSoup(res.text, "lxml")

items = soup.find_all("div", attrs={"class":'box__item-container'})

# 판다스 리스트 만들기
no = 1
no2 = []
name2 = []
price2 =[]
link2 = []
sales2 = []

# 리스트 for 문 돌리기

for item in items:
    # 광고 제품은 제외
    ad_badge = item.find("span", attrs={"class":"ad-badge-text"})
    if ad_badge:
    #    print("  <광고 상품 제외합니다>")
        continue

    name = item.find("span", attrs={"class":"text__item"}).get_text() # 제품명
    # 애플 제품 제외
    if "케이스" in name or '라이트' in name or '필름' in name or '중고' in name:
        #print("  <상품 제외합니다>")
        continue

    price = item.find("strong", attrs={"class":"text text__value"}) # 가격

    if price :
        price = price.get_text()
    else :
        continue

    link = item.find("a", attrs={"class":"link__item"})["href"]
    
    try :
        sales = item.find('li', class_= 'list-item list-item__pay-count').find('span', class_='text')
        sales = re.search(r'\d.', sales.get_text()).group()
    except : 
        sales = "0"
    
#     #print(name, price, rate, rate_cnt)
#     print(f"제품명 : {name}")
#     print(f"가격 : {price}")
#     print(f"구매 : {sales}")
# #    print("바로가기 : {}".format("https://www.coupang.com" + link))
#     print("바로가기 : {}".format(link))
#     print("-"*100) # 줄긋기
    
    
    #판다스리스트 등록하기
    no2.append(no)
    name2.append(name)
    price2.append(price)
    link2.append(link)
    sales2.append(sales)
    
    no += 1

#판다스 만들기
gmarket = pd.DataFrame()
gmarket['번호']= no2
gmarket['제품명']= name2
gmarket['가격'] = price2
gmarket['링크'] = link2
gmarket['구매량'] = sales2

# txt 형식의 파일로 저장하기
f = open(ff_name, 'a',encoding='UTF-8')     
f.write(str(link2))
f.close( )
        
# csv 형태로 저장하기
gmarket.to_csv(fc_name,encoding="utf-8-sig")

# 엑셀 형태로 저장하기
gmarket.to_excel(fx_name)
    
#sys.stdout = orig_stdout
#f.close()
print('출력이 완료되었습니다. ')