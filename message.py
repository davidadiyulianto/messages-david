
# coding: utf-8

# LIBRARY:
from __future__ import print_function
from httplib import HTTP
from urlparse import urlparse,urlunparse
from bs4 import BeautifulSoup
from collections import Counter
import pandas as pd
import db_common as db
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



# --- get yesterday date ---
def yersterdayDate():
    # yesterday = (dt.date.today() - dt.timedelta (days=1))
    yesterday = dt.date.strftime(dt.date.today() - dt.timedelta(days = 1),"%Y-%m-%d")
    return yesterday

# --- query messages ---
def query(date):
    print ("begin querying data")
    start_time = time.time()
    messages = db.get_whole_data(
        query=
        """
        select distinct msg_reply,date(create_time)
        from ws_message_reply
        where date(create_time)='{}'
        """
        .format(date),
        DB = {"name":"tokopedia-message","ip":"192.168.1.81"},
        port_used=5432,
        convert_dict=True)
    print ("query finished")
    print("processing time = %s seconds" %(time.time() - start_time))
    filename=("msg_{}.csv").format(date)
    messages.to_csv(filename,index=False)
    return messages


# --- getting final url---
# by URLLIB (blibli.com can't be accessed)
def destination(url):
    try:
        response = urllib2.urlopen(url)
        print ("4 " + response.url)
        return response.url
    except:
        print ("0 " + url)
        return False
        # response=os.system("ping -n 1 " + urlparse(url).netloc)
        # if response == 0 :
        #     return url
        #     print ("2")
        # else:
        #     return False

# by HTTP LIB
def unshorten_url(url):
    try:
        parsed = urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()
        # print(response.status)
        if response.status/100 == 3 and response.getheader('Location'):
            if (response.status % 10)<=1 :
                print ('1 '+ response.getheader('Location'))
                return response.getheader('location')
            else :
                print ('1 '+ url)
                return url
        elif response.status/100 == 2 :
            print ('2 ' + url)
            return url
        else :
            print ('3 ' + url)
            return False
    except:
        return destination(url)

# by requests lib
def finalDestination(url):
    session = requests.Session()  # so connections are recycled
    resp = session.head(url, allow_redirects=True)
    print("1 " + resp.url)
    return resp.url
# -----------------------------------------------------------------------

# ---validation of a domain---
# BY PING
def domainValidation(list):
    output=[]
    for domain in list:
        print (domain)
        response=os.system("ping -n 1 " + domain)
        print (response)
        if response == 0:
            output.append(domain)
    return output


# BY USING HTTPLIB,URLLIB (also find the last destination URL)
def domainValidation2(list):
    final=[]
    original=[]
    ipSearch = re.compile(r'[0-2][0-5][0-5]\.[0-2][0-5][0-5]\.[0-2][0-5][0-5]\.[0-2][0-5][0-5]')
    for url in list:
        if (re.match(ipSearch,url)):
            response=os.system("ping -n 1 " + url)
            print (response)
            if response == 0 :
                domain=url
            else:
                domain=False
        else :
            domain = unshorten_url(url)

        if (domain):
            domain = urlparse(domain).netloc
            if (domain not in final):
                final.append(domain)
                original.append(url)
    output=pd.DataFrame({"original" : original,"destination" : final})
    return output

# --- CORRECTING BAD URL ---
def correcting(url):
    ipSearch = re.compile(r'[0-2][0-5][0-5]\.[0-2][0-5][0-5]\.[0-2][0-5][0-5]\.[0-2][0-5][0-5]')
    array=[]
    containsDot=False
    
    if (not urlparse(url).scheme) and ("//" not in url) and (not re.match(ipSearch,url)):
        url="http://" + url

    temp = urlparse(url)

    for i in temp.netloc:
        if i in (string.punctuation):
            array.append(i)
    if ("." in array):
        array=filter(lambda x: x !=".",array)
        containsDot=True
        
    punctCount = list(Counter(array).most_common())
    punctRank = list(Counter(array))
    
    if (array):
        netlocTemp=temp.netloc
        if punctCount[0][1]>1 :
            if (containsDot):
                netlocTemp=netlocTemp.replace(punctCount[0][0],"")
            else:
                netlocTemp=netlocTemp.replace(punctCount[0][0],".")
            temp=temp._replace(netloc=netlocTemp)
        else:
            if containsDot:
                netlocTemp=netlocTemp.replace(array[-1],"")
            else:
                netlocTemp=netlocTemp.replace(array[-1],".")
            temp=temp._replace(netloc=netlocTemp)
    
    if ("." in temp.netloc):
        temp = urlunparse(temp)
        # print (temp)
        return temp
    else:
        return False

