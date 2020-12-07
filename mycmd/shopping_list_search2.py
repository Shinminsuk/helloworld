# 옥션, 지마켓, 쿠팡, 위메프 에서 검색리스트를 추출 
# 위메프는 안된다.  고로 전체할 때 3번 위메프는 빼야 한다. 

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import re
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse, parse_qs
import xlwt   # pip install xlwt 실행 후 수행

# 지마켓, gmarket, 'https://browse.gmarket.co.kr/search?'
# 옥션, auction, 'https://browse.gmarket.co.kr/search?'
# 쿠팡, coupang, 'https://www.coupang.com/np/search?'
# 위메프, wmprice, 'https://search.wemakeprice.com/search?'

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
    
########### 값 입력 ##############
shop = [ 'gmarket','auction', 'coupang','wemakeprice']
for i, k in enumerate(shop) : 
    print (i, ":" , k , end=' ||| ')
shopnum = input('어느 사이트를 검색할까요?(숫자) : ')
query = input("여기 입력할 값이 검색어 : ")
   
# 사전 셋팅 쿼리값
g_params = {'keyword': query, 's': '8', 't': 'a'} # 판매인기순
a_params = {'keyword': query, 'encKeyword': query, 'Fwk': query, 'frm': 'hometab', 'dom': 'auction', 'isSuggestion': 'No', 
            'acode': 'SRP_SU_0100',  's': '8'}
c_params = {'q': query, 'isPriceRange': 'false', 'page': '1', 'filterSetByUser': 'true',
            'channel': 'user', 'rating': '0', 'sorter': 'saleCountDesc', 'listSize': '36'}
w_params = {'keyword': query, 'search_cate': 'top', 'isRec': '1', '_service': '5', '_type': '3'}

# 키 확인
key_dic = {'soup' : '최초시작', 'title' : '물품명' , 'brand' : '브랜드', 'link' : '링크', 'photo' : ' 포토' , 'price' : '가격', 'oprice' : '최초가격',
           'rev_cnt' : ' 조회수', ' review' : '상품평수' , 'sale_cnt' : '판매량', 'relkey' : '연관검색어' }

# soup 값은 리스트로 떨어질 수 있는 값을 기

g_search = { 'soup' : 'div.box__component',
            'title' : 'span.text__item-title a span.text__item' , 
            'brand' : 'span.text__item-title a span.text__brand', 
            'link' : 'span.text__item-title a' , # 링크는 href 
            'photo' : 'div.box__image img' , # 이미지는 src
            'price' : 'div.box__item-price div.box__price-seller strong' ,
            'oprice' : 'div.box__item-price div.box__price-original span.text', 
            'rev_cnt' : '', 
            'review' : 'ul.list__score li.list-item__feedback-count span.text', 
            'sale_cnt' : 'ul.list__score li.list-item__pay-count span.text',
            'relkey' : 'ul.list__keywords'
           }

a_search = { 'soup' : 'div.component--item_card',
            'title' : 'span.text--itemcard_title a span.text--title' , 
            'brand' : 'span.text--itemcard_title a span.text--brand', 
            'link' : 'span.text--itemcard_title a', 
            'photo' : 'div.section--itemcard_img a img' , 
            'price' : 'div.area--itemcard_price span.price_seller strong.text--price_seller' ,
            'oprice' : 'div.area--itemcard_price span.price_original strong.text--price_original', 
            'rev_cnt' : '', 
            'review' : 'ul.list--score li.reviewcnt span.text--reviewcnt' , 
            'sale_cnt' : 'ul.list--score li.buycnt span.text--buycnt' ,
            'relkey' : 'div.section--relative_keywords ul.list--relative_keywords'
           }

c_search = { 'soup' : 'ul#productList li.search-product',
            'title' : 'div.name' , 
            'brand' : '', 
            'link' : 'a', 
            'photo' : 'a dt.image' , 
            'price' : 'div.price-area strong.price-value' ,
            'oprice' : 'div.price-area div.price .base-price', 
            'rev_cnt' : '', 
            'review' : 'div.other-info span.rating-total-count', 
            'sale_cnt' : '',
            'relkey' : 'dl.search-related-keyword dd'
           }
w_search = { 'soup' : 'div.list_conts_wrap',
            'title' : 'a div.list_info div.info_btnarea p.info_text' , 
            'brand' : '', 
            'link' : 'a', 
            'photo' : 'a div.list_thum img' , 
            'price' : 'a div.list_info div.list_price div.price_info em.num' ,
            'oprice' : 'a div.list_info div.list_price div.price_sale span.num', 
            'rev_cnt' : '', 
            'review' : 'a div.list_info div.info_noti span.num', 
            'sale_cnt' :'a div.list_info div.list_price span.purchase span.num',
            'relkey' : 'div.relation_word div.word_list'
           }

