from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import Each_site, os , pandas as pd

url = 'http://mb.211.ca/top-level-terms/mental-health-addictions/?language=en&filter%5B4475%5D=youth-mental-health'

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
    data = {'Program':'=HYPERLINK("{}","{}")'.format(url,program),'provider': provider, **info}
    df1 = pd.DataFrame([data])
    df =  pd.concat([df,df1], sort=False)

path = os.path.dirname(__file__)+'\\Manitoba_Mental_health_Addictions.csv'
df.to_csv(path, index=False)
