#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 13:30:28 2019

@author: kevin
"""

url = "https://fr.wikipedia.org/wiki/Liste_des_communes_de_France_les_plus_peupl%C3%A9es"

from bs4 import BeautifulSoup
import requests
import pandas as pd


def get_soup_from_url(url): 
    page = requests.get(url)
    return BeautifulSoup(page.text,'lxml') 


soup = get_soup_from_url(url)
rows = soup.find("tbody").findChildren("tr")
inc = 0
ville = []
for row in rows : 
    if inc <=10 and inc >= 1: 
        ville.append(row.find('b').text)
    inc+=1


def find_dist_ville (listVille):
    dic=[]
    for ville in listVille : 
       
        for ville2 in listVille :
            if ville!=ville2 : 
                soup = get_soup_from_url('https://fr.distance24.org/'+ville+'/'+ville2)
                dic.append([ville,ville2,int(soup.find('p').text.split(' ')[12][:3])])
    return dic
dist_ville = find_dist_ville(ville)
import itertools
l =list(itertools.combinations(dist_ville,2)) #censé remove doublon mais marche pas ici
df = pd.DataFrame(dist_ville, columns=['origin','dest','distance'])
df.set_index(['origin','dest']).unstack()
df.sort_values(by=['distance'],ascending=False)

#def with_api_dist_ville (listVille) :
#    