from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import bs4

url = 'http://mb.211.ca/program-at-site/psychiatric-emergency-room-nurses-at-st-boniface-hospital/'

def site_info(url):
    html = urlopen(url).read()
    Soup = BS(html, 'lxml')
    info = {}
    def block_info(block):
        data = {}
        for line in block:
            if isinstance(line,bs4.element.Tag) and line.name != 'br':
                if line.name == 'h4':
                    label = line.get_text()
                elif label in data.keys():
                    data[label] += '\n'+line.get_text().strip().strip('\n')
                else:
                    data[label] = line.get_text().strip().strip('\n')
            elif not isinstance(line,bs4.element.Tag) and len(line.strip())!=0:
                if label in data.keys():
                    data[label] += '\n'+line.strip().strip('\n')
                else:
                    data[label] = line.strip().strip('\n')
        data[label] = data[label].replace('Get Directions','')
        return data

    #Service Description
    article_block = Soup.find('article',{'class':'article'})
    info = {**info, **block_info(article_block)}
    #Address & Mailing Address
    info_block = Soup.find('ul',{'class':'list-info'}).find_all('li')
    for ul in info_block:
        info = {**info, **block_info(ul)}
    #Extra details
    side_blocklist = Soup.select('ul[class="list-utilities"]')
    for ul in side_blocklist:
        a_list = ul.find_all('a')
        if len(a_list)==0: a_list = ul
        for a in a_list:
            label = 'Not available'
            for li in a:
                if isinstance(li,bs4.element.Tag) and (li.name == 'span' or li.name == 'strong'):label = li.get_text()
                elif isinstance(li,bs4.element.NavigableString):
                    if len(li.strip())!=0: info[label] = li.strip()

    url = Soup.find('header',{'class':'section-head'}).find('a')['href']
    html = urlopen(url).read()
    Soup = BS(html, 'lxml')
    #Agency Description
    article_block = Soup.find('article',{'class':'article'})
    info = {**info, **block_info(article_block)}
    return info
