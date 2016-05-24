# import library
import pandas as pd
import datetime as dt
import numpy as np
import re
import time
import string

from sklearn.cross_validation import train_test_split

import sys
#import db_common as db

import glob
import os

from IPython.display import clear_output

from sklearn import metrics

from collections import Counter

from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer, TfidfTransformer
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import scale, label_binarize
from sklearn.svm import LinearSVC, LinearSVR, SVC
from sklearn.externals import joblib 

from sklearn.base import TransformerMixin, BaseEstimator
import string


# selecting column
class ColumnSelector(BaseEstimator, TransformerMixin):
    def __init__(self, column):
        self.column = column
    def fit(self, X, *args):
        return self
    def transform(self, X, *args):
        return X[self.column]

# import custom transformer
class ApplyFunction(BaseEstimator, TransformerMixin):
	def __init__(self, function, is_feature=False):
		self.function = function
		self.is_feature = is_feature

	def fit(self, X, *args):
		return self

	def transform(self, X, *args):
		series = X.apply(self.function)
		if self.is_feature:
			return X[:, None]
		else:
			return series
        
# make the column into array with y dimension
class ColumnTransform(BaseEstimator, TransformerMixin):
#     def __init__(self, column):
#         self.column = column

    def fit(self, X, *args):
        return self

    def transform(self, X, *args):
        return X[:, None]

#make a custom transformer that print output 
class PrintThat(BaseEstimator, TransformerMixin):
    def fit(self, *args):
        return self
    
    def transform(self, X, *args):
        print X
        print type(X)
        #print len(X)
        return X
    
    
    
# import regex function

# clean link
def clean_link(x):
    remove_char = re.sub(r"""[-a-zA-Z0-9@:%$-/:-?{-~!"^_`\[\]_\+~#=]{2,256}[$-/:-?{-~!"^_`\[\]][a-z]{2,6}\b([-a-zA-Z0-9@:%_\+$-/:-?{-~!"^_`\[\]~#?&//=]*)""", '', str(x))
    words = remove_char.split()

    return(" ".join(words).lower()) 

def take_link(x):
    select_char = re.finditer(r"""[-a-zA-Z0-9@:%$-/:-?{-~!"^_`\[\]_\+~#=]{2,256}[$-/:-?{-~!"^_`\[\]][a-z]{2,6}\b([-a-zA-Z0-9@:%_\+$-/:-?{-~!"^_`\[\]~#?&//=]*)""", str(x))

    result = []
    for match in select_char:
        result.append(match.group())

    return(" ".join(result).lower()) 

def clean_symbol(x):
    remove_char = re.sub('[^A-Za-z0-9]+', " ", str(x))
    words = remove_char.split()

    return(" ".join(words).lower()) 

def count_special_char(x):
    special_char = len([c for c in x if c in string.punctuation])
    return special_char

# other_function
def contain_link(x):
    if x == "":
        return 0
    else:
        return 1


def preprocess_input(line):
    if line is None:
        line = ""
    return " ".join(filter(lambda x: x in string.printable, line).split())

def clean_words(x,array):
    x=str(x.lower())
    words = x.split()
    words = [x for x in words if x in array]
    return(" ".join(words).lower())
