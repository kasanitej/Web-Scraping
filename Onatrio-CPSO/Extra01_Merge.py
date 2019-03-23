import pandas as pd
import os

df1 = pd.read_csv(r'C:\Users\kasan\OneDrive\PC Desktop\Web Scraping\CPSO\Psychiatry\urllist.csv')
df2 = pd.read_csv(r'C:\Users\kasan\OneDrive\PC Desktop\Web Scraping\CPSO\child & Adolescent phy\urllist.csv')

df3 = pd.concat([df1,df2],ignore_index=True)
df3.drop_duplicates(keep='first',inplace=True)
df3.sort_values(by=['Name'], ascending=True, inplace=True)
df3.to_csv(os.path.dirname(__file__)+r'\finalUrllist.csv',index=False)

print(df3['url'].tolist())
