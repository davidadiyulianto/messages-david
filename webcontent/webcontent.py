
# coding: utf-8

# In[1]:

from __future__ import print_function
from httplib import HTTP
import bs4
from collections import Counter
import pandas as pd
import urllib as url
import datetime as dt
import urllib2
import httplib
import requests
import string
import time
import os,sys
import csv
import re


# In[80]:

url="https://www.tokopedia.com/login.pl"


# In[3]:

def opening(url):
    html=requests.get(url)
    soup=bs4.BeautifulSoup(html.text)
    return soup


# In[4]:

def findTokopedia(soup):
    return re.findall('([^<]*tokopedia[^>]*)',str(soup))


# In[26]:

def findCss(soup):
    allCss = soup.findAll(type='text/css')
    return allCss


# In[13]:

def findAllCss(soup):
    return re.findall('([^ ]*tokopedia[^>]*\.css)',str(soup.text))


# In[83]:

def findButton(soup):
    allButton = soup.findAll('button')
    for i in allButton:
        print (i.text)
    return allButton


# In[114]:

def findLink (soup):
    arrayLink=[]
    allLink = soup.findAll('a', href=True)
    for i in allLink:
        arrayLink.append(i['href'])
    return arrayLink


# In[8]:

def findInputField(soup):
    inputFields = soup.findAll('input')
    passwordFields = soup.findAll('input',type='password')
    print ("password fields count = {}".format(len(passwordFields)))
    textFields = soup.findAll('input',type='text')
    print ("text fields count = {}".format(len(textFields)))
    return inputFields


# In[9]:

def findImage(soup):
    return soup.findAll("img")


# In[10]:

def findIcon(soup):
    return soup.findAll("i")


# In[162]:

def main():
    soup = opening(url)
    
    tokopediaFound=False
    topedCSS=False
    
    # --- find tokopedia string in html ---
    print ("1. Checkin tokopedia string in the page html")
    tokopediaString = findTokopedia(soup)
    if tokopediaString:
        print("found tokopedia in html string")
        tokopediaFound=True

    # --- find CSS ---
    print ("2. Checking all CSS in the page")
    CSS = findCss(soup)
    for i in CSS:
        try:
            if "tokopedia" in i['href']:
                print (i['href'])
                topedCSS=True
                print ("find css related to tokopedia")
        except:
            pass

    # --- find button ---
    print ("3. Checking all buttons in the page")
    button = findButton(soup)
    print (button)
    
    # --- find links ---
    print ("4. Checking all links in the page")
    links = findLink(soup)
    print (links)
    
    # --- find images ---  
    print ("5. Checking all images in the page")
    images = findImage(soup)
    for i in images:
        print (i['alt'] + " = " + i['src'])
        
    # --- find icons ---
    print ("6. Checking all icons in the page")
    icon = findIcon(soup)
    for i in icon:
        print (i)

    # --- find input fields ---
    print ("7. Checking all input fields in the page")
    inputField = findInputField(soup)
    print (inputField)
    
if __name__=="__main__":
    main()
