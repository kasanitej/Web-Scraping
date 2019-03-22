from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import os, bs4, pandas as pd
from threading import Thread
import queue


url = "https://www.albertahealthservices.ca/findhealth/results.aspx?type=service&id=25&locationCity=Calgary&radius=all#contentStart"
folder = os.path.dirname(url)

def GetSoup(url):
    html = urlopen(url).read()
    return BS(html, "lxml")

#########Gathering urls###################
Soup = GetSoup(url)
a_tags = Soup.find_all('a',{'class':'gridTitle'})
urls = [folder + '/' + a_tag['href'].replace('#contentStart','') for a_tag in a_tags]
urls = list(set(urls))
path = os.path.dirname(__file__)
df = pd.DataFrame(urls, columns=['Alberta URLs'])
df.to_csv(path+'\\Alberta links.csv',index=False)
###########################################

def data_insert(data,key,value):
    if key in data.keys():
        data[key] += '\n'+value
    else:
        data[key] = value
    return data

def details(url):
    Soup = GetSoup(url)
    data = {}
    detailsblock = Soup.find('div',{'id':'facility_details'})
    if detailsblock:
        for detail in detailsblock:
            if isinstance(detail,bs4.element.NavigableString):
                if detail.strip()!='':
                  data = data_insert(data,'services',detail.strip())
            elif detail.has_attr('id') and (detail['id'] in ['mobileContainer','MainPlaceHolder_detailsMap']):
                continue
            elif detail.has_attr('id') and detail['id'] == 'detailsAccordion':
                for indv_detail in detail.find_all('details',{'class':'acc-group'}):
                    col_name = indv_detail.find('summary').get_text().strip()
                    value = indv_detail.get_text().replace(col_name,'').strip()
                    data[col_name] = value
            elif detail.has_attr('id') and detail['id']=='MainPlaceHolder_facilityOfficialNameContainer':
                location = detail.find('a').get_text()
                data = data_insert(data,'location',location)
            elif detail.has_attr('class') and detail['class'] == ['hcl_title']:
                provider = detail.find('span').get_text()
                data = data_insert(data,'provider',provider)
            else:
                data = data_insert(data,'services',detail.get_text())
    if 'provider' in data.keys():
        data['provider']= f'=HYPERLINK("{url}","{provider}")'
    else:
        return a.put(url)

    return q.put(data)

iter = 0
files = [];n_thr = 100
a= queue.Queue()
while True:
    for i in range(int(len(urls)/n_thr)+1):
        q= queue.Queue()
        th = []
        for url in urls[i*n_thr:(i+1)*n_thr]:
            t = Thread(target=details,args=(url,))
            t.start()
            th.append(t)
        for thr in th:
            thr.join()
        df = pd.DataFrame([])
        while not q.empty():
            df1 = pd.DataFrame([q.get()])
            df = pd.concat([df,df1])
        if df.shape[0] != 0:
            name = str(iter*n_thr)+'_'+str((iter+1)*n_thr)+'.csv'
            files.append(name)
            df.to_csv(str(iter*n_thr)+'_'+str((iter+1)*n_thr)+'.csv',index=False)
            print((iter+1)*n_thr, 'done')
            iter += 1
    if a.empty():
        break
    else:
        urls = []
        while not a.empty():
            urls.append(a.get())

df = pd.DataFrame([])
for file in files:
    df1 = pd.read_csv(file)
    df = pd.concat([df,df1])

df.to_csv('alberta.csv',index=False)
