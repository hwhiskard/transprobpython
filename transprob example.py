# -*- coding: utf-8 -*-
"""
Created on Sun May  2 06:43:53 2021

@author: WHI93526
"""
#%%
import numpy as np
import pandas as pd
from src.transprob import transprob

examplePath = r"C:\Users\WHI93526\OneDrive - Mott MacDonald\Python\transprob\transprobpython\example data\FinancialRating.csv"

creditExample = pd.read_csv(examplePath,delimiter=',',header=0,parse_dates= [1])


creditExample["ID"] = creditExample["ID"].astype(np.int64)
creditExample["Date"] = creditExample["Date"].astype(np.datetime64)
creditExample["Rating"] = creditExample["Rating"].astype('str')

#print(creditExample.shape[1])
transcounts = transprob(creditExample[0:9],startDate= None,endDate= '10-Nov-2015')

print(transcounts)

transcounts = transprob(creditExample,startDate= None,endDate= '10-Nov-2015')

print(transcounts)


# %%
