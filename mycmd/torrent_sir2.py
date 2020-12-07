# torrent_sir 을 기반으로 전체 구분자에 대한 조회수 높은 2페이지를 출력한다

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import os
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse, parse_qs
import xlwt   # pip install xlwt 실행 후 수행

# https://torrentsir24.com/bbs/board.php?bo_table=movie

def find_elem(content, src, ex): # title soup 된 변수,  src 검색할주소 ex 'link'
    try:
        if ex == 'x':
            title = content.select_one(src)
        elif ex == 'link' :
            title = content.select_one(src)['href']
        else : 
            title = content.select_one(src).text.strip()
        return title 
    except:
        print(src, '확인 필요')
        return None

# 사전 셋팅
a = [['영화','bo_table=movie'],['드라마','bo_table=drama'],
    ['예능오락', 'bo_table=entertain'],['시사교양', 'bo_table=tv'],
    ['동영상' ,'bo_table=ani'],['애니메이션' ,'bo_table=ani&sca=애니메이션'],
    ['스포츠' ,'bo_table=ani&sca=스포츠'],['음악' ,'bo_table=music'],
    ['게임' ,'bo_table=game'],['유틸' ,'bo_table=util'],
    ['도서강좌', 'bo_table=lecture'],['어린이' ,'bo_table=child'],['+19', 'bo_table=gallery']]

# 검색할 것을 딕셔너리로 사전설정 1, 2로 나눈이유는 밑에 soup를 불러오는 두가지가 달라서 단순구분용
dic1 = {'num' : 'div.wr-num', 'photo' : 'div.wr-thumb','title' : 'div.wr-subject a', 'link' : 'div.wr-subject a',
          'lu_cnt' : 'div.wr-hit','date' : 'div.wr-date', 'price' : ''}
dic2 = {'title2': 'h1', 'date2': 'span.pull-right', 'size': 'b.font-16', 'tolink': 'a.list-group-item',
        'toname': 'a.list-group-item', 'maglink': 'ul.list-group li.list-group-item a'}
params = {}  # requests.get 으로 가져올 때 파라미터값을 넣기 위한 설정

7# 목록을 출력
for i, k in enumerate(a):
    if i%4 == 3 :
        print('{0:>2}'.format(i) ,":", '{0:<20}'.format(k[0]), end="\n")
    else :
        print("{0:>2}".format(i) ,":", '{0:<20}'.format(k[0]), end="")

# 입력을 받음
# q = int(input('검색숫자를 넣으세요 : ')) # 파라미터 설정을 위한 숫자값
# page = int(input('검색할 페이지 숫자를 넣으세요 : '))
# cnt = int(input('조회수 몇건 이상파일을 찾습니까 : ')) # 조회수 보다 높은 것만 정리함
# qq = int(input(' 조회순으로 정렬할까요? 1을 입력하면 정렬합니다. : ')) # 조회수가 많은 것부터 출력한다

q = int(input('검색숫자를 넣으세요 : ')) # 파라미터 설정을 위한 숫자값 이숫자 이후의 것을 불러옴
page = 2
cnt = 0 # 조회수 보다 높은 것만 정리함
qq = 1 # 조회수가 많은 것부터 출력한다

#파일명에 검색일자시간을 넣기위한 내용과 폴더 및 파일명 지정 
now = time.localtime()
s = '%03d-%02d-%02d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
fdir = 'c:\\doit\\data\\'
#os.chdir(fdir)
fx_name = fdir+'torrent_sir_'+s+a[int(q)][0]+'.xls'
fc_name = fdir+'torrent_sir_'+s+a[int(q)][0]+'.csv'

#판다스 정리를 위한 리스트 생성 (https://torrentsir24.com/bbs/board.php?bo_table=movie&page=1)
coms = [] # a 분야를 선택하는 
nums = [] # 번호 'div.wr-num'
photos = [] # 포토 'div.wr-thumb'
titles = [] # 제목 'div.wr-subject a' text  #strip()
links = [] # 링크 'div.wr-subject a' 'href # attrs('href')
lu_cnts = [] # 조회수 'div.wr-hit' #int
dates = []# 날짜 'div.wr-date'

