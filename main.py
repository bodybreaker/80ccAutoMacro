import requests as r
from bs4 import BeautifulSoup as bs
import time
import os


USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
LOGIN_URL = "http://www.palgong-cc.co.kr/mobile/login_ok.asp"
DAY_LIST_URL = "http://palgong-cc.co.kr/mobile/reserve.asp"
TIME_LIST_URL ="http://www.palgong-cc.co.kr/mobile/reserve_step1.asp"
RESERVE_URL = "http://www.palgong-cc.co.kr/mobile/reserve_step2_ok.asp"

ID = ""
PW = ""

HOPE_DATE = []
HOPE_TIME = []


file = open('setting.txt', mode='rt', encoding='utf-8')

for index,line in enumerate(file):
    line = line.replace("\n","",999)
    line = line.replace(" ","",999)
    if index == 0:
        ID = line
    if index ==1:
        PW = line
    if index == 2:
        HOPE_DATE = line.split(',')
    if index == 3:
        HOPE_TIME = line.split(',')

cookies = {}
res = r.post(LOGIN_URL,data={'memb_inet_no':ID,'memb_inet_pass':PW},headers={
    'user-agent':USER_AGENT
})

cookies = res.cookies

while True:
    print("희망일자 >> ",HOPE_DATE)
    print("희망시간 >> ",HOPE_TIME)
    res = r.post(DAY_LIST_URL,headers={
        'user-agent':USER_AGENT,
        'referer':'http://www.palgong-cc.co.kr/mobile/',
        'host':'www.palgong-cc.co.kr'
        },cookies=cookies)

    res.raise_for_status()
    res.encoding='UTF-8'

    doc = res.text
    soup = bs(doc,'html.parser')

    reserveListData = soup.select("a[title='예약가능']")

    availDateTimeList = []
    availDatesList = []
    for reserve in reserveListData:
        date = reserve.attrs['onclick'].replace('Date_Click(','').replace(');','').split(',')
        dateStr = ""
        for d in date:
            dateStr+=d.replace("'","").replace("'","")
        availDatesList.append(dateStr)
        #availDatesList.append(str(int(''.join(filter(str.isdigit,reserve.text)))))

    # 예약가능 시간 조회
    for date in availDatesList:
        res = r.post(TIME_LIST_URL,data={'book_date':date},headers={
            'user-agent':USER_AGENT,
            'referer':'http://www.palgong-cc.co.kr/mobile/',
            'host':'www.palgong-cc.co.kr'
            },cookies=cookies)
        res.raise_for_status()
        res.encoding='UTF-8'
        doc = res.text
        soup = bs(doc,'html.parser')

        availTimeList = soup.select("tbody tr td a")
        print("가능일자 >>",date)
        timeList = []
        for t in availTimeList:
            obj = {}
            tStr = t.attrs['href'].replace("JavaScript:Book_Confirm(","").replace(");","").split(",")
            
            obj['date']=date;
            if tStr[1] =="'1'":
                obj['course'] = 'OutCourse'
            elif tStr[1]=="'2'":
                obj['course'] = "InCourse"
            obj['time'] = tStr[2].replace("'","").replace("'","")
            availDateTimeList.append(obj)
            timeList.append(obj['time'])
        print("\t시간 >> ",timeList)
    print("-------------------------------------------------------------------------------")
    #availDateTimeList 에 모든 가능일자 담김
    #print(availDateTimeList)


    for el in availDateTimeList:
        for hd in HOPE_DATE:
            if el['date'] == hd:
                # 날짜 일치할때
                for ht in HOPE_TIME:
                    if el['time'][0:2] == ht:
                        # 시간도 일치할 때 예약 진행
                        courseType = '1'
                        if el['course'] == 'OutCourse':
                            courseType = '1'
                        elif el['course'] == 'InCourse':
                            courseType = '2'
                        res = r.post(RESERVE_URL,data={'book_date':hd,'book_crs':courseType,'book_time':el['time']},headers={
                            'user-agent':USER_AGENT,
                            'referer':'http://www.palgong-cc.co.kr/mobile/',
                            'host':'www.palgong-cc.co.kr'
                            },cookies=cookies)
                        res.raise_for_status()
                        res.encoding='UTF-8'
                        print("=======================예약 완료=======================")     
                        os.system("pause")    
                        os.exit()               
    time.sleep(0.3)

#print(soup.prettify())
#pyinstaller --onefile main.py