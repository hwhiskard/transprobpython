# -*- coding: utf-8 -*-
"""
Created on Sun May  2 06:43:53 2021

@author: WHI93526
"""
#%%
import numpy as np
import pandas as pd
import time
from src.transprob import transprob

examplePath = r"C:\Users\WHI93526\OneDrive - Mott MacDonald\Python\transprob\transprobpython\example data\FinancialRating.csv"

creditExample = pd.read_csv(examplePath,delimiter=',',header=0,parse_dates= [1])


creditExample["ID"] = creditExample["ID"].astype(np.int64)
creditExample["Date"] = creditExample["Date"].astype(np.datetime64)
creditExample["Rating"] = creditExample["Rating"].astype('str')


# Expected Output from Matlab:

'''
          0         1         2         3         4         5         6
0  0.895291  0.097147  0.000000  0.000000  0.007562  0.000000  0.000000
1  0.000000  0.861549  0.000000  0.000000  0.138451  0.000000  0.000000
2  0.000000  0.000000  0.9291  0.036201  0.000000  0.031285  0.003415
3  0.000000  0.000000  0.093907  0.904298  0.000000  0.001677 0.000118
4  0.000000  0.000000  0.000000  0.000000  1.000000  0.000000  0.000000
5 0.000000 0.000000  0.159528  0.003296 0.000000  0.670936  0.166240
6 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000  1.000000
'''

startTime = time.time()

transitionProbabilityShort = transprob(creditExample[0:10],DateFormatString= "%d-%b-%Y",startDate= None,endDate= '10-Nov-2015')



print(creditExample[0:10])
print(transitionProbabilityShort)
executionTime = (time.time() - startTime)
print('Execution time in for test matrix (s): ' + str(executionTime))


#%%

# Expected Output from Matlab:

'''
          0         1         2         3         4         5             6         7
0  0.949729  0.018788  0.000745  0.000389  0.003270  0.026603  1.2e-05  0.000465
1  0.030025  0.953244  0.011067  0.000025  0.001058  0.004318  2e-06  0.000262
2  0.006028  0.045172  0.947244  0.000006  0.000264  0.001276  1e-06  0.000009
3  0.000710  0.000032  0.000005  0.900166  0.055817  0.006133  1.9105e-02  0.018032
4  0.004266  0.000799  0.000155  0.025773  0.918504  0.043381  2.070733e-03  0.005051
5  0.031603  0.001268  0.000137  0.002868  0.023968  0.938451  3.84e-04  0.001323
6  0.000068  0.000006  0.000001  0.038265  0.012296  0.002155  0.83591  0.111298
7  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  1.000000
'''

startTime = time.time()

transitionProbabilityFull = transprob(creditExample,DateFormatString= "%d-%b-%Y",startDate= None,endDate= '10-Nov-2015')


print(transitionProbabilityFull)

executionTime = (time.time() - startTime)
print('Execution time in for full matrix (s): ' + str(executionTime))

# %%
