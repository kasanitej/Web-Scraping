from bs4 import BeautifulSoup as BS
import pandas as pd
from urllib.request import urlopen
from math import ceil
from threading import Thread
import queue, re, os

def assign(CorpName,AuthDate,ShareHolders,address,Num):
    if Num == 0:
        Num = 1
    Corpinfo={'Corporation Name-{}'.format(Num) : [CorpName],
    'Authorization-{}'.format(Num)  : [AuthDate],
    'ShareHolders-{}'.format(Num)  : [ShareHolders],
    'Address-{}'.format(Num)  : [address]
    }
    return Corpinfo

def Extract_Name_CPSO(Soup):
    Name_CPSO=Soup.find('h1').get_text().strip().split('\n')
    Name=Name_CPSO[0]
    CPSO=Name_CPSO[2][:-1].strip()
    return Name,CPSO

def Extract_Status_Class(Soup):
    info=Soup.find('div',{'class':'info'})
    info=info.find_all('p')
    for p in info:
        if 'Current Status:' in p.get_text():
            status = p.get_text()[17:].split('\n')
            status = [i.strip() for i in status]
            status = ' '.join(status)
        if 'CPSO Registration Class:' in p.get_text():
            Class = p.get_text()[26:].split('\n')
            Class = [i.strip() for i in Class]
            Class = ' '.join(Class)
    return status,Class

def Extract_Summary(Soup):
    Summary=Soup.find('section',{'data-jump-section':'Summary'})
    Data=Summary.find_all('p')
    for p in Data:
        if 'Former Name:' in p.get_text() or 'Former Names:' in p.get_text():
            Former_Name = p.get_text()[14:].split('\n')
            Former_Name = [i.strip() for i in Former_Name if i.strip()!='']
            Former_Name = '\n'.join(Former_Name)
        if 'Gender:' in p.get_text():
            Gender = p.get_text()[9:].split('\n')
            Gender = [i.strip() for i in Gender]
            Gender = Gender[0]
        if 'Languages Spoken:' in p.get_text():
            lang = p.get_text()[21:].split('\n')
            lang = [i.strip() for i in lang]
            lang = lang[0]
        if 'Education:' in p.get_text():
            Edu = p.get_text()[11:].split('\n')
            Edu = [i.strip() for i in Edu]
            Edu = Edu[0]
    return Former_Name,Gender,lang,Edu

def Exrtact_PracticeLocation(Soup):
    Data = Soup.find('div',{'class':'practice-location'})
    address=[];i=0;phone='';Fax='';Electoral=''
    for info in Data:
        if 'Primary Location of Practice' not in info and info.name!='br' and (info.name == 'strong' or len(info)!=1):
            if info.name == 'strong':
                if info.get_text()=='Phone:':
                    i=1
                if info.get_text()=='Fax:':
                    i=2
                if info.get_text()=='Electoral District:':
                    i=3
                continue
            if i==1:
                phone = info.strip()
            if i==2:
                Fax = info.strip()
            if i==3:
                Electoral = info.strip()
            if i==0:
                address.append(info.strip())
    address=','.join(address)
    return address,phone,Fax,Electoral

def Extract_AdditionalLoactions(Soup):
    Data=Soup.find_all('div',{'id':'p_lt_ctl04_pageplaceholder_p_lt_ctl01_CPSO_Doctor_AllDetail_collapseAdditionalAddress'})
    Add_address = [];addr = ''
    for Datainfo in Data:
        Datainfo = Datainfo.find('div',{'class':'practice-location'})
        for info in Datainfo:
            if info.name == 'strong':
                addr+=info.get_text().strip()
            elif info.name == 'hr':
                addr = addr[:-1]
                Add_address.append(addr)
                addr = ''
            elif info.name!='br' not in info and len(info.strip())!=0:
                addr+=info.strip()+","
        addr = addr[:-1]
        Add_address.append(addr)
    Add_address='\n'.join(Add_address)
    return Add_address

