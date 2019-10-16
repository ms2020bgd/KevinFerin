# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import json


def get_soup_from_url(url): 
    page = requests.get(url)
    return BeautifulSoup(page.text,'lxml') 

def get_top_contrib (url) :
    soup = get_soup_from_url(url)
    rows = soup.find("tbody").findChildren("tr")
    #print(result[0].find_all("td"))
    dic = {}
    for row in rows :       
        rowList = row.find_all("td")
        rowDic = {'User' : rowList[0].text.split(' (')[0],
                  'Contrib' : int(rowList[1].text),
                  'Location' : rowList[2].text
                 }
        dic[int(row.find("th").text.replace('#',''))]=rowDic
   
    return dic

headers = {'Authorization': 'Token ba1495e0d4956dedc48cb93017474ff495053fb7'}


def get_stars (dic) :
    for (key, value) in dic.items() :
        res = requests.get('https://api.github.com/users/'+value['User'], headers=headers)
        json = res.json()
        value['NbRepos']=json['public_repos']
        value['TotalStars']=0
        p,v = 1,True
        jsons=[]
        while(v) :
            res = requests.get('https://api.github.com/users/'+value['User']+'/repos?page=%s' %p, headers=headers)
            v = len(res.json())!=0
            p+=1
            if(v) :
                jsons.append(res.json())
        for el in [json for json in jsons] :
            for el2 in el : 
                value['TotalStars']+=el2['stargazers_count'] 

        if(key%3==0):
            print(key)
        
    return dic


#url =  "https://gist.github.com/paulmillr/2657075"
#top_contrib = get_top_contrib(url)
#print("End top_contrib")
#top_stars = get_stars(top_contrib)
#print("End get star")

#with open('result.json', 'w') as outfile:
#    json.dump(top_stars, outfile)
#print("Stored json")


import pandas as pd
import os 
data = pd.read_json("result.json",orient="value")
data = data.transpose()
l=[]
for i in range (1,len(data['TotalStars'])+1):
    if (data['NbRepos'].get(i)!= 0 ):
        l.append(data['TotalStars'].get(i)/data['NbRepos'].get(i))
    else : 
        l.append(0)
data['mean_star']=l
data.sort_values(by=['mean_star'],ascending =False)

data.to_json("resultSortedByMeanValue.json")
