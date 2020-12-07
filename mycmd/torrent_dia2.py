# 기존 파일에서 try를 if 문으로 설정한 내용
# 다이아토렌트에서 분야별, 기간별 인기순위를 100건 가져오는 모듈

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse
import xlwt   # pip install xlwt 실행 후 수행

def get_download(url,fname): # 기존 함수에서 디렉토리를 뻈음.
    try:
        print(url)
        urlretrieve(url,fname)
        time.sleep(5)  # 다운로드 시간을 좀 준다 10초
        print('다운로드 완료')
    except:
        return None

# 입력값을 받기 위한 설정
print(' 0 : 전체, 1 : 1일, 2 : 3일, 3 : 7일, 4 : 1개월, 5 : 3개월\n')
scainput = input('기간의 번호를 선택하세요(번호만) : ')
print(''' 
            0 전체
            1 한국영화: torrent_movieko
            2 해외영화: torrent_movieov
            3 드라마 : torrent_drama
            4 완결모음: torrent_tvend
            5 음악: torrent_music
            6 해외방송: torrent_ftv
            7 키즈방송: torrent_kids''')
boinput = input('위 번호 중 분야를 선택하세요(번호만) : ')

# sca = [ '전체', '1일', '3일', '7일', '1개월', '3개월']
# bo_table = [ '', 'torrent_movieko','torrent_movieov', 'torrent_drama',
#         'torrent_tvend', 'torrent_music', 'torrent_ftv', 'torrent_kids')
sca = ['','1일', '3일', '7일', '1개월', '3개월'] # 기간 선택
bo_table = [ '', 'torrent_movieko','torrent_movieov', 'torrent_drama' , 'torrent_tvend'
           'torrent_music', 'torrent_ftv', 'torrent_kids']  #분야 선택

#파일명에 검색일자시간을 넣기위한 내용
now = time.localtime()
s = '%03d-%02d-%02d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)

#저장경로 폴더 지정
fdir = 'c:\\doit\\data\\'
os.chdir(fdir)

#파일명 사전 셋팅
fx_name = fdir+'torrent_dia_'+s+sca[int(scainput)]+bo_table[int(boinput)]+'.xls'
fc_name = fdir+'torrent_dia_'+s+sca[int(scainput)]+bo_table[int(boinput)]+'.csv'

#헤더, 파라미터 사전 셋팅을 위한 설정
url = 'https://www.torrentdia.com/bbs/ranking.php'
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
params = {'sca' : sca[int(scainput)], 'bo_table' : bo_table[int(boinput)]}

#판다스 정리를 위한 리스트 생성
titles = [] # titles 제목 : td.list-subject -> a  (텍스트)
links = [] # links 링크 : td.list-subject -> a['href']
sizes = [] # sizes 용량 : td."td_size600 td_ranking_size text-center"
dates = []# dates 등록일 : td."td_date td_ranking_date text-center en"
titles2 = [] # titles2 제목 :  span id = 'TITLE_google'
explains  = [] # explain 설명 : p class = 'desc'
downlinks = [] # downlink 다운로드 링크 : span class = 'right-side-actions' -> a
magnetlinks = [] # magnetlink u마그넷 주소 : div class = 'right-side-actions' -> a (btn btn-color btn-xs
no = 1 # 저장 갯수 설정을 위한 넘버링

# 실제 스크래핑 시작
html = requests.get(url, headers=headers, params=params)
soup = BeautifulSoup(html.text, 'html.parser')
#contents = soup.find('table',class_='div-table').find('tbody').find_all('tr')
contents = soup.select('table.div-table tbody tr')

print(len(contents), '개의 리스트가 있습니다. ')

for tr in contents[:10] :
#    try :
    title = tr.select_one('td.list-subject a').text  # 파일명
    link = tr.select_one('td.list-subject a')['href'] # 세부링크
    size = tr.select_one('td.td_ranking_size').text.strip() # 파일용량
    date = tr.select_one('td.td_date').text # 등록일
    shtml = requests.get(link, headers=headers)
    soup = BeautifulSoup(shtml.text, 'html.parser')
#    title2 = soup.select_one('span#TITLE_google') #제목
#    if title2 :
#       title2 = title2.text
#    else :
#        title2 = '제목 없음'
#    explain = soup.select_one('p.desc') #설명
#    if explain :
#        explain = explain.text
#    else :
#        explain = '설명 없음'
    downlink = soup.select_one('span.right-side-actions a')
    if downlink :
        downtext = downlink.text
        downlink= downlink['href']
        get_download(downlink, fdir+downtext)
    else :
        downlink= '링크에러?'
#   magnetlink = soup.select_one('div.right-side-actions a')
    titles.append(title)
    links.append(link)
    sizes.append(size)
    dates.append(date)
#    titles2.append(title2)
#    explains.append(explain)
    downlinks.append(downlink)
    print( no, '번째 파일 저장')
    no += 1
#    except :
#        no += 1
#        print(no)

# 리스트를 판다스로 저장하기
torrent_dia = pd.DataFrame()
torrent_dia['파일명']=titles
torrent_dia['세부링크']=links
torrent_dia['용량']=sizes
torrent_dia['등록일']=dates
#torrent_dia['제목']=titles2
#torrent_dia['설명']=explains
#torrent_dia['다운링크']=downlinks

#엑셀 파일로 저장하기
#torrent_dia.to_excel(fx_name)
#print(" xls 파일 저장 경로: %s" %fx_name)

# csv 형태로 저장하기
torrent_dia.to_csv(fc_name,encoding="utf-8-sig")
print("csv 파일 저장 경로: %s" %fc_name)