from selenium import webdriver
from bs4 import BeautifulSoup as BS
import time, info, os, pandas as pd


url = 'https://onlineservices.ocswssw.org/Thinclient/Public/PR/EN'
browser = webdriver.Chrome()
browser.get(url)
time.sleep(3)


search = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
comb = [letter+letter1 for letter in search for letter1 in search]#676 items
search_type = ['inputFirstname','inputLastname']

def getalldetailsfrompage(Count):
    data = {'Name' : [],'Registration No' : [],'Previous Name' : [],'Business Name' : [],
    'Business Address' : [],'Business Phone' : [],'Class of Certificate of Registration': []}
    for i in range(2,Count+2):#starts with 2
        #OpenPopUp
        browser.find_element_by_xpath('//tr[{}]/td[2]/a[contains(@onclick,"TC_PublicRegister.OpenMember")]'.format(i)).click()
        time.sleep(1)
        SWData = info.get_popupinfo(BS(browser.page_source,'lxml'))
        for key in data:
            data[key].append(SWData[key][0])
        #ClosePopUp
        browser.find_element_by_xpath('/html/body/div[5]/div[1]/div/a[2]').click()
    return pd.DataFrame(data)

def last_name(path,escape):
    comb2 = [letter for letter in search]
    if escape == 1:
        comb2 = comb2[4:]
    for letter in comb2:
        LastNameElement = browser.find_element_by_id('inputLastname')
        LastNameElement.send_keys(letter)
        browser.find_element_by_id('btnSearch').click()

        time.sleep(1)

        Count = info.get_count(BS(browser.page_source,'lxml'))
        print('$'*len(letter.replace(' ',''))+letter,':',Count)

        df = getalldetailsfrompage(Count)
        df.to_csv(path +'\\'+letter+'_'+str(Count)+'.csv',index=False)

        if Count == 100:
            ind = comb2.index(letter)
            for New_letter in search:
                comb2.insert(ind+1,letter+New_letter);ind+=1
            for New_letter in search:
                comb2.insert(ind+1,letter+' '+New_letter);ind+=1

        LastNameElement.clear()

escape=1
for letter in comb[24*26:25*26]:
    path = os.path.dirname(__file__) +'\\'+letter
    if not os.path.exists(path):
        os.makedirs(path)

    FirstNameElement = browser.find_element_by_id('inputFirstname')
    FirstNameElement.send_keys(letter)
    if escape == 0:
        browser.find_element_by_id('btnSearch').click()

        time.sleep(2)

        Count = info.get_count(BS(browser.page_source,'lxml'))
        print(letter,':',Count)

        df = getalldetailsfrompage(Count)
        df.to_csv(path +'\\'+'01_'+letter+'_'+str(Count)+'.csv',index=False)
    else:
        Count = 100
    if Count == 100:
        last_name(path,escape)
        escape=0
    FirstNameElement.clear()

browser.close()
