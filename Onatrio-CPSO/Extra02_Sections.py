import Doclist as D
from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
from threading import Thread
import queue
import pandas as pd

urls =  list(set(D.urllist + D.urllist1))

def ExtractSections(url):
    try:
        html = urlopen(url)
    except:
        print('Connection \'{}\' not established'.format(url.split('/')[-2]))
        return Conn.put([url])

    Soup = BS(html.read(),"lxml")
    sec = Soup.find_all({'section':'data-jump-section'})
    sections = [s['data-jump-section'] for s in sec]
    Name=Soup.find('h1').get_text().strip().split('\n')[0]
    q.put(sections)
    name.put([Name])

q = queue.Queue()
name = queue.Queue()
Conn = queue.Queue()

while(len(urls) != 0):
    th = []
    for url in urls:
        t = Thread(target=ExtractSections,args=(url,))
        t.start()
        th.append(t)
    for t in th:
        t.join()
    urls = []
    while not Conn.empty():
        urls += Conn.get()

sec = []
while not q.empty():
    temp = q.get()
    sec.append(temp)

Full_Name = []
while not name.empty():
    temp = name.get()
    Full_Name += temp



SecTable = pd.DataFrame([],columns = list(set(sum(sec,[]))), index = Full_Name)
for idx,row in enumerate(sec):
    temp = []
    for i in SecTable.columns:
        if i in row:
            temp.append(1)
        else:
            temp.append(0)
    print(SecTable.loc[Full_Name[idx]])
    SecTable.loc[Full_Name[idx]] = temp
    print('------------------------------------')

SecTable.to_csv(r'C:\Users\kasan\OneDrive\PC Desktop\Web Scraping\section.csv')
# import numpy as np
# import json
#
# path = r'C:\Users\kasan\OneDrive\PC Desktop\Web Scraping\First.json'
# m = np.array([[1.6543,2,3],[4,5,6],[7,8,9]])
# json.dump(m.tolist(),open(path, 'w'))
#
# obj_text = open(path, 'r').read()
# b_new = json.loads(obj_text)
# a_new = np.array(b_new)
#
# print(a_new)
