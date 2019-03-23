import pandas as pd
import os

def check1(x):
    Active = ['reinstated', 're-issued', 'active','activce','reissued','renstated','reinstateed',
    'reinstasted','reinstatement','reinstaed','reinstared','general certificate of registration issued',
    'certificate issued on','certificate issed on']
    NotActive = ['cancelled', 'revocation', 'suspended', 'retired','Reprimand','cancel','surrendered','inctive','resignation']
    Act = any([word in x for word in Active])
    NAct = any([word in x for word in NotActive])
    if Act:
        return 'active'
    elif NAct:
        return 'inactive'
    elif Act and NAct:#Both Active and inactive
        return 'confused'
    else:#None
        return 'what'

def check(x):
    if x != 'nan':
        x = x.lower()
        x = x.replace('..','.')
        x = x.replace('.,','')
        x = x.replace('jan.','january')
        x = x.replace('feb.','febuary')
        x = x.replace('mar.','march')
        x = x.replace('apr.','april')
        x = x.replace('may.','may')
        x = x.replace('jun.','june')
        x = x.replace('jul.','july')
        x = x.replace('aug.','august')
        x = x.replace('sep.','september')
        x = x.replace('sept.','september')
        x = x.replace('oct.','october')
        x = x.replace('nov.','november')
        x = x.replace('dec.','december')
        if len(x.strip())==0:
            return 'Active'
        if x[-1]=='.':
            if len(x)>= 957:
                return 'inactive'
            x = x.split('.')[-2]
            return check1(x)
        else:
            return check1(x)
    else:
        return 'Active'

folder = os.path.dirname(__file__)
file = folder+'\\00_Files_31899.xlsx'
df = pd.read_excel(file,header=1)

df['Description'] = df['Description'].astype('str')
df['Status'] = df[['Description']].applymap(check)

df[['Registration No','Description','Status']].to_csv(folder+'\\check.csv',index=False)
