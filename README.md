
# Transprob Python

After using Markov Chains, I realised there was no python package to calculate Transition probability. This is something easily available in Matlab, so I recreated it in Python.
 
Probabilities are calculated using the Duration algorithm
## Getting Started

The source code for transprob sits in src/ transprob.py 

To run call trans_prob with the following variables

`data` - nx3 table with columns as Id, Date and State, in that order e.g:

ID| Date |Rating |
---| --- | --- |
 10283 | 10-Nov-1984 | CCC |
10283 | 12-May-1986 | B |
10283 | 29-Jun-1988 |CCC |


`date_format_string` Denotes the date format of input data, e.g. "%d-%b-%Y" for '10-Nov-2015'

`start_date` Optional parameter to limit data on start date

`end_date` Optional parameter to limit data on end date

### Examples
An example can be found in transprob_example

```python
import numpy as np
import pandas as pd
import time

from src.transprob import trans_prob

examplePath = "example_data\FinancialRating.csv"

creditExample = pd.read_csv(examplePath, delimiter=',', header=0, parse_dates=[1])

creditExample["ID"] = creditExample["ID"].astype(np.int64)
creditExample["Date"] = creditExample["Date"].astype(np.datetime64)
creditExample["Rating"] = creditExample["Rating"].astype('str')

startTime = time.time()

transitionProbabilityShort = trans_prob(creditExample[0:10], date_format_string="%d-%b-%Y",
                                        start_date=None, end_date='10-Nov-2015')
```
## Acknowledgements
This library takes inspiration and applies the same methodology as the MATLAB transprob function 
 - https://www.mathworks.com/help/finance/transprob.html
 
## Disclaimer

This has been created as a personal project, so any results should be seperately validated.