def Extract_CorpInfo(Soup):
    CorpName,AuthDate,addr,ShareHolders1,address1='','','','','';ShareHolders,Corpaddress=[],[];Corp=0;Corpinfo={}
    Data=Soup.find('div',{'id':'p_lt_ctl04_pageplaceholder_p_lt_ctl01_CPSO_Doctor_AllDetail_collapseCorporation','class':'collapse-container'})
    if Data:
        for info in Data:
            if info.name == 'strong' and info.get_text()=='Corporation Name:':
                if Corp==0:
                    i=1;Corp+=1
                else:
                    addr=addr[:-1];Corpaddress.append(addr)
                    address1 = '\n'.join(Corpaddress);ShareHolders1 = ''
                    for i in range(0,ceil(len(ShareHolders)/4)):
                        ShareHolders1 += ','.join(ShareHolders[4*i:4*(i+1)])+'\n'
                    ShareHolders1=ShareHolders1[:-1]
                    Corpinfo={**Corpinfo,**assign(CorpName,AuthDate,ShareHolders1,address1,Corp)}
                    Corp+=1;CorpName='';AuthDate='';ShareHolders=[];Corpaddress=[];addr='';i=1
                continue

            if 'Professional Corporation Information' not in info and (info.name == 'strong'or info.name == 'span' or len(info)!=1):
                if i==1:
                    CorpName = info.get_text()
                    i=0

                if info.name == 'p':
                    for p_info in info:
                        if p_info.name == 'strong':
                            if p_info.get_text()=='Certificate of Authorization Status:':
                                i=2
                            if p_info.get_text()=='Shareholders:':
                                i=3
                            if p_info.get_text()=='Business Address:':
                                i=4
                            continue

                        if i==2 and p_info.name!='br' and len(p_info.strip())!=0:
                            AuthDate = p_info.strip()
                        if i==3 and p_info.name!='br':
                            if p_info.name == 'a':
                                ShareHolders.append(ShareName+p_info.get_text().strip()+')')
                            else:
                                ShareName=p_info.strip()
                        if (i==10 or i==4) and p_info.name!='br':
                            if i == 10:
                                addr+=p_info.strip()+','
                            if i == 4:
                                if len(addr) != 0 and len(p_info.strip())!=0:
                                    addr=''
                                    addr+=p_info.strip()+','
                                    i=10
                                if len(p_info.strip())!=0:
                                    addr+=p_info.strip()+','
                                    i=10
                    if len(addr)!=0:
                        addr=addr[:-1]
                        Corpaddress.append(addr)
                        address1 = '\n'.join(Corpaddress)
                        ShareHolders1=''
                        for i in range(0,ceil(len(ShareHolders)/4)):
                            ShareHolders1 += ','.join(ShareHolders[4*i:4*(i+1)])+'\n'
                        ShareHolders1=ShareHolders1[:-1]

        Corpinfo={**Corpinfo,**assign(CorpName,AuthDate,ShareHolders1,address1,Corp)}
    else:
        Corpinfo = assign('','','','',1)
    return Corpinfo

def Extract_OtherJurisdictions(Soup):
    Data=Soup.find('div',{'class':'detail'})
    Other_Juris=''
    if Data:
        for datainfo in Data:
            if datainfo.name != 'p' and datainfo.name != 'br' and datainfo.strip() != '':
                Other_Juris+=datainfo.strip()+'\n'
    Other_Juris=Other_Juris.strip()
    return Other_Juris

def Extract_HospitalPri(Soup):
    Data=Soup.find('section',{'data-jump-section':'Hospital Privileges'})
    Loc=''
    if Data:
        TableRow = Data.find('tbody')
        if TableRow:
            TableRow = TableRow.find_all('tr')
            for row in TableRow:
                for idx,data in enumerate(row):
                    if idx == 1:
                        if len(Loc)!=0:
                            Loc=(Loc+'\n'+data.get_text()+':').strip()
                        else:
                            Loc=data.get_text().strip()+':'
                    if idx == 3:
                        Loc=(Loc+data.get_text()).strip()
    return Loc

def Extract_Specialties(Soup):
    Data=Soup.find('section',{'data-jump-section':'Specialties'})
    Specialties = ''
    if Data:
        TableRow = Data.find('table').find_all('tr')
        for row in TableRow[1:]:
            for idx,data in enumerate(row):
                if idx == 1:
                    if len(Specialties)!=0:
                        Specialties+='\n'+data.get_text().strip()+'||'
                    else:
                        Specialties+=data.get_text().strip()+'||'
                if idx == 3:
                    Specialties+=data.get_text().strip()+'||'
                if idx == 5:
                    Specialties+=data.get_text().strip()
    return Specialties

