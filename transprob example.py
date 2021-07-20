# -*- coding: utf-8 -*-
"""
Created on Sun May  2 06:43:53 2021

@author: WHI93526
"""
import numpy as np
import pandas as pd
from transprob import *

examplePath = r'C:\Users\WHI93526\OneDrive - Mott MacDonald\Python\transprob\creditRatingExample.csv'

creditExample = pd.read_csv(examplePath,delimiter=',',header=None,parse_dates= [1])
print(creditExample)

creditExample[0] = creditExample[0].astype(np.int64)
creditExample[1] = creditExample[1].astype(np.datetime64)
creditExample[2] = creditExample[2].astype('str')


transcounts = transprob(creditExample)
#print(transcounts)
print(pd.pivot_table(transcounts,values = 'Probability',index = 'State2',columns = 'State1'))

