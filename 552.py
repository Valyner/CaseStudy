import pandas as pd
import numpy as np
import json 
from itertools import permutations
from pandas.io.json import json_normalize
from urllib.request import urlopen
import requests

url = "https://raw.githubusercontent.com/Valyner/GetirCaseStudy/main/getir_algo_input.json"
data = json.loads(requests.get(url).text)

mat=pd.DataFrame(data['matrix'])
vehicles=pd.DataFrame(data['vehicles'])
job= pd.DataFrame(data['jobs'])
for i in range(0,3) :
    vehicles.iloc[i,2]=vehicles.iloc[i,2][0]
for i in range(0,7) :
    job.iloc[i,2]=job.iloc[i,2][0]
    
y=[]
# Binary değerler atanır.
for i in range(1<<21):
    t=bin(i)[2:]
    t='0'*(21-len(t))+t      
    y.append(list(map(int, list(t))))        
  

test=pd.DataFrame(y)

sonuc=test[test.sum(axis=1)==7] # Sipariş sayısı kontrolü
  
sonuc_y=sonuc.copy()
x=sonuc_y.values.tolist()
x=list(x)
y_assy=[]

# 2^21 farklı olasılığa ait binary yapısı oluşturulur.
for i in range(0,len(x)):
    den=pd.DataFrame(np.asarray(x[i]).reshape(3,7))
    for j in range(0,len(den.columns)):
        if den.iloc[:,j].sum()!= 1: # siparişe sadece 1 tane araç gidebilir 
            y_assy.append(np.asarray(x[i]))
            break 
    for j in range(0,len(den.index)):
        tot=0
        for k in range(0,len(den.columns)):
            tot+= den.iloc[j,k]*job.iloc[k,2]
        if tot > vehicles.iloc[j,2]: # araç kapasite kontrol
            y_assy.append(np.asarray(x[i]))
            break 
    if den.iloc[:,:].sum().sum()!=len(job.index): # sipariş sayısı kadar araç gönderildi
       y_assy.append(np.asarray(x[i]))


df1=pd.DataFrame(y_assy)
df2=pd.DataFrame(x)


df = df2.merge(df1, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only'] # 2 tablo arasındaki farklı datalarını almak için.

numpy_array = df.drop('_merge',axis=1).to_numpy()
numpy_array=np.asarray(numpy_array).reshape(len(numpy_array)*3,7)
df=pd.DataFrame(numpy_array)  
total_time=df.copy()   
df=total_time.copy()
df.insert(7,"Total",0)
df.insert(8,"Route","")

# Araçların oluşturulacak rotayı en az süreyle tamamlaması amaçlanmaktadır.
# Farklı rotaların sürelerini test etmek amacı ile ilgili aracın gideceği
# tüm varyasyonlar combi fonksiyonunda belirlenir.
def combi(a,num,list_arg): # 
    comb = permutations(a, num)

    for i in comb:
        list_arg.append(i)
        
# Belirlenen kombinasyonların süre hesaplamaları yapılır. 
# Listeye append edilir. 

def calc(list_calc,vehicle_no):
    for j in range(0,len(list_calc)):
        count=0
        list_calc[j]=list(list_calc[j])
        count+=mat.iloc[vehicle_no,list_calc[j][0]+3]
        for i in range(0,len(list_calc[j])-1):
            count+=mat.iloc[list_calc[j][i]+3,list_calc[j][i+1]+3]
        list_calc[j].append(count)

# Tüm olası ihtimaller için combi ve calc fonksiyonları çağırılır
# Servis süreleri eklenir ve Rotalar tabloya yazılır.
for i in range(0,len(df.index)):
    a=[]
    for j in range(0,len(df.columns)-2):
        
        if df.iloc[i,j] == 1 :
            a.append(df.columns[j])
    if len(a)>0:
        num=len(a)
        list_poss=[]
        combi(a, num, list_poss)
        calc(list_poss,i%3)
        list_poss=sorted(list_poss,key=lambda l:l[-1], reverse=False)          
        df.iloc[i,-2]=list_poss[0][-1]
        for k in range(0,num):
            df.iloc[i,-2]+= job.iloc[j,3]
        df.iloc[i,-1]=str(list_poss[0][:-1])
        
df.insert(9,"GrandTotal",0)   
df.insert(10,"Index",0)
df.insert(11,"Vehicle",0)

for i in range(0,int((len(df.index)/len(vehicles.index)))):
    
    i=i*3
    df.iloc[i,9]= df.iloc[i,7]+df.iloc[i+1,7]+df.iloc[i+2,7]
    df.iloc[i+1,9]= df.iloc[i,7]+df.iloc[i+1,7]+df.iloc[i+2,7]
    df.iloc[i+2,9]= df.iloc[i,7]+df.iloc[i+1,7]+df.iloc[i+2,7]
    df.iloc[i,10]=i/3
    df.iloc[i+1,10]=i/3
    df.iloc[i+2,10]=i/3
    df.iloc[i,11]=1
    df.iloc[i+1,11]=2
    df.iloc[i+2,11]=3
df=df.sort_values("GrandTotal")

for i in range(0,3):
    print("For Vehicle %d, index of job(s) and Route %s" %(df.iloc[i,11],df.iloc[i,8]))
print("TotalTime is %d" %(df.iloc[0,9]))
                     
        
