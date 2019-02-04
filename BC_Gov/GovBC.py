from urllib.request import  urlopen
from bs4 import BeautifulSoup as BS
import bs4
import pandas as pd, os

urlist = []
print('Collecting webpages........')
url = 'https://www2.gov.bc.ca/gov/search?q=mental+health+services%2Binmeta%3Acfdsda_cfdServices%3DChild%2FYouth+Mental+Health&id=3101EE72823047269017D08E55AF6441&tab=1&sourceId=A0AE7036F68548C19B12B2BAB4483BFC'
while(url):
    html = urlopen(url)
    Soup = BS(html,'lxml')
    results = Soup.find_all('div', {'class':'result_item'})
    urlblock = [result.find({'a':'href'}) for result in results]
    urlist += [urltag['href'] for urltag in urlblock]
    #################################################################
    Pgnumblock = Soup.find('ul',{'id':'paginationSearch'})
    nextpg = Pgnumblock.find_all({'a':'href'})
    url = False
    pick = 0
    for pg in nextpg:
        if pg['href'] == '#':
            pick = 1
            continue
        if pick == 1:
            url = 'https://www2.gov.bc.ca/gov/search'+pg['href']
            break

url=pd.DataFrame(urlist,columns=['url'])
path = os.path.dirname(__file__)+'\\url.csv'
url.to_csv(path, index=False)

df = pd.DataFrame([])
for url in urlist:
    print(url)
    html = urlopen(url)
    Soup = BS(html,'lxml')
    infoblock = Soup.find('div',{'id':'main-content'})
    name = infoblock.find('h1').get_text()
    data = {}
    data['name']=name
    bodyblock = infoblock.find('div',{'id':'body'})
    for line in bodyblock:
        if not isinstance(line,bs4.element.NavigableString):#not space
            if line.name == 'p':#avoiding div
                for li in line:#going through each linen
                    if li.name == 'strong':
                        column = li.get_text().strip().replace(':','')
                    elif li.name != 'br':
                        if column in data.keys():
                            if isinstance(li,bs4.element.NavigableString):
                                data[column] += '\n'+li.strip()
                            else:
                                data[column] += '\n'+li.get_text().strip()
                        else:
                            if isinstance(li,bs4.element.NavigableString):
                                data[column] = li.strip()
                            else:
                                data[column] += '\n'+li.get_text().strip()
            if line.name == 'ul':#avoiding div
                for li in line:#going through each line
                    if not isinstance(li,bs4.element.NavigableString):
                        if column in data.keys():
                            data[column] += '\n'+li.get_text().strip()
                        else:
                            data[column] = li.get_text().strip()
    df1= pd.DataFrame([data])
    df = pd.concat([df,df1],sort=False)

path = os.path.dirname(__file__)+'\\GovBC.csv'
df.to_csv(path, index=False)
