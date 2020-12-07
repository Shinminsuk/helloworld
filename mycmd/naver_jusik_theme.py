#naver 주식 관련 
# 주식 테마 링크의 전체 리스트를 다운받는 모듈 

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import re
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse, parse_qs
import xlwt   # pip install xlwt 실행 후 수행

#### 사전 셋팅 (테마주 리스팅) #######################
surl = 'https://finance.naver.com'
url = 'https://finance.naver.com/sise/theme.nhn?'
#페이지 링크 https://finance.naver.com/sise/theme.nhn?&page=2
params = { 'page' : '1' }
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}

#### 마지막 페이지 가져오기 ####
html = requests.get(url, headers = headers, params = params )
soup = BeautifulSoup(html.text, 'html.parser')
p = re.compile('[0-9]+')
#page = soup.find_all('table.Nnavi td a')
page = soup.select('table.Nnavi td a')
page = p.search(page[-1]['href']).group()
page = int(page)

#판다스 정리를 위한 리스트 생성 
nums = [] # 번호 'div.wr-num'
titles = [] # 테마제목
turls = [] # 테마주 주소 
tuds = [] # 테마의 등락률 
names = [] # 개별주식이름
links = [] # 개별주식상세페이지 
codes = [] # 개별주식 코드명 
ju_code = {} # name, code 로 구성된 딕셔너리 
prices = [] # 개별주식의 현재가
explains = [] #개별주식의 편입사유 
dates = [] # 검색한 일자시간을 등록하기 위한 's'
no = 1
#검색일자시간을 넣기위한 내용
now = time.localtime()
s = '%04d-%02d-%02d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
ss = '%04d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)

#### 스크래핑 시작 #################

## 전체페이지를 하려면
for i in range(1, page+1) :
#for i in range(1, 2) :
    params.update({'page' : i })
    html = requests.get(url, headers = headers, params = params )
    soup = BeautifulSoup(html.text, 'html.parser')
    contents = soup.find('div', id = 'contentarea_left').find_all('tr')
    #contents = soup.select('div#contentarea_left table.theme tr')

    for tr in contents:  # 1페이지에 있는 
        try : 
            title = tr.select_one('td.col_type1 a').text  #테마명 
            titlelink = tr.select_one('td.col_type1 a')['href']
            turl = surl + titlelink # 링크로 전체주소 만들기 # 테마명 링크
            tud = tr.select_one('td.col_type2 span') # 전일대비 등락률
            if tud :
                tud = tr.select_one('td.col_type2 span').text.strip()
            else :
                tud = ""
            # 테마명령크로 개별 테마내 종목 가져오기
            # 각 개별주식의 코드를 딕셔너리로 저장 dic = {'종목명' : '코드'}
            thtml = requests.get(turl, headers=headers)
            soup = BeautifulSoup(thtml.text, 'html.parser')
            contents = soup.select('#contentarea > div:nth-child(5) tr')
            for content in contents : # 전체
                try : 
                    td = content.select('td')
                    #print(len(td), type(td))
                    name = td[0].select_one('a').text  # 주식이름
                    link = td[0].select_one('a')['href'] #개별주식의 상세페이지
                    code = parse_qs(link)
                    code = code['/item/main.nhn?code'][0] # 해당 종목의 코드를 추출
                    explain = td[1].text.replace('테마 편입 사유','').replace('\n','').strip()
                    price = td[2].text
                    link = surl + link
                except :
                    continue
                nums.append(no)
                titles.append(title) # 테마제목
                turls.append(turl) # 테마주 주소 
                tuds.append(tud) # 테마의 등락률 
                names.append(name) # 개별주식이름
                links.append(link) # 개별주식상세페이지 
                codes.append(code) # 개별주식 코드명 
                prices.append(price) # 개별주식의 현재가
                explains.append(explain) #개별주식의 편입사유 
                dates.append(ss) # 검색한 일자시간을 등록하기 위한 's'
                ju_code[name] = code # name, code 로 구성된 딕셔너리 
            print(title, '테마주가 끝났습니다. ', no)
            no += 1      
        except : 
            continue
        
# 내역을 판다스로 정리 (테마 전체)
theme_jusik = pd.DataFrame()
theme_jusik['번호'] = nums
theme_jusik['테마이름'] = titles
theme_jusik['테마주소'] = turls 
theme_jusik['테마등락률'] = tuds
theme_jusik['주식이름'] = names
theme_jusik['세부링크'] = links
theme_jusik['주식코드'] = codes
theme_jusik['현재가'] = prices
theme_jusik['편입사유'] = explains
theme_jusik['검색일자'] = dates

#저장경로 폴더 지정
fdir = 'c:\\doit\\data\\'
os.chdir(fdir)
fx_name = fdir+'theme_jusik_'+s+'.xls'
fc_name = fdir+'theme_jusik_'+s+'.csv'

# csv 형태로 저장하기
theme_jusik.to_csv(fc_name, encoding="utf-8-sig")
print("csv 파일 저장 경로: %s" %fc_name)

# ju_code 는 딕셔너리 (주식명, 코드명)
# ju_code_pd = pd.DataFrame(list(ju_code.items()), columns=['주식명', '코드명'])
# ju_code_pd.to_csv(fdir+'ju_code_pd_'+s+'.csv', encoding="utf-8-sig")
                        