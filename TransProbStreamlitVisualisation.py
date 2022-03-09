import streamlit as st
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
from src.transprob import transprob

st.title('Transition Probability Matrix')
st.write('Calculates a transition probability matrix using Duration algorithm. Enter start date, end date and length of dataset in the side bar')
st.write(' ')



csvFile =st.file_uploader('Upload CSV input','csv')

if csvFile is not None:
    creditExample = pd.read_csv(csvFile,delimiter=',',header=0,parse_dates= [1])
    


    creditExample["ID"] = creditExample["ID"].astype(np.int64)
    creditExample["Date"] = creditExample["Date"].astype(np.datetime64)
    creditExample["Rating"] = creditExample["Rating"].astype('str')

    st.write('Here is an example of the input data')
    st.write(creditExample[0:10])

    minDate = creditExample["Date"].min()
    maxDate = creditExample["Date"].max()
    maxLength = len(creditExample)
    # Create row, column, and value inputs
    st.sidebar.write('Define Start Date, first date is: ', str(minDate))
    startdate = st.sidebar.date_input('start date', datetime.date(1980,1,1))
    st.sidebar.write('Define End Date, last date is: ', str(maxDate))
    enddate = st.sidebar.date_input('end date', datetime.date(2010,1,1))
    st.sidebar.write('Define Data Input length, max length is ',maxLength)
    datalength = st.sidebar.number_input('number of rows: ', 500)


    st.subheader('Calculate Transition Matrix')
    st.write('')
    runButton = st.button('Click here to calculate')

    if runButton:
        transitionProbabilityShort = transprob(creditExample[0:datalength],DateFormatString= "%Y-%m-%d",startDate= str(startdate),endDate= str(enddate))
        heatmap = sns.heatmap(transitionProbabilityShort, cmap ='RdYlGn', linewidths = 0.80, annot = True)
        st.pyplot()