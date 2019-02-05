import pandas as pd, os, time
from selenium import webdriver
import info
from bs4 import BeautifulSoup as BS

#import the registration numbers
dir = os.path.dirname(__file__)
path = dir + '\\00_All files_31913.csv'
df = pd.read_csv(path)
df['Registration No'] = df['Registration No'].astype(str).str.pad(6,'left','0')

#open the browser and go to the link
url = 'https://onlineservices.ocswssw.org/Thinclient/Public/PR/EN'
browser = webdriver.Chrome()
browser.get(url)
time.sleep(3)

def Extract_details():
    time.sleep(1)
    Count = info.get_count(BS(browser.page_source,'lxml'))
    if Count != 1:
        file = open(dir+'\\discripancies.txt','a')
        file.write(RegNo+':'+str(Count)+'\n')
        return file.close()
    #OpenPopUp
    browser.find_element_by_xpath('//tr[2]/td[2]/a[contains(@onclick,"TC_PublicRegister.OpenMember")]').click()
    time.sleep(1)
    df2=info.get_popupinfo(BS(browser.page_source,'lxml'))
    #ClosePopUp
    browser.find_element_by_xpath('/html/body/div[5]/div[1]/div/a[2]').click()
    return df2

Start=-1
df1 = pd.DataFrame([])
#Go to each "Registartion No" one by one
for RegNo in df['Registration No'].iloc[31875:]:#
    print(df[df['Registration No']==RegNo].index[0]+1,'\t',RegNo)
    if Start==-1:
        Start = df[df['Registration No']==RegNo].index[0]
    RegNoElement = browser.find_element_by_id('inputRegistrationNo')
    RegNoElement.send_keys(RegNo)
    browser.find_element_by_id('btnSearch').click()
    df2=Extract_details()
    df1=pd.concat([df1,df2],axis=0,sort=False)
    check = df[df['Registration No']==RegNo].index[0]
    if len(df1)%100==0 or check==31912:
        End = df[df['Registration No']==RegNo].index[0]
        df1.to_csv(dir+'\\{}_{}.csv'.format(Start+1,End+1),index=False)
        Start = -1
        df1.drop(df1.index, inplace=True)
    RegNoElement.clear()

browser.close()