#----------apply regex------------
def filterURL (list):
    output=[]
    seen=[]
    counter=1
    searcher = re.compile(r'(^|\W)(?!(https?:\/\/)?(\S+\.)*tokopedia\.com)((\S+(\.\S+)+)|(\S+([^a-z0-9\s\.]\S+)+))(\s|$)')
    ipSearch = re.compile(r'[0-2][0-5][0-5]\.[0-2][0-5][0-5]\.[0-2][0-5][0-5]\.[0-2][0-5][0-5]')
    isAlpha = re.compile(r'[A-Za-z]+')
    for msgOri in list.msg_reply:
        # messages1=msgOri
        messages1 = re.sub('[^A-Za-z0-9\.,:*/_&=\-?]+', ' ', msgOri)
        messages1 = re.sub('(\.{2,})'," ",messages1)
        messages1 = re.sub('(\?{2,})'," ",messages1)
        messages1 = messages1.replace(" dot ",".")
        messages1 = messages1.replace("(dot)",".")
        messages1 = messages1.replace("dotcom ",".com ")
        messages1 = messages1.lower()
        messages1 = searcher.findall(messages1)
        print (messages1)
        print (counter,end='')
        print (",",end='')
        for match in messages1:
            for match2 in match:
                if (re.match(isAlpha,match2)):
                    temp = match2.replace(" ","")
                    temp2 = re.sub('[^A-Za-z0-9]','',match2)
                    if (temp[:1]!='.'): # handle tokopedia regex problem
                        # ---del dot in first and last char---
                        if (temp[-1:]=="."):
                            temp=temp[:-1]
                        print (temp)
                        # --- numbers and IP rules ---
                        if (not temp2.isdigit() or (re.match(ipSearch,temp))): #not all number
                            print ("a")
                            if not any(match2 in s for s in seen):
                                print ("b")
                                if ((match2 !="") and (match2 !=" ")):
                                    print("c")
                                    if (temp[:3] != 'inv') and (temp[:3] != 'pym') and (temp[:3] != 'com'):
                                        print ("d")
                                        # ---transform bad url---
                                        temp=correcting(temp)
                                        if (temp):
                                            output.append(temp)
                                            seen.append(match2)
        counter+=1
    print("\n")
    output=pd.DataFrame(output)
    output.columns=['url']
    return output

# ------- domain metadata function -------
def findInfo(site):
    #Create Alexa URL
    urlget = "http://www.alexa.com/siteinfo/" + site

    #Get HTML
    html = url.urlopen(urlget)

    #Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html)
    souprank = BeautifulSoup(url.urlopen('http://data.alexa.com/data?cli=10&dat=snbamz&url='+site).read())
    try:
        globalRank=int(souprank.popularity['text'])
    except:
        globalRank = "-"
    try:
        domesticRank=int(souprank.country['rank'])
    except:
        domesticRank = "-"
    try:
        reachRank=int(souprank.reach['rank'])
    except:
        reachRank = "-"
    
    return globalRank,domesticRank,reachRank#,dailyviews


def getInfo(list):
    list['global_rank']=0
    list['domestic_rank']=0
    list['reach_rank']=0
    # urlList['daily_views']=0
    indexurl=0
    for match in list.destination:
        print (match)
        list['global_rank'][indexurl], list['domestic_rank'][indexurl],list['reach_rank'][indexurl] = findInfo(match)
        indexurl+=1



# -- MAIN --
def main():
    # ---VARIABLE---
    yesterday=yersterdayDate() # get date for query and file name
    # print (yesterday)
    # CHOOSE ONE:

    # 1. QUERY!!!!! UNCOMMENT TO RUN

    msg_unique = query(yesterday)

    
    # 2. get query dummy

    # -----------------------------------------
    # fileRead = 'sample_msg.csv' # sample 20-04-2016
    # # -----------------------------------------
    
    # # fileRead = 'msg_2016-04-30.csv'
    # msg_unique=pd.read_csv(fileRead) #only for test


    # BEGIN PROCESS:
    # --- FILTERING ---
    output=filterURL(msg_unique)
    filename1=('1_filteredURL{}.csv').format(yesterday)
    output.to_csv(filename1,index=False)

    # --- VALIDATION ---
    output=domainValidation2(output.url)
    filename2=('2_finalDomain{}.csv').format(yesterday)
    output.to_csv(filename2,index=False)

    # --- GET METADATA ---
    urlList=output
    getInfo(urlList)
    filename3=('3_domainData{}.csv').format(yesterday)
    urlList.to_csv(filename3, index=False)


if __name__=="__main__":
    main()