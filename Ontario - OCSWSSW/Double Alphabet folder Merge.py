import os, pandas as pd

search = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
folders = ['YS']
for folder_name in folders:
    folder = folder_name

    path = os.path.dirname(__file__)+'\\'+folder

    data = {'Name' : [],'Registration No' : [],'Previous Name' : [],'Business Name' : [],
    'Business Address' : [],'Business Phone' : [],'Class of Certificate of Registration': []}
    df = pd.DataFrame(data)
    for file in os.listdir(path):
        df1 = pd.read_csv(path+'\\'+file)
        df = pd.concat([df,df1],sort=False)

    df['Registration No']=df['Registration No'].astype(int)
    df.drop_duplicates(subset='Registration No',keep='first',inplace=True)
    df.sort_values(by=['Registration No'], ascending=True, inplace=True)
    df.to_csv(path+'\\'+'00_'+folder+'_'+str(df.shape[0])+'.csv',index=False)

    print(folder_name,'\t',df.shape[0])
    
    #Just to make the file at the top in my folder
    file_path = path +'\\'+ os.listdir(path)[1]
    file_path1 = path +'\\'+ os.listdir(path)[0]
    os.utime(file_path1,(os.stat(file_path).st_atime, os.stat(file_path).st_mtime))
