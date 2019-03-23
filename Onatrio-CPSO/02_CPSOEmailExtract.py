from bs4 import BeautifulSoup as BS
import re, requests, os, json, queue
from urllib.parse import unquote
from threading import Thread
import pandas as pd

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
    Soup=BS(sess.get(url).text,"lxml")

    HF,Token,StateG,View=Extract(Soup)

    form={'manScript_HiddenField':HF,
    '__CMSCsrfToken':Token,
    '__EVENTTARGET':'',
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    'lng':'en-CA',
    '__VIEWSTATEGENERATOR':StateG,
    'p$lt$ctl01$SearchBox$txtWord_exWatermark_ClientState':'',
    'p$lt$ctl01$SearchBox$txtWord':'',
    'searchType':'general',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$advancedState':'open',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ConcernsState':'closed',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$txtCPSONumber':'',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$txtLastNameQuick':'',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddCity':'',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$txtPostalCode':'',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$txtLastName':item+'%',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$grpGender':'',
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
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$txtExtraInfo':'',
    'p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$btnSubmit1':'Submit',
    '__VIEWSTATE':View}

    Next=0;Find=1;count=0
    while(True):
        Soup=BS(sess.post(url, data=form).text,"lxml")
        CountSearchArea=Soup.find('div',{'class':"row doctor-search-count"})
        if CountSearchArea:
            if Find == 1:#This will give you the count
                St=CountSearchArea.find('strong').get_text()
                count=int(re.match(r'.* (\d*) .*',St).group(1))
                Find=0
                #print(item,'\t',count)

            #Display the links in the page
            DoctorSearchArea=Soup.find('div',{'class':'doctor-search-results'})
            Doctors=DoctorSearchArea.find_all('a')
            for Doctor in Doctors:
                # print(Doctor.get_text(),'$',Doctor['href'])
                q.put([Doctor.get_text(),Doctor['href']])

            #Crawling & Gathering Weblinks
            SearchPageArea=Soup.find('div',{'class':'large-8 columns'})
            PageNumbers=SearchPageArea.find_all('a')
            for pagenum in PageNumbers:
                if pagenum.has_attr('class') and pagenum['class'] == ['active'] or Next == 2 :
                    if Next==0 and int(pagenum.get_text())%5 == 0:#if more than 5 pages the next button is "Next 5"
                        Next=2
                        continue
                    Next=1
                    continue
                #This block is to get the page url
                if Next == 1 and pagenum.has_attr('href') :
                    ET=re.match(r'javascript:__doPostBack\(\'(.*)\',\'\'\)',pagenum['href']).group(1)
                    HF,Token,StateG,View=Extract(Soup)
                    form={'manScript_HiddenField':HF,
                    '__CMSCsrfToken':Token,
                    '__EVENTTARGET':ET,
                    '__EVENTARGUMENT':'',
                    'lng':'en-CA',
                    '__VIEWSTATEGENERATOR': StateG,
                    'p$lt$ctl01$SearchBox$txtWord_exWatermark_ClientState':'',
                    'p$lt$ctl01$SearchBox$txtWord':'',
                    '__VIEWSTATE':View}
                    Next=0
                    url=r'https://www.cpso.on.ca/Public-Register-Info-(1)/Doctor-Search-Results'

        if Next in [1,2] or count<=10:
            break

path = os.path.dirname(__file__)+'\LangDict.json'
obj_text = open(path, 'r').read()
LangList = json.loads(obj_text)
q = queue.Queue()

for Lang,SearchCriteria in LangList.items():
    th = []
    for item in SearchCriteria:
            t = Thread(target=ExtractDetails,args=(Lang,item + '%',))
            t.start()
            th.append(t)
    for thr in th:
        thr.join()

urllist = pd.DataFrame(columns=['Name','url'])
while not q.empty():
    urllist.loc[urllist.shape[0]] = q.get()

urllist.drop_duplicates(keep='first',inplace=True)
urllist.sort_values(by=['Name'], ascending=True, inplace=True)
urllist.to_csv(os.path.dirname(__file__)+'\\urllist.csv', index = False)
