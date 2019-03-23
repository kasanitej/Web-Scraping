from urllib.request import urlopen
from bs4 import BeautifulSoup as BS
import bs4
from math import ceil

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

    #Header Details
    Header = Soup.find('header',{'class':'section-head'})
    program = Header.find('h1').get_text()
    print(program)
    a = Header.find('a')
    provider = a.get_text()
    #Agency Description
    html = urlopen(a['href']).read()
    Soup = BS(html, 'lxml')
    article_block = Soup.find('article',{'class':'article'})
    #Whole Details
    info = {'Program': '=HYPERLINK("{}","{}")'.format(url, program),'provider': provider,**info, **block_info(article_block)}
    return info

def list_to_str(Add_sevices):
    serv = ''
    for i in range(0, ceil(len(Add_sevices) / 5)):
        serv += ','.join(Add_sevices[5 * i:(i + 1) * 5]) + '\n'
    return serv

def services(result, additional_services):
    toggle = result.find('a', {'class': 'search-result-toggle'})
    Add_sevices = []
    if toggle:
        No_Add_services = toggle.get_text().strip()
        services = result.find('div', {'class': 'search-result-inner'}).find_all('li')
        for service in services:
            a = service.find('a')
            if a['href'] == '#':
                add_serv = a.get_text().strip()
                Add_sevices.append(add_serv)
            else:
                if add_serv in additional_services.keys():
                    additional_services[add_serv].append(a['href'])
                else:
                    additional_services[add_serv] = [a['href']]
    serv = list_to_str(Add_sevices)[:-1]
    return serv

def dict_exchange(k):
    url_dict = {}
    urls = sum(k.values(),[])
    urls = list(set(urls))
    for url in urls:
        for serv,addr_list in k.items():
            if url in addr_list:
                if url in url_dict.keys():
                    url_dict[url].append(serv)
                else:
                    url_dict[url] = [serv]
    return urls, url_dict
