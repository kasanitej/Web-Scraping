from bs4 import BeautifulSoup as BS
import re, requests, queue, math, os, json
from urllib.parse import unquote
from threading import Thread
import pandas as pd
from urllib.request import urlopen

SearchDict={}
def Extract(Soup):
    ##manScript_HiddenField:
    HidF=Soup.find_all('script',{'src':re.compile('.*_TSM_CombinedScripts_=(.*)')})
    for src in HidF:
        HF=unquote(src['src'])[92:]

    Tkn=Soup.find_all('input',{'type':'hidden'})
    for input in Tkn:
        if 'Csrf' in input['name']:
            Token=input['value']##__CMSCsrfToken:
        if '__VIEWSTATEGENERATOR'==input['name']:
            StateG=input['value']##__VIEWSTATEGENERATOR
        if '__VIEWSTATE'==input['name']:
            View=input['value']##__VIEWSTATE
    return [HF,Token,StateG,View]


def ExtractDetails(Lang,item):
    sess=requests.session()
    url="https://www.cpso.on.ca/Public-Information-Services/Find-a-Doctor?search=general"
    try:
        html = sess.get(url)
    except:
        print('Initial Connection {} not established'.format(Lang))
        return Conn.put([[Lang],[item]])

    Soup=BS(html.text,"lxml")

    HF,Token,StateG,View=Extract(Soup)

    form={'manScript_HiddenField':HF,
    '__CMSCsrfToken':Token,
    'lng':'en-CA',
    '__VIEWSTATEGENERATOR':StateG,
    'searchType':'general',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$advancedState':'open',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ConcernsState':'closed',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$txtLastName':item,
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$grpDocType':'rdoDocTypeSpecialist',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddSpecialist':'278', ##119 psychiatry;278 child & Adolescent
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddHospitalName':'-1',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddLanguage':Lang,
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkActiveDoctors':'on',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkPracticeRestrictions':'on',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkPendingHearings':'on',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkPastHearings':'on',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkHospitalNotices':'on',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkConcerns':'on',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkNotices':'on',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$btnSubmit1':'Submit',
    '__VIEWSTATE':View}

    try:
        html = sess.post(url, data=form)
    except:
        print('Post for {} not established'.format(Lang))
        return Conn.put([[Lang],[item]])

    Soup=BS(html.text,"lxml")
    CountSearchArea=Soup.find('div',{'class':"row doctor-search-count"})
    count=0
    if CountSearchArea:
        St=CountSearchArea.find('strong').get_text()
        count=int(re.match(r'.* (\d*) .*',St).group(1))
        print(Lang,item,count)
        q.put([Lang,item,count])
        #l.put([Lang])



url="https://www.cpso.on.ca/Public-Information-Services/Find-a-Doctor?search=general"
Soup = BS(urlopen(url).read(),'lxml')
Lang = Soup.find('select' , {'name':'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddLanguage'}).find_all('option')
LangDict = {}
for L in Lang:
    LangDict[L['value']] = L.text

LangList = list(LangDict.keys())

q = queue.Queue()
l = queue.Queue()
Conn = queue.Queue()
th = []

##################### To get which Language has Doctors ###########################
#### This will save some time when we check every alphabet for every Language ####

while(len(LangList)!=0):
    for Lang in LangList:
        t = Thread(target=ExtractDetails,args=(Lang,'%',))
        t.start()
        th.append(t)
    for thr in th:
        thr.join()
    LangList = []
    while not Conn.empty():
        LangList += Conn.get()[0]

LangList,UniqList = [],[]
while not q.empty():
    temp = q.get()
    LangList += [temp[0]]
    UniqList += [temp[2]]

LangIndex = LangList
print('xxxxxxxxxxxxxxxxxxxxxxxx Collection Done xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
############################# End #############################################

Alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
SearchCriteria=[Alphabet] * len(LangList)
LostConn = dict(zip(LangList,SearchCriteria))
th = []
while(len(LostConn)!=0):
    for Lang , alphabets in LostConn.items():
        for item in alphabets:
            t = Thread(target=ExtractDetails,args=(Lang,item + '%',))
            t.start()
            th.append(t)
        for thr in th:
            thr.join()
    LostConn = {}
    while not Conn.empty():
        temp = Conn.get()
        if temp[0][0] in LostConn.keys():
            LostConn[temp[0][0]] +=  temp[1][0]
        else:
            LostConn[temp[0][0]] = temp[1][0]

DocTable = pd.DataFrame([],columns=list(Alphabet),index=LangIndex)

FinalDict = {}
while not q.empty():
    data = q.get()

    if data[0] in FinalDict.keys():
        FinalDict[data[0]] =  ''.join(sorted(FinalDict[data[0]] + data[1][0]))
    else:
        FinalDict[data[0]] =  data[1][0]

    DocTable.loc[data[0],data[1][0]]=data[2]

DocTable['Total'] = DocTable.sum(axis=1).astype(int)
DocTable['Unique']= UniqList

DocTable.to_csv(os.path.dirname(__file__)+'\LangStatistics.csv')
path = os.path.dirname(__file__)+'\LangDict.json'
json.dump(FinalDict,open(path, 'w'))
