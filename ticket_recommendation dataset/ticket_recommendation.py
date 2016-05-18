
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

#sklearn
# from sklearn.cross_validation import train_test_split
from sklearn import metrics

from custom_transformer import ColumnSelector, ApplyFunction, ColumnTransform, PrintThat
import custom_transformer as ct


# In[2]:

dataset=pd.read_csv("ticket_all_lev.csv")


# In[3]:

dataset=dataset[np.isfinite(dataset['tpl_id'])]


# In[4]:

datasetSorted = dataset.sort_values(["tpl_id"],ascending=[1])


# In[5]:

ds_X = datasetSorted.ix[:,["ticket_title","ticket_msg","ticket_category","tpl_id"]]


# In[6]:

ds_y = datasetSorted["tpl_id"]


# In[7]:

XTrain,XTest,yTrain,yTest = ct.train_test_split(ds_X,ds_y,test_size=0.5,random_state=7)


# In[8]:

pipe = ct.Pipeline([
                ("features", ct.FeatureUnion([
                            ("message", ct.Pipeline([
                                        ("select_text", ColumnSelector("ticket_msg")),       
#                                         ("debug1", ct.PrintThat()),
                                        ("preprocessing_input", ApplyFunction(ct.preprocess_input)),
                                        ("delete_link", ApplyFunction(ct.clean_link)),
                                        ("clean_text", ApplyFunction(ct.clean_symbol)),
                                        ("hashing_vectorizer", ct.HashingVectorizer()),
                                    ])
                            ),
                            ("title", ct.Pipeline([
                                        ("select_text", ColumnSelector("ticket_title")),                                        
                                        ("preprocessing_input", ApplyFunction(ct.preprocess_input)),
                                        ("take_link", ApplyFunction(ct.take_link)),
                                        ("clean_link", ApplyFunction(ct.clean_symbol)),
                                        ("hashing_vectorizer", ct.HashingVectorizer()),
#                                         ("debug2", PrintThat())
                                    ])
                            ),
                            ("category", ct.Pipeline([
                                        ("select_text", ColumnSelector("ticket_category")), 
                                        ("to_array", ColumnTransform()),
                                        ("debug3", PrintThat()),
                                    ]),
                            ),
 
                        ], transformer_weights={"message":1, "title":1, "category": 1})
                ),
                ("classifier", ct.LinearSVC())

            ])


# In[11]:

start_time = time.time()
print type(XTrain)
print type(yTrain)

pipe.fit(XTrain, yTrain)

p_time = time.time() - start_time
print("predict time is {}".format(p_time))


# In[13]:

y_predict=pipe.predict(XTest)


# In[14]:

# y_predict


# In[ ]:

#     cross validation
start_time = time.time()
cv_score = ct.cross_val_score(pipe, XTrain, yTrain, cv=5)
cv_time = time.time() - start_time
print("predict time is {}".format(cv_time))

print("CV accuracy: %0.2f (+/- %0.2f)" % (cv_score.mean(), cv_score.std() * 2))

# test data
print ("Avg precision(micro) = %f" % metrics.precision_score(yTest, y_predict, average='micro'))
print ("Avg recall(micro) = %f" % metrics.recall_score(yTest, y_predict, average='micro'))
print ("Avg precision(macro) = %f" % metrics.precision_score(yTest, y_predict, average='macro'))
print ("Avg recall(macro) = %f" % metrics.recall_score(yTest, y_predict, average='macro'))
