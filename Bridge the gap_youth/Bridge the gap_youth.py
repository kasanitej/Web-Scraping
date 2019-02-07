from urllib.request import urlopen,Request
from bs4 import BeautifulSoup as BS
import re, bs4
import pandas as pd

url = 'https://www.bridgethegapp.ca/adult/service-directory/service_directory_category/youth/'

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urlopen(req).read()
Soup = BS(html, 'lxml')

def details(block):
    data = {}
    url_block = block.find('a',{'target':'_self'})
    url = url_block['href']
    name = url_block.get_text()
    data['name'] ='=HYPERLINK("{}","{}")'.format(url,name)
    #####################################
    pattern = re.compile(r'.*content')
    content_block = block.find('div',{'class':pattern})
    if content_block:
        contents = content_block.find_all('span')
        content = '\n'.join([content.get_text().strip() for content in contents])
        data['content']=content
        # print(data['content'])
    #####################################
    pattern = re.compile(r'.*tags')
    tag_block = block.find('div',{'class':pattern})
    if tag_block:
        tags = tag_block.find_all('a')
        tag = '\n'.join([tag.get_text() for tag in tags])
        data['tags']=tag
    #######################################
    pattern = re.compile(r'.*meta')
    meta_blocks = block.find_all('div',{'class':pattern})
    for meta in meta_blocks:
        label = meta.find('label').get_text().replace(':','')
        span = meta.find('span')
        info = []
        for every_line in span:
            if isinstance(every_line,bs4.element.NavigableString):
                info.append(every_line.strip())
            elif every_line.name !='br':
                info.append(every_line.text.strip())
        data[label]='\n'.join(info)
    return data

wpbdp_lists = Soup.find('div', {'id':"wpbdp-listings-list"})
a_list = wpbdp_lists.find_all('div',{'class':'listing-details'})

df = pd.DataFrame([])
for id, a in enumerate(a_list):
    print(id)
    df1 = pd.DataFrame([details(a)])
    df = pd.concat([df,df1],sort=False)

import os
path = os.path.dirname(__file__)+'\\bridgethegap.csv'
df.to_csv(path, index=False)
