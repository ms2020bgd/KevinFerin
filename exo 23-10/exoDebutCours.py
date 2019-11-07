#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 13:33:00 2019

@author: kevin
"""

import pandas as pd
import os,sys
import datetime

people = pd.read_csv("people.csv")

def clean_people(df):
    # rename columns:
    df = df.rename(columns={'email address': 'email'})
    
    # remove rows which have an empty "first_name" (NA):
    #df = df[df.first_name.notna()] <- equivalent to next line:
    df = df.dropna(subset=['first_name'])
    
    # drop duplicates on ID column:
    df = df.drop_duplicates()
    
    # Normalize gender column:
    df['gender'] = df['gender'].replace({'Female': 'F', 'Male': 'M'})
    
    # Convert column "age" to number (coerce: put NaN for bad values):
    df['age'] = pd.to_numeric(df.age, errors='coerce')
    
    # Convert columns to date type:
    df['registration'] = pd.to_datetime(df.registration)
    df['last_seen'] = pd.to_datetime(df.last_seen, unit='s')
    # When missing, last seen should fallback to the registration date:
    df['last_seen'] = df.last_seen.combine_first(df.registration)
    
    # Add a "full_name" column by concatenating two other ones:
    df['full_name'] = df.first_name + " " + df.last_name
    
    # Add a "country" column by extracting it from the address, with a split:
    df['country'] = df.address.str.split(', ').str[1]
    
    # Column "money" contains values like "$50.23" or "€23,09".
    # We want to make it uniform (only dollar currency) and as number, not str.
    df['currency'] = df.money.str[0]  # extract first char ($/€) to a new "currency" column
    df['money'] = df.money.str[1:].str.replace(',', '.')  # extract remaining chars and replace , by .
    df['money'] = pd.to_numeric(df.money)  # convert to number
    # convert euros cells to dollar:
    df.loc[df.currency == '€', 'money'] = df[df.currency == '€'].money * 1.10
    del df['currency']  # remove "currency" column which is now useless
    
    # Keep only rows where email is not NA:
    df = df.dropna(subset=['email'])
    # Keep only rows where email is a good email:
    # CAUTION: in the real world you should not use dummy regexes like this to validate email addresses,
    # but instead use a dedicated pd.to_datetime(people.last_seen)tool like https://github.com/syrusakbary/validate_email.
    df = df[df.email.str.contains('.+@[0-9a-zA-Z\.\-_]+\.\w{2,}')]
    # Some users may use email alias (example: john.smith+truc@gmail.com is an alias for john.smith@gmail.com).
    # We want to drop these duplicates. To do that, we extract the 'alias' part with a regex:
    groups = df.email.str.extract('([0-9a-zA-Z\.\-_]+)(\+[0-9a-zA-Z\.\-_]+)?(@[0-9a-zA-Z\.\-_]+\.\w{2,})')
    df['email'] = groups[0] + groups[2]  # we override the email with the email without the alias part
    # Then, just use drop_duplicates, which will keep the first line by default:
    df = df.drop_duplicates(subset=['email'])
    
    return df

df_clean = clean_people(people)
df_clean.inactive = df_clean.last_seen < datetime.datetime(2018,10,23)
df_clean = df_clean.dropna(subset=['phone'])
df_clean.phone=df_clean.phone.str.replace('.','')
df_clean = df_clean[df_clean.phone.str.contains('[0-9]{10}')]
df_clean['phoneStarting06/07']=df_clean.phone.str[:2].isin(["06","07"])
#Marche pas cette librairie

from geopy.geocoders import Nominatim
import time
geolocator = Nominatim(user_agent="Cours 23/10")
location = geolocator.reverse("49.6326, 18.2841")
location.raw['address']['village'] in df_clean.address.iloc[0]
l = []
for i,j,a in df_clean[['lat','lon','address']].values:
    try : 
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="iteration")
        time.sleep(0.4)
        location = geolocator.reverse(""+str(i)+", "+str(j))
        if ((location.raw['address']['country'] in a) or (location.raw['address']['village'] in a)) :
            l.append(True)
        else : l.append(False)
    except : 
        l.append(False)
        
df_clean['LatLongToCountry'] = l