#내부 사이트(예시 : https://torrentsir24.com/bbs/board.php?bo_table=movie&wr_id=15311)
titles2 = [] # 제목 'h3.panel-title' 
dates2 = [] # 날짜시간 'span.pull-right'
sizes = [] # 용량 'b.font-16'
tolinks = [] # 토렌트파일링크 'a.list-group-item' 
tonames = [] # 토렌트파일네임 'a.list-group-item' text # torrent로 끝나도록 re
tocnts = [] # 토렌트 파일 갯수 
maglinks = [] # 마그넷주소 'ul.list-group li.list-group-item a'
no = 1 # 저장 갯수 설정을 위한 넘버링

#입력값이 있으면 업데이트 
if qq == 1 : 
    params.update({'sop' : 'and', 'sst' : 'wr_hit', 'sod' : 'desc', 'sfl' : '', 'stx' : '', 'sca' : ''})
    

##### 실제 스크래핑 시작 ######################################################################
for i in a[q:] :
    com = i[0]

#헤더, 파라미터 사전 셋팅을 위한 설정
    url = 'https://torrentsir24.com/bbs/board.php?'
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
    params.update(parse_qs(i[1]))  #

    for i in range(1, page+1) : 
        params.update({'page' : i})
        html = requests.get(url, headers=headers, params=params)
        soup = BeautifulSoup(html.text, 'html.parser')
        #contents = soup.find('table',class_='div-table').find('tbody').find_all('tr')
        contents = soup.select('li.list-item')

        for tr in contents :
            title = find_elem(tr, dic1['title'], 'text')  # 파일명
            t = re.compile('(.*?])')
            title = t.match(title)
            if title :
                title = title.group() # 정규표현식으로 구분자를 구분
            else :
                title = ""
            link = find_elem(tr, dic1['link'], 'link') # 세부링크
            date = find_elem(tr, dic1['date'], 'text')  # 등록일
            lu_cnt = find_elem(tr, dic1['lu_cnt'], 'text') # 조회수
            if lu_cnt : 
                lu_cnt = int(lu_cnt)
                if lu_cnt < cnt :
                    continue
            else :
                lu_cnt = 0
            # 세부링크 한번더 
            shtml = requests.get(link, headers=headers)
            soup = BeautifulSoup(shtml.text, 'html.parser')
            title2 = find_elem(soup, dic2['title2'], 'text') #제목
            date2 = find_elem(soup, dic2['date2'], 'text')
            size = find_elem(soup, dic2['size'], 'text')
            tocnt = len(soup.select('a.list-group-item'))
            tolink = find_elem(soup, dic2['tolink'], 'x') # 링크
            maglink = find_elem(soup, dic2['maglink'], 'x')
            if maglink :
                maglink = maglink.text
            else :
                maglink = '마그넷링크없음'
            if tolink :
                toname = tolink.text
                tolink= tolink['href']
            else :
                tolink= '링크에러?'
            coms.append(com)
            titles.append(title)
            titles2.append(title2)
            links.append(link)
            sizes.append(size)
            dates2.append(date2)
            tolinks.append(tolink)
            tonames.append(toname)
            maglinks.append(maglink)
            lu_cnts.append(lu_cnt)
            tocnts.append(tocnt)
            
            print( no, '번째 파일 저장')
            no += 1

# 리스트를 판다스로 저장하기
torrent_sir = pd.DataFrame()
torrent_sir['분야']=coms
torrent_sir['파일명']=titles
torrent_sir['파일명2']=titles2
torrent_sir['세부링크']=links
torrent_sir['토렌트파일명']= tonames
torrent_sir['토렌트파일갯수']=tocnts
torrent_sir['조회수']= lu_cnts
torrent_sir['용량']=sizes
torrent_sir['등록일']=dates2
torrent_sir['마그넷링크']= maglinks

#엑셀 파일로 저장하기
#torrent_dia.to_excel(fx_name)
#print(" xls 파일 저장 경로: %s" %fx_name)

# csv 형태로 저장하기
torrent_sir.to_csv(fc_name,encoding="utf-8-sig")
print("csv 파일 저장 경로: %s" %fc_name)