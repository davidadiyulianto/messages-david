
# coding: utf-8

# In[10]:

import pandas as pd
pd.options.display.max_rows = 999
import numpy as np
import time
import datetime as dt
import os
import re
import sys
import string
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from sklearn import metrics

from custom_transformer import ColumnSelector, ApplyFunction, ColumnTransform, PrintThat
import custom_transformer as ct
from sklearn.metrics import accuracy_score


# define functions
def delete_symbol(x):
    remove_char = re.sub('[^A-Za-z0-9]+', "", str(x))
    words = remove_char.split()

    return(" ".join(words).lower()) 

def mostOccurence(array):
    wordfreq = []
    wordlist = []
    allwordlist = []
    a = 1
    for s in (array):
#         print (s)
        print ("{}/{}".format(a,len(array)))
        s=s.lower()
        # s = delete_symbol(s)
        wordListTemp = s.split()
        for w in wordListTemp:
            if ((w[:3] != 'inv') and (len(w)!=2)):
                if (w):
                    w=delete_symbol(w)
                    allwordlist.append(w)
                    if (w not in wordlist) and (not w.isdigit()):
                        wordlist.append(w.lower())
        a+=1
    
    for w in wordlist :
        wordfreq.append(allwordlist.count(w))
        
    return wordlist,wordfreq

# --------------------------------

# minimum data each label
dataCount=15

# In[2]:
print ("importing dataset ...")
dataset = pd.read_csv("ticket_all_lev.csv")

ds_clean = pd.DataFrame(columns=["ticket_msg","ticket_title","tpl_id"])
ds_clean["ticket_msg"] = dataset["ticket_msg"]
ds_clean["ticket_title"] = dataset["ticket_title"]

# cleaning dataset
print ("copying dataset ...")
for i in range (0,len(dataset["tpl_id"])):
    if pd.notnull(dataset["tpl_id"][i]):
        ds_clean["tpl_id"][i] = dataset["tpl_id"][i]
    else :
        ds_clean["tpl_id"][i] = dataset["highest_tpl_id"][i]


ds_clean["tpl_id"] = ds_clean["tpl_id"].astype('int')

ds_clean = ds_clean[pd.notnull(ds_clean['ticket_msg'])]
ds_clean = ds_clean[pd.notnull(ds_clean['ticket_title'])]
ds_clean = ds_clean[pd.notnull(ds_clean['tpl_id'])]

# --- count each label ---
# completing data set for cross validation
print ("completing dataset for cross validation")
count = ds_clean['tpl_id'].value_counts().sort_values(ascending=1)
count = pd.DataFrame(count)

count.columns = ["count"]

count=count[(count["count"] < dataCount)] # get data with data < 10 for each label

# --- add data for each label ---
a = 0
temp = pd.DataFrame()
toAppend = pd.DataFrame()
for i in count["count"]:
    n = 0
    print (i , count.index.values[a])
    abc = ds_clean[(ds_clean['tpl_id'] == count.index.values[a])]
    for j in range (i,dataCount):
        temp=abc.sample(n=1)
        toAppend=pd.concat([toAppend,temp],ignore_index=True)
    a+=1

# In[4]:

ds_clean = pd.concat([ds_clean,toAppend],ignore_index=True)

# ------------ word count data for stop words --------------
# - option #01:

# print ("making stop words list")
# wordList = pd.DataFrame(columns = ["word","count"])
# wordList["word"],wordList["count"] = mostOccurence(ds_clean["ticket_msg"])

# stopsList = (wordList.sort_values(["count"],ascending=0))

# stops = list(stopsList["word"].head(200))
# filename = 'word_list.csv'
# stopsList.to_csv(filename,index = False)

# - option #02 (from csv):

print ("importing stops list ...")
stopsList = pd.read_csv("word_list.csv")
# stops = list(stopsList["word"].tail(15000))
stops = stopsList[(stopsList["count"]<5)]
stops = list(stops["word"])

# - option #03:

stopsList2 = pd.read_csv("stopwordID.csv")
stops2 = list(stopsList2["kata"])
# stops = stops2


# - option #04 (combine #02 and #03):
stops=stops.append(stops2)

ds_X = ds_clean
ds_y = ds_clean["tpl_id"]
XTrain,XTest,yTrain,yTest = ct.train_test_split(ds_X,ds_y,test_size=0.2,random_state=42)


