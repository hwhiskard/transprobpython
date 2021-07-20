# -*- coding: utf-8 -*-
"""
Created on Mon May  3 07:35:45 2021

@author: WHI93526
"""

import numpy as np
import pandas as pd
from itertools import product

def transprob(data,startDate = None,endDate = None):
    
    '''
    Transition probability function. Calculates probabilities using Duration algorithm   
    Inputs:-  nx3 table with columns as Id, Date and State
           - Optional input for start and end date to limit calculations.
           - 
    Output: 
        
    '''
    #-------------- Test Dataset is in desired format ------------------------------------------#
    
    assert (data.shape[1] == 3), "Input data must only have 3 columns"
    
    assert (pd.api.types.is_datetime64_any_dtype(data[1])), "Date Column must be in datetime64 format"
    
    
    print('Transprob checks complete')
    
    
    #-------------- Define functions ------------------------------------------#
    
    def CalulateTotalTimePeriod(startDate,endDate):
    
        """
        Assign start and end date if not specified. Then calculate time range.                
        """
    
        if startDate == None:
            
            startDate = data[1].min()
            
        if endDate == None:
            
            endDate = data[1].max()
        
        timePeriod = endDate - startDate
        
        return startDate,endDate,timePeriod

    def FilterDatawithDates(Data,startDate,endDate):
        
        '''
        Filters the dataset to be between the start and end dates
        '''
        
        Data = Data[(Data[1] >= startDate) & (Data[1] <= endDate)]
        
        return Data

    def TimeSpentInRating(data,endDate):
        
        """      
        Calculates the total time spent in a single code. First calculated on an Id level basis and then aggregated
        """
        
        TotalTimeinState = pd.DataFrame(columns = ['ID','State','TimeinState'])
        for ID in data[0].unique():
        
            dataID = data[data[0] == ID]
            dataID = dataID.sort_values(by = 1, ascending = True)
            dataID = dataID.reset_index(drop = True)
            dataID['TimeinState'] = 0
            dataID['TimeinState'] = dataID['TimeinState'].astype('timedelta64[ns]')
            for idx, row in dataID.iterrows():
                
                if idx != dataID.index.max():
                
                    dataID.loc[idx,'TimeinState'] = dataID.loc[idx+1,1] - dataID.loc[idx,1] 
                
                else:
                     dataID.loc[idx,'TimeinState'] = endDate - dataID.loc[idx,1] 
                
            TimeInState = dataID.groupby([0,2])['TimeinState'].sum()
            TimeInState = TimeInState.reset_index()
            TimeInState.columns = ['ID','State','TimeinState']
            
            TotalTimeinState = TotalTimeinState.append(TimeInState,ignore_index=True)
        

        TotalTimeinState = TotalTimeinState.groupby(['State'])['TimeinState'].sum()
        #TotalTimeinState.columns = ['State','TimeinState']
        
        TotalTimeinState = TotalTimeinState / pd.Timedelta('365 days') # Convert to Years
        TotalTimeinState = TotalTimeinState.reset_index()

        return TotalTimeinState
    
    
    
    
    def IDTransitionCount(data):
        
        
        """
        
        Counts the number of transitions in the time period.
        Does not include moves of one state to the Same (e.g. 1 > 1) i.e not moving. 
        
        
        """
        
        transcounts = pd.DataFrame(columns = ['ID','State1','State2','Count'])
        
        for ID in data[0].unique():
            
            dataID = data[data[0] == ID]
            dataID = dataID.sort_values(by = 1, ascending = True)
            dataID = dataID.reset_index(drop = True)
            
            # Filter out values that repeat. E.g. B >> B >> C, becomes B >> C
            dataID[2] = dataID[dataID[2] != dataID.loc[:,2].shift(1)][2]
            dataID = dataID[pd.notnull(dataID[2])]
            dataID = dataID.reset_index(drop = True)
            
            
                    
                    
            
            count = 0
            # Could be simplified using shift
            for i in range(0,dataID.shape[0]-1,1):
                
                state1 = dataID.loc[i,2]
                state2 = dataID.loc[i+1,2]
                
                if ((transcounts['ID'] == ID) & (transcounts['State1'] == state1) &  (transcounts['State2'] == state2)).any():
                    
                    # Adds to the count if the state transition has already occurred
                    
                    index = transcounts[(transcounts['ID'] == ID) & (transcounts['State1'] == state1) &  (transcounts['State2'] == state2)].index
                    count = transcounts.loc[index,'Count'].max()
                    
                    transcounts.loc[index,'Count'] = count +1
                else:    
                    
                    # If transition has not occurred record with count = 1 created
                    
                    tCount = pd.DataFrame({'ID':ID,'State1':dataID.loc[i,2],'State2':dataID.loc[i+1,2],'Count':1},index = [0])
                    transcounts = transcounts.append(tCount,ignore_index=True)    
                
        
        
        
        
        return transcounts

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
     
      
    
    def countperTime(totaltransCounts,TotalTimeInRating):
        
        '''
        Divides counts of transitions by total time spent in the State.
        '''

        countperTime = pd.merge(totaltransCounts,TotalTimeInRating, left_on=['State1'], right_on = ['State'])
        countperTime['countperTime'] = countperTime['Count'] / countperTime['TimeinState']
        countperTime = countperTime.drop(['Count','State','TimeinState'],axis = 1)
        countperTime.columns = ['State1','State2','Probability']
        return countperTime
    
    def calculateNonTransitionProbability(countperTime):
        
        '''
        Calculate the probability of staying in state and create full transition probability table
        '''
        
        sumPerState = countperTime.groupby('State1')['Probability'].sum()
        sumPerState = sumPerState.reset_index()
        sumPerState['State2'] = sumPerState['State1']
        sumPerState['NonTranProb'] = 1 - sumPerState['Probability']
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
    
    
    return transitionProbability