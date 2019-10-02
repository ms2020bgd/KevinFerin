# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 18:07:18 2019

@author: Kevin
"""

from bs4 import BeautifulSoup
import requests
import numpy as np 

def get_soup_from_url(url): 
    page = requests.get(url)
    return BeautifulSoup(page.text,'lxml')



### Function that find numberth link to a wikipedia article
def find_link(soup,number) : 
    #The text is contained in a p tag included in the parser-output class tag 
    children = soup.find("div", class_="mw-parser-output").findChildren("p", recursive=False)
    #For every p tag we look for all the a tags that have a href 
    for child in children:
        k = child.findChildren("a", href=True, recursive=False)
        #Check the numberth valid link 
        if (len(k)>0 and number>0): 
            number-=1
        elif (len(k)>0 and number==0) : 
            return k[0]['href']
    
    #This part is a backup strategy to find links 
    for a in soup.find_all("a",href=True): 
        if ( a['href'].find('/wiki/')==0) : 
            if (('/wiki/Aide' not in a['href']) and ('/wiki/Fichier' not in a['href'])):
                if(number==0):
                    return a['href']
                else : number-=1
### Function that given a wikipedia URL, calculate the depth to the article about Philosophy
def get_distance(urlFirstArticle):
    soup = get_soup_from_url(urlFirstArticle)
    newUrl = urlFirstArticle
    profondeurToPhilo = 0 
    parcours =[urlFirstArticle]
    while (newUrl != "https://fr.wikipedia.org/wiki/Philosophie") : 
        soup = get_soup_from_url(newUrl)
        print("L'article est {}".format(soup.find("h1",class_="firstHeading").text))
        s=0
        k = find_link(soup,s)
        newUrl = "https://fr.wikipedia.org"+k
        ## Check to avoid loop between two articles 
        ## So we take the next link
        while (newUrl in parcours): 
            s+=1
            k = find_link(get_soup_from_url(parcours[-1]),s)
            newUrl = "https://fr.wikipedia.org"+k
        parcours+=[newUrl]
        profondeurToPhilo+=1
    return profondeurToPhilo

### Calculate the mean distance
def get_mean_dist(numberOfArticle):
    dist = []
    for i in range(1,numberOfArticle+1):
        print("Nombre d'article {}/{}".format(i,numberOfArticle))
        ## This is the url to get a random page of wikipedia
        urlFirstArticle = "https://fr.wikipedia.org/wiki/Special:Random"
        dist.append(get_distance(urlFirstArticle))
    print ("La profondeur philosophique moyenne est ", np.mean(dist))
    

urlFirstArticle = "https://fr.wikipedia.org/wiki/Axiome"
#print(get_distance(urlFirstArticle))
get_mean_dist(5)