shoplist = [ ['gmarket', 'https://browse.gmarket.co.kr/search?', g_params, g_search], 
          ['auction', 'http://browse.auction.co.kr/search?', a_params, a_search], 
          ['coupang', 'https://www.coupang.com/np/search?', c_params, c_search], 
          ['wmprice', 'https://search.wemakeprice.com/search?', w_params, w_search], 
        ]

print('%s사이트에서 "%s"를 검색합니다. ' % (shoplist[int(shopnum)][0], query)  )

#파일명을 생성하기 위한 셋팅 
now = time.localtime()
s = '%03d-%02d-%02d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
fdir = 'c:\\doit\\data\\'
#os.chdir(fdir)
fx_name = fdir+s+query+'.xls'
fc_name = fdir+s+query+'.csv'

#판다스 정리를 위한 리스트 생성 
shopnames = [] # 쇼핑몰
nums = [] # 번호
titles = [] # 제목 
links = [] # 링크 
oprices = [] #최초가격
prices = [] # 가격
reviews = [] # 상품평수
sales = [] # 판매량
dates = []# 날짜
relkeys = [] #연관 검색어

no = 1 # 저장 갯수 설정을 위한 넘버링

########### 실제 스크래핑 시작 #######################

# 헤더, 파라미터 입력값으로 사전 셋팅
## 여기를 for 문으로 돌려서 4개 사이트 한꺼번에 ? 
## shoplist 리스트를 가준으로 
url = shoplist[int(shopnum)][1]
params = shoplist[int(shopnum)][2]
key_dic = shoplist[int(shopnum)][3]
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
shopname = shoplist[int(shopnum)][0]

# 스크래핑 시작 
html = requests.get(url, headers=headers, params=params)
soup = BeautifulSoup(html.text, 'html.parser')
contents = soup.select(key_dic['soup'])

for tr in contents :
    title = find_elem(tr, key_dic['title'], 'text')  # 파일명
    if title is None : 
        continue
    link = find_elem(tr, key_dic['link'], 'link') # 세부링크
    oprice = find_elem(tr, key_dic['oprice'], 'text') # 원가격
    if oprice is None :
        oprice = 0
    price = find_elem(tr, key_dic['price'], 'text') # 가격
    review = find_elem(tr, key_dic['review'], 'text') # 리뷰수
    try : 
        review = review.replace(",","")
        p = re.compile('[0-9]+')
        review = p.search(review)
        if review : 
            review = review.group()
        else :
            review = '없어'
    except :
        pass
    # 판매량 확인
    sale_cnt = find_elem(tr, key_dic['sale_cnt'], 'text') # 판매량
    try : 
        sale_cnt = sale_cnt.replace(",","")
        p = re.compile('[0-9]+')
        sale_cnt = p.search(sale_cnt)
        if sale_cnt :
            sale_cnt = sale_cnt.group()
            sale_cnt = int(sale_cnt)
        else :
            sale_cnt = 0 
    except : 
        pass
#     if int(sale_cnt) < 100 :
#         continue
    relkey = find_elem(tr, key_dic['relkey'], 'text') # 연관검색어
    
    #판다스 입력을 위한 어팬드
    shopnames.append(shopname)
    titles.append(title)
    links.append(link)
    oprices.append(oprice)
    prices.append(price)
    reviews.append(review)
    sales.append(sale_cnt)
    relkeys.append(relkey)
    dates.append(s)
    print( no, '번째 파일 저장', "="*20)
    print( title, ' : ', price)
    no += 1

# 리스트를 판다스로 저장하기
shopinglist = pd.DataFrame()
shopinglist['쇼핑몰']=shopnames
shopinglist['제목']=titles
shopinglist['세부링크']=links
shopinglist['최초가격']= oprices
shopinglist['가격']=prices
shopinglist['상품평수']=reviews
shopinglist['판매량']= sales
shopinglist['연관검색어']= relkeys
shopinglist['검색일자']= dates

#엑셀 파일로 저장하기
#torrent_dia.to_excel(fx_name)
#print(" xls 파일 저장 경로: %s" %fx_name)

# csv 형태로 저장하기
shopinglist.to_csv(fc_name,encoding="utf-8-sig")
print("csv 파일 저장 경로: %s" %fc_name)