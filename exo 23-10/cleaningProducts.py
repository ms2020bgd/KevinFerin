#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 18:28:59 2019

@author: kevin
"""

import pandas as pd 
import os,sys
import pygeoip as geoIP
import requests
import numpy as np 
import pycountry
import PyCurrency_Converter
import currency

#currency.convert('USD','EUR',200)
from currency_converter import CurrencyConverter
converter= CurrencyConverter()
pathname = os.path.dirname(__file__)

products = pd.read_csv("products.csv", sep =";")

def getCountryFromIP (ip_adress):
    response = requests.get("https://freegeoip.app/json/"+ip_adress)
    if ((response.status_code==200) and (response.json()["country_code"]!='')):
        return response.json()["country_code"]
    else : 
        return ''

def getCurrencyFromCountry (country) :
    if (country != ''): 
        response = requests.get("https://restcountries.eu/rest/v2/alpha?codes="+country)
        k =response.json()[0]["currencies"][0]["code"]
        return k
    else : 
        return ''

from multiprocessing import Pool
p = Pool(processes=8)
countries = p.map(getCountryFromIP,products['ip_address'])
currencies = p.map(getCurrencyFromCountry,countries)

products['country']=countries
products['currency']=currencies


products.price = products.price.astype('str')
products.price = products.price.str.split(' ').str[0]
def take(x,y):
    if y != '': 
        return y 
    else : return x
products.currency = products.currency.combine(products.price.str.split(' ').str[1].fillna(''),take)

def func (row):
    try :
        if row["currency"]!='' :
            return converter.convert(row["price"],row["currency"],'EUR')
         
        else : 
            return np.NaN

    except ValueError :
        return np.NaN
            

products["priceEuros"]=products.apply(lambda row : func(row),axis=1)
products.priceEuros = products.priceEuros.astype(float)
products.dropna(subset=['priceEuros'], inplace=True)


def getDifferentAllergie(products):
    temp = products.infos.str.lower().str.replace("ingredients:",'').str.replace("contains",'') \
    .str.replace("and",'').str.replace("contain",'').str.replace("may",'').str.replace(',','') \
    .str.replace('  ',' ').str.strip().str.split(' ')
    df2 = pd.DataFrame(temp.values.tolist()).replace('',None)
    k=df2.values.flatten()
    k=k[k!=None]
    return pd.Series(k).unique()

uniqueAl = getDifferentAllergie(products)


