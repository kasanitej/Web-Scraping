from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import Each_site, os , pandas as pd
from math import ceil

url = 'http://mb.211.ca/top-level-terms/mental-health-addictions/page/2/?page=1&language=en&filter%5B4475%5D=youth-mental-health'

def services(result):
    toggle = result.find('a',{'class':'search-result-toggle'})
    Add_sevices = []
    if toggle:
        No_Add_services = toggle.get_text().strip()
        services = result.find('div',{'class':'search-result-inner'}).find_all('li')
        for service in services:
            serv = service.find('a',{'href':'#'})
            if serv:
                Add_sevices.append(serv.get_text().strip())
    serv = ''
    for i in range(0,ceil(len(Add_sevices)/5)):
        serv += ','.join(Add_sevices[5*i:(i+1)*5])+'\n'
    serv = serv[:-1]
    return serv

html = urlopen(url).read()
Soup = BS(html, 'lxml')

results = Soup.find_all('li',{'class':'search-result'})

df = pd.DataFrame([])
for result in results:
    a = result.find('a')
    url = a['href']
    program = a.get_text()
    provider = result.find('h6').get_text()
    print(program)
    info = Each_site.site_info(url)
    Add_serv = services(result)
    data = {'Program':'=HYPERLINK("{}","{}")'.format(url,program),'provider': provider, **info, 'Additional Services': Add_serv}
    df1 = pd.DataFrame([data])
    df =  pd.concat([df,df1], sort=False)


path = os.path.dirname(__file__)+'\\Manitoba_Mental_Health_Addiction.csv'
df.to_csv(path, index=False)
