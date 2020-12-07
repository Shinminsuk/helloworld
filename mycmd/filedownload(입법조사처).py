# 15차시기준
# 국회입법조사처 연구보고서
# https://www.nars.go.kr/report/list.do?page=1&cmsCode=CM0043&categoryId=&searchType=&searchKeyword=

# '#content > div.ls-box > ul > li:nth-child(1)'
#전체 코드 

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urlretrieve
from urllib import parse
from selenium import webdriver
import time
import requests
import re
import math
import os
import pandas as pd

# selenium으로 파일 저장함수 : 사전 링크 리스트를 txt로 저장한 것으로 가정
# 다운로드 파일이름 변경이 안되고 '다운로드폴더'에 저장됨 ==========  알아 볼 것

def get_pdf(ft_name): # 해당 파일(파일링크 주소txt 파일)을 불러와서 
    path = "c:/doit/chromedriver_win32/chromedriver.exe"
    driver = webdriver.Chrome(path)

    f = open(ft_name, 'r',encoding='UTF-8')  
    while True:
        line = f.readline()
        if not line: break
    #    print(line)
        driver.get(line)
        time.sleep(5) # 연속다운로드시 부하가 있을까 하여.
    print('다운로드 완료')
    f.close()

# pdf 다운로드 함수 # 사전 from urllib.request import Request, urlopen, urlretrieve
def get_download(url,fname): # 기존 함수에서 디렉토리를 뻈음. 
    try:
        print(url)
        urlretrieve(url,fname)
        time.sleep(10)  # 다운로드 시간을 좀 준다 10초
        print('다운로드 완료')
    except:
        return None
    
    
#첫 페이지 파싱

url = 'https://www.nars.go.kr/report/list.do?cmsCode=CM0043&categoryId=&searchType=&searchKeyword='
res = requests.get(url)
html = res.text
soup = BeautifulSoup(html,'html.parser')

# 총 페이지 건수 추출
ttl = soup.find('p', class_= 'ttl').text
p = re.compile('\d+').findall(ttl)
max_c = int(p[0])

res_c = int(input('가져올 건수를 입력하세요(최종페이지부터 가져옵니다): '))
page_cnt = math.ceil( res_c / 10)

#저장경로 폴더 지정
fdir = 'c:\\doit\\pdf\\'
os.chdir(fdir)

print ('총건수 : ', max_c, '중 가져올 건수 : ', res_c, '가져올 페이지 수: ', page_cnt, '저장경로 : ', fdir)

a_list = []
b_list = []  # 파일명 포함 총링크주소 
title_list = []
author_list = []
date_list = []
file_list = []
num = 0
# 자동 다운로드는 selenium 활용 함수로 , 'f'파일명으로 저장하기까지 완성

for i in range(1, page_cnt+1): # 숫자는 페이지 넘버
    url = 'https://www.nars.go.kr/report/list.do?cmsCode=CM0043&categoryId=&searchType=&searchKeyword='
    params = {'page' : i }
    resp = requests.get(url, params = params).text
    soup = BeautifulSoup(resp,'html.parser')
    lis = soup.find('ul', class_='brdl-tp1').find_all('li')

    # 'a'는 자바스크립트로 링크가 떨어져서 해당 주소와 원url을 합쳐서 url1을 도출함 
    for li in lis:
        title = li.find('div',class_='tt').get_text()
        #b = li.find('div', class_='zl').get_text()
        author = li.findAll('span')[2].get_text()
        date = li.findAll('span')[3].text
        a = li.findAll('a')[2]['href'] # a[0] 단축링크파일명 a[1] 한글파일명
        a = a.replace('javascript:fileDownLoad(','').replace(');','').replace("'","").split(",")
        url1 = 'https://www.nars.go.kr/fileDownload2.do?doc_id={}&fileName='.format(a[0]) # 한글파일명 제외한 링크
        #url1 = 'https://www.nars.go.kr/fileDownload2.do?doc_id={}&fileName={}'.format(a[0],a[1])
        a_list.append(a[0])
        b_list.append(url1)
        title_list.append(title)
        author_list.append(author)
        date_list.append(date)
        file_list.append(a[1])
        get_download(url1, a[1])  # 함수로 처리 (한글파일명제외해야 작동하는 듯 ascii 문제?)
        num += 1       

# 파일로 저장하기위해  pandas로 데이터프레임 만들기
reports = pd.DataFrame()
reports['다운로드링크'] = b_list
reports['제목'] = title_list
reports['저자'] = author_list
reports['날짜'] = date_list
reports['파일명'] = file_list
reports['링크파일명'] = a_list

# 엑셀 파일로 저장하기 
reports.to_excel(fdir+'reports.xls')

# txt 파일로 링크주소 리스트 저장하기 최종링크 주소
ft_name = fdir+'testtest.txt'
f = open( ft_name, 'w',encoding='UTF-8')  
for i in b_list:
    f.write(i)
    f.write('\n')
f.close( )

# txt 파일로 저장된 리스트로 파일다운로드 # 다운로드위치 지정은 아직 못함
#get_pdf(ft_name)

print ('총 ', num, '건 저장완료', '\n', '링크저장txt파일 : ', ft_name)
# 이거 아래가 안되네... get_download 함수
#        url1 = 'https://www.nars.go.kr/fileDownload2.do?'
#        params = {'doc_id': a[0], 'filename': a[1] }
#        params = parse.urlencode(params, doseq=True)
#        url2 = 'https://www.nars.go.kr/fileDownload2.do?'+params
#        url2 = url2.replace('%28','(').replace('%29',')').replace('+','%20')
#        urlretrieve(url2,fname)
#        get_download(url2, fname, fdir)

# pdf 다운로드 함수
#def get_download(url,fname,directory):
#    try:
#        os.chdir(directory)
#        print(url)
#        request.urlretrieve(url,fname)
#        print('다운로드 완료')
#    except:
#        return None

# requests 모듈로 header 정보에 크롬 브라우져의 User-Agent를 만들어서 보내는 방법
#headers = {
#    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
#}
#html = session.get(WIKI_URL, headers=headers).content