# In[8]:
stops1 = ["kredit", "order", "invoice", "tagihan", "dana", "proses","kurir","pengiriman","gojek","penjual","pembeli","belanja","toko"]

# ngram_vectorizer = ct.CountVectorizer(ngram_range=(1, 4), analyzer='char')
pipe = ct.Pipeline([
                ("features", ct.FeatureUnion([
                            ("message", ct.Pipeline([
                                        ("select_text", ColumnSelector("ticket_msg")),       
#                                         ("debug1", ct.PrintThat()),
                                        ("preprocessing_input", ApplyFunction(ct.preprocess_input)),
                                        ("clean_symbol", ApplyFunction(ct.clean_symbol)),
                                        ("hashing_vectorizer", ct.HashingVectorizer(stop_words=stops)),
                                    ])
                            ),
                            ("title", ct.Pipeline([
                                        ("select_text", ColumnSelector("ticket_title")),                                        
                                        ("preprocessing_input", ApplyFunction(ct.preprocess_input)),
                                        ("clean_symbol", ApplyFunction(ct.clean_symbol)),
                                        ("hashing_vectorizer", ct.HashingVectorizer(stop_words=stops2)),
#                                         ("debug2", PrintThat())
                                    ])
                            ),
                            ("ngram", ct.Pipeline([
                                        ("select_text", ColumnSelector("ticket_title")), 
                                        ("preprocessing_input", ApplyFunction(ct.preprocess_input)),
                                        ("clean_symbol", ApplyFunction(ct.clean_symbol)),
                                        ("ngram_vectorizer",ct.CountVectorizer(ngram_range=(2,2), analyzer='word')),
                                        # ("debug3", PrintThat()),
                                    ]),
                            ),
 
                        ], transformer_weights={"message":1, "title":1, "ngram": 1})
                ),
                ("classifier", OneVsRestClassifier(ct.LinearSVC(random_state=0)))

            ])


# In[11]:

start_time = time.time()

print ("fit")
pipe.fit(XTrain, yTrain)

p_time = time.time() - start_time
print("predict time = {}".format(p_time))


# In[13]:

y_predict=pipe.predict(XTest)


#     cross validation
start_time = time.time()
cv_score = ct.cross_val_score(pipe, XTrain, yTrain, cv=5)
cv_time = time.time() - start_time
print("predict time = {}".format(cv_time))

print("CV accuracy: %0.2f (+/- %0.2f)" % (cv_score.mean(), cv_score.std() * 2))

# test data
print ("Avg precision(micro) = %f" % metrics.precision_score(yTest, y_predict, average='micro'))
print ("Avg recall(micro) = %f" % metrics.recall_score(yTest, y_predict, average='micro'))
print ("Avg precision(macro) = %f" % metrics.precision_score(yTest, y_predict, average='macro'))
print ("Avg recall(macro) = %f" % metrics.recall_score(yTest, y_predict, average='macro'))

print ("Accuracy score {}".format(accuracy_score(yTest,y_predict)))


# Decision Function

probabilities = pipe.decision_function(XTest)
probabilities = pd.DataFrame(probabilities,columns=pipe.classes_)
print (len(probabilities.columns))

output = pd.DataFrame(columns=['#1','#2','#3'])
print (len(probabilities))
for i in range (0,len(probabilities)):
    temp = probabilities.iloc[i]
    temp = temp.sort_values(ascending=0)
    highestProb = list(temp[:3].index)
    dftemp=pd.DataFrame({'#1':[highestProb[0]],'#2':[highestProb[1]],'#3':[highestProb[2]]})
    output=pd.concat([output,dftemp],ignore_index=True)

output["real"]=yTest.values

correct1=0
correct2=0
correct3=0
conclusion=0
for i in range (0,len(output)):
    if (output.iloc[i]["#1"] == output.iloc[i]["real"]):
        correct1+=1
        conclusion+=1
    elif (output.iloc[i]["#2"] == output.iloc[i]["real"]):
        correct2+=1
        conclusion+=1
    elif (output.iloc[i]["#3"] == output.iloc[i]["real"]):
        correct3+=1
        conclusion+=1


firstchoiceaccuracy = (float(correct1))/(float(len(yTest)))
totalaccuracy = (float(conclusion))/(float(len(yTest)))
print (firstchoiceaccuracy)
print (totalaccuracy)