def Extract_RegHis(Soup):
    Data=Soup.find('section',{'data-jump-section':'Registration History'})
    Reg_His=''
    if Data:
        TableRow = Data.find('tbody').find_all('tr')
        for row in TableRow:
            for idx,data in enumerate(row):
                if idx == 1:
                    if len(Reg_His)!=0:
                        Reg_His+='\n'+data.get_text().strip()+'||'
                    else:
                        Reg_His=data.get_text().strip()+'||'
                if idx == 3:
                    Reg_His+=data.get_text().strip()
    return Reg_His

def Extract_PostGraduate(Soup):
    PEdu = ''
    PostEdu = Soup.find('section' , {'data-jump-section':'Postgraduate Training'})
    if PostEdu:
        postdetails = PostEdu.find_all('p')
        for post in postdetails:
            str = '|'.join([post1.strip() for post1 in post.text.split('\n') if post1.strip() and 'Please note:' not in post1.strip()])
            PEdu += str+'\n'
    return PEdu.strip()

def Extract_Restrictions(Soup,Section):
    Data=Soup.find('section',{'data-jump-section':Section})
    Restriction='No'
    if Data:
        Restriction='Yes'
    return Restriction

def Extract_DoctorDetails(url,q):
    Soup=BS(urlopen(url).read(),'lxml')

    Name,CPSO = Extract_Name_CPSO(Soup)
    status,Class = Extract_Status_Class(Soup)
    Former_Name,Gender,lang,Edu = Extract_Summary(Soup)
    address,phone,Fax,Electoral = Exrtact_PracticeLocation(Soup)
    Add_address = Extract_AdditionalLoactions(Soup)#Additional Practice Locations
    Corpinfo = Extract_CorpInfo(Soup)#Professional corporation Information
    Other_Juris = Extract_OtherJurisdictions(Soup)#Other Jurisdictions
    Loc = Extract_HospitalPri(Soup)#Hospital Privileges
    Specialties = Extract_Specialties(Soup)#Speciality
    PostGraduation = Extract_PostGraduate(Soup)
    Reg_His = Extract_RegHis(Soup)
    Restriction = Extract_Restrictions(Soup,'Practice Restrictions')
    Hearing1 = Extract_Restrictions(Soup,'Previous Hearings')
    Hearing2 = Extract_Restrictions(Soup,'Pending Hearings')
    Concern = Extract_Restrictions(Soup,'Concerns')

    Details = {'Name':['=HYPERLINK("{}","{}")'.format(url,Name)],
    'CPSO' :[CPSO],
    'Current Status':[status],
    'CPSO Registration Class':[Class],
    'Former Name':[Former_Name],
    'Gender':[Gender],
    'Languages Spoken':[lang],
    'Education':[Edu],
    'Address':[address],
    'Phone':[phone],
    'Fax':[Fax],
    'Electoral':[Electoral],
    'Additional Practice Location(s)': [Add_address],
    'Medical Licences in Other Jurisdictions':[Other_Juris],
    'Hospital Privileges':[Loc],
    'Speciality|issued Date|Type':[Specialties],
    'PostGraduation':[PostGraduation],
    'Action|Issue Date':[Reg_His],
    'R Yes/No':[Restriction],
    'H1 Yes/No':[Hearing1],
    'H2 Yes/No':[Hearing2],
    'C Yes/No':[Concern],
    **Corpinfo}
    q.put(pd.DataFrame.from_dict(Details))
    print(Name)

#Multithreading
q= queue.Queue()
df = pd.read_csv(os.path.dirname(__file__)+r'\finalUrllist.csv')
urllist = df['url'].tolist()
th = []
for url in urllist[:]:
    t = Thread(target=Extract_DoctorDetails,args=(url,q,))
    t.start()
    th.append(t)

for thr in th:
    thr.join()

Doc=pd.DataFrame()
while not q.empty():
    Doc=pd.concat([Doc,q.get()],sort=False)

Doc.sort_values(by=['Name'], ascending=True, inplace=True)
Doc.to_excel(os.path.dirname(__file__) + '\CPSODocList.xlsx',index=False)
