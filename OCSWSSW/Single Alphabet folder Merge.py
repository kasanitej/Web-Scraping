import os, pandas as pd

folder = 'R'
path = os.path.dirname(__file__)+'\\'+folder

data = {'Name' : [],'Registration No' : [],'Previous Name' : [],'Business Name' : [],
'Business Address' : [],'Business Phone' : [],'Class of Certificate of Registration': []}
df = pd.DataFrame(data)

for folder1 in os.listdir(path):
    folder1 = path+'\\'+folder1
    file = os.listdir(folder1)[0]
    print(file)
    df1 = pd.read_csv(folder1+'\\'+file)
    df = pd.concat([df,df1],sort=False)

df['Registration No']=df['Registration No'].astype(int)
df.drop_duplicates(subset='Registration No',keep='first',inplace=True)
df.sort_values(by=['Registration No'], ascending=True, inplace=True)
df.to_csv(path+'\\'+folder+'_'+str(df.shape[0])+'.csv',index=False)
print(folder,df.shape[0])
