from bs4 import BeautifulSoup as BS
import pandas as pd

def member_summary(Soup):
    data = {'Name' : [],'Registration No' : [],'Previous Name' : [],'Business Name' : [],
    'Business Address' : [],'Business Phone' : [],'Class of Certificate of Registration': []}

    table = Soup.find('table')
    if table:
        tb_rows = table.find_all('tr')
        for row in tb_rows:
            td = row.find_all('td')
            row = [tr.text.strip() for tr in td]
            if row[0] != '':
                colname = row[0]
                data[colname]+=[','.join(row[1:])]
            else:
                data[colname]+=[','.join(row[1:])]

    for key,value in data.items():
        data[key]=[','.join(value)]
    return data

def section(Soup):
    data = {}
    table = Soup.find('table')
    if table:
        trs = table.find_all('tr')
        for tr in trs:
            ths = tr.find_all('th')
            if ths:
                th_key = []
            for th in ths:
                th_key.append(th.text)
            tds = tr.find_all('td')
            for idx,td in enumerate(tds):
                if th_key[idx] in data.keys():
                    data[th_key[idx]]=data[th_key[idx]]+'\n\n'+td.text.replace('\n','')
                else:
                    data[th_key[idx]]=td.text.replace('\n','')
    return data

def prof_corporation(Soup):
    data = {}
    Soup=Soup.find('div',{'class':'panel-body'})
    print(Soup.text.strip())
    # return data

def get_count(Soup):
    result_block = Soup.find('div',{'id':'divResult'}).find_all('a',{'href':'#'})
    return len(result_block)

def get_popupinfo(Soup):
    sec = Soup.find_all('div',{'class':'panel panel-primary'})
    # section 2 & 3 has same format
    Terms=section(sec[1])
    for key in Terms.keys():
        Terms[key+'-1']=Terms.pop(key)
    df = pd.DataFrame({**member_summary(sec[0]),**Terms,**section(sec[2])})
    return df
    # prof_corporation(sec[3])#Prof_corpincomplete and not required as it has repeated info as member summary
