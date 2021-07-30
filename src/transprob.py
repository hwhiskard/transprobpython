# -*- coding: utf-8 -*-
"""
Created on Mon May  3 07:35:45 2021

@author: WHI93526
"""

import numpy as np
import pandas as pd
from scipy.linalg import expm
from itertools import product
import datetime

def transprob(data,DateFormatString,startDate = None,endDate = None):
    
    '''
    Transition probability function. Calculates probabilities using Duration algorithm   
    Inputs:-  nx3 table with columns as Id, Date and State, e.g:
                ID,Date,Rating
                10283,10-Nov-1984,CCC
                10283,12-May-1986,B
                10283,29-Jun-1988,CCC
                10283,12-Dec-1991,D
                13326,09-Feb-1985,A
                13326,24-Feb-1994,AA
                13326,10-Nov-2000,BBB
                14413,23-Dec-1982,B
           - Optional input for start and end date to limit calculations.
           - String denoting the date format, e.g. "%d-%b-%Y" for '10-Nov-2015'
    Output: 
        
    '''
    #-------------- Check that Dataset is in desired format ------------------------------------------#
    
    
    
    assert (data.shape[1] == 3), "Input data must only have 3 columns"
    
    data.columns = [0,1,2]
    
    assert (pd.api.types.is_datetime64_any_dtype(data[1])), "Date Column must be in datetime64 format"
    
    
    print('Transprob input data checks complete')
    
    def timer(fn):
        from time import perf_counter
        
        def inner(*args, **kwargs):
            start_time = perf_counter()
            to_execute = fn(*args, **kwargs)
            end_time = perf_counter()
            execution_time = end_time - start_time
            print('{0} took {1:.8f}s to execute'.format(fn.__name__, execution_time))
            return to_execute
        
        return inner

    
    #-------------- Define functions ------------------------------------------#
    @timer
    def CalulateTotalTimePeriod(startDate,endDate):
    
        """
        Assign start and end date if not specified. Then calculate time range.                
        """

        if startDate == None:
            
            startDate = data[1].min()
        else:
            startDate = datetime.datetime.strptime(startDate, DateFormatString)   

        if endDate == None:
            
            endDate = data[1].max()
        else:
            endDate = datetime.datetime.strptime(endDate, DateFormatString) 
        timePeriod = endDate - startDate
        
        return startDate,endDate,timePeriod
    
    @timer
    def FilterDatawithDates(Data,startDate,endDate):
        
        '''
        Filters the dataset to be between the start and end dates
        '''
        
        Data = Data[(Data[1] >= startDate) & (Data[1] <= endDate)]
        
        return Data

    @timer
    def TimeSpentInRating(data,endDate):
        
        """      
        Calculates the total time spent in a single code. First calculated on an Id level basis and then aggregated
        """
        
        TotalTimeinState = pd.DataFrame(columns = ['ID','State','TimeinState'])
        IDList = data[0].unique()
        # Perform individually for every Id
        for ID in IDList:
        
            dataID = data[data[0] == ID]
            dataID = dataID.sort_values(by = 1, ascending = True)
            #dataID = dataID.reset_index(drop = True)
            dataID['TimeinState'] = 0
            dataID['TimeinState'] = dataID['TimeinState'].astype('timedelta64[ns]')
            
            dataIdShift = dataID.shift(periods = -1)
            dataID['TimeinState'] =   dataIdShift[1] - dataID[1]
            
            dataID.loc[dataID.index[-1],'TimeinState'] = endDate - dataID.loc[dataID.index[-1],1]
            
            dataID['TimeinState'] = dataID['TimeinState'].dt.days.astype('int32')
            TimeInState = dataID.groupby([0,2])['TimeinState'].sum()
            
            TimeInState = TimeInState.reset_index()
            TimeInState.columns = ['ID','State','TimeinState']
            
            TotalTimeinState = TotalTimeinState.append(TimeInState,ignore_index=True)
        

        TotalTimeinState = TotalTimeinState.groupby(['State'])['TimeinState'].sum()
        
        TotalTimeinState = TotalTimeinState / 365.25 # Convert to Years
        TotalTimeinState = TotalTimeinState.reset_index()

        return TotalTimeinState
    
    
    
    @timer
    def IDTransitionCount(data):
        
        
        """
        
        Counts the number of transitions in the time period.
        Does not include moves of one state to the Same (e.g. 1 > 1) i.e not moving. 
        
        
        """
        IDList = data[0].unique()
        transcounts = pd.DataFrame(columns = ['ID','State1','State2','Count'])
        for ID in IDList:
            
            dataID = data[data[0] == ID]
            dataID = dataID.sort_values(by = 1, ascending = True)
            dataID = dataID.reset_index(drop = True)
            
            # Filter out values that repeat. E.g. B >> B >> C, becomes B >> C
            dataID[2] = dataID[dataID[2] != dataID.loc[:,2].shift(1)][2]
            dataID = dataID[pd.notnull(dataID[2])]
            dataID = dataID.reset_index(drop = True)
                
            count = 0

            DataSum = dataID
            DataSum[3] = dataID[2].shift(periods = -1)
           
            DataGrup = DataSum.groupby([0,2,3])[1].count()
            DataGrup = DataGrup.reset_index(drop = False)
            DataGrup.columns = ['ID','State1','State2','Count']
            #print(DataGrup)  
            
            transcounts = transcounts.append(DataGrup,ignore_index=True)
            # Could be simplified using shift
            # for i in range(0,dataID.shape[0]-1,1):
                
                

            #     state1 = dataID.loc[i,2]
            #     state2 = dataID.loc[i+1,2]
                
            #     if ((transcounts['ID'] == ID) & (transcounts['State1'] == state1) &  (transcounts['State2'] == state2)).any():
                    
            #         # Adds to the count if the state transition has already occurred
                    
            #         index = transcounts[(transcounts['ID'] == ID) & (transcounts['State1'] == state1) &  (transcounts['State2'] == state2)].index
            #         count = transcounts.loc[index,'Count'].max()
                    
            #         transcounts.loc[index,'Count'] = count +1
            #     else:    
                    
            #         # If transition has not occurred record with count = 1 created
                    
            #         tCount = pd.DataFrame({'ID':ID,'State1':dataID.loc[i,2],'State2':dataID.loc[i+1,2],'Count':1},index = [0])
            #         transcounts = transcounts.append(tCount,ignore_index=True)    
                
        
        
        return transcounts

    @timer
    def GroupTransitionCounts(transcounts):
        
        '''
        Group counts and fill in non occuring transitions 
        '''
        
        totaltransCounts = transcounts.groupby(['State1','State2'])['Count'].sum()
        totaltransCounts = totaltransCounts.reset_index()
        
        # Find Non Occurring Transitions and add them to the transition matrix
        uniqueStates = data[2].unique()
        
        allStateCombinations = pd.DataFrame(product(uniqueStates,uniqueStates),columns = ['State1','State2'])
        allStateCombinations['Count'] = 0
        allStateCombinations = allStateCombinations[allStateCombinations['State1'] != allStateCombinations['State2']]
        totaltransCounts = totaltransCounts.append(allStateCombinations,ignore_index=True)
        totaltransCounts['Duplicated'] = totaltransCounts.loc[:,['State1','State2']].duplicated()

        totaltransCounts = totaltransCounts[totaltransCounts['Duplicated'] == False]
        totaltransCounts = totaltransCounts.sort_values(by = ['State1','State2'])
        
        totaltransCounts = totaltransCounts.drop(['Duplicated'],axis = 1)
        return totaltransCounts  
     
      
    @timer
    def countperTime(totaltransCounts,TotalTimeInRating):
        
        '''
        Divides counts of transitions by total time spent in the State.
        '''

        countperTime = pd.merge(totaltransCounts,TotalTimeInRating, left_on=['State1'], right_on = ['State'])
        countperTime['countperTime'] = countperTime['Count'] / countperTime['TimeinState']
        
        countperTime = countperTime.drop(['Count','State','TimeinState'],axis = 1)
        countperTime.columns = ['State1','State2','Probability']
        countperTime['Probability'] = countperTime['Probability'].fillna (0) # Fill any fields with Nan with 0. Accounts for probabilities that have 0 time in state

        return countperTime
    
    @timer
    def calculateNonTransitionProbability(countperTime):
        
        '''
        Calculate the probability of staying in state and create full transition probability table
        '''
        
        sumPerState = countperTime.groupby('State1')['Probability'].sum()
        sumPerState = sumPerState.reset_index()
        sumPerState['State2'] = sumPerState['State1']
        sumPerState['NonTranProb'] =  - sumPerState['Probability']
        sumPerState = sumPerState.drop('Probability',axis = 1)
        sumPerState.columns = ['State1','State2','Probability']
       
        transitionProbability = countperTime.append(sumPerState,ignore_index=True)
                       
        return transitionProbability
    #-------------- Call functions ------------------------------------------#
    


    startDate,endDate,timePeriod = CalulateTotalTimePeriod(startDate,endDate)
     
    data = FilterDatawithDates(data,startDate,endDate)
    
    TotalTimeInRating = TimeSpentInRating(data,endDate)
    
    transcounts = IDTransitionCount(data)
    
    totaltransCounts = GroupTransitionCounts(transcounts)
    
    countperTimeA = countperTime(totaltransCounts,TotalTimeInRating)
    
    transitionProbability = calculateNonTransitionProbability(countperTimeA)
    
    #-------------- Test Output dataset ------------------------------------------#

    transprobOut = pd.pivot_table(transitionProbability,values = 'Probability',index = 'State1',columns = 'State2')
    transprobOut = pd.DataFrame(expm(np.array(transprobOut))) 
  



    # Check that the total probability of transitions from a state is 1 
    for _,row in transprobOut.iterrows():
 
        assert abs(row.sum()) - 1 < 0.0001, "Output state probabilities do not sum to 1"

    return transprobOut