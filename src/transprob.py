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


# -------------- Define functions ------------------------------------------#
@timer
def calculate_total_time_period(data, start_date, end_date, date_format_string):
    """
    Assign start and end date if not specified. Then calculate time range.
    """

    if start_date is None:
        start_date = data[1].min()
    else:
        start_date = datetime.datetime.strptime(start_date, date_format_string)

    if end_date is None:
        end_date = data[1].max()
    else:
        end_date = datetime.datetime.strptime(end_date, date_format_string)

    time_period = end_date - start_date

    return start_date, end_date, time_period


@timer
def filter_data_with_dates(data, start_date, end_date):
    """
    Filters the dataset to be between the start and end dates
    """

    data = data[(data[1] >= start_date) & (data[1] <= end_date)]

    return data


@timer
def time_spent_in_rating(data, end_date):
    """
    Calculates the total time spent in a single code. First calculated on an Id level basis and then aggregated by state

    Returns:
        total_time_in_state: df of each state and time spent in each
    """

    total_time_in_state = pd.DataFrame(columns=['ID', 'State', 'TimeinState'])
    ID_list = data[0].unique()
    # Perform individually for every Id
    for ID in ID_list:
        data_ID = data[data[0] == ID]
        data_ID = data_ID.sort_values(by=1, ascending=True)

        data_ID['TimeinState'] = 0
        data_ID['TimeinState'] = data_ID['TimeinState'].astype('timedelta64[ns]')

        # take next time as comparator and subtract
        data_ID_shift = data_ID.shift(periods=-1)
        data_ID['TimeinState'] = data_ID_shift[1] - data_ID[1]

        # Final time is taken as end - last date
        data_ID.loc[data_ID.index[-1], 'TimeinState'] = end_date - data_ID.loc[data_ID.index[-1], 1]

        data_ID['TimeinState'] = data_ID['TimeinState'].dt.days.astype('int32')
        time_in_state = data_ID.groupby([0, 2])['TimeinState'].sum()

        time_in_state = time_in_state.reset_index()
        time_in_state.columns = ['ID', 'State', 'TimeinState']

        total_time_in_state = total_time_in_state.append(time_in_state, ignore_index=True)

    total_time_in_state = total_time_in_state.groupby(['State'])['TimeinState'].sum()

    total_time_in_state = total_time_in_state / 365.25  # Convert to Years
    total_time_in_state = total_time_in_state.reset_index()

    return total_time_in_state


@timer
def ID_transition_count(data):
    """

    Counts the number of transitions in the time period.
    Does not include moves of one state to the Same (e.g. 1 > 1) i.e not moving.
    Performed initially per ID and then summarised
    Returns:
        trans_counts - count of number of times each transition is made
    """
    ID_list = data[0].unique()
    trans_counts = pd.DataFrame(columns=['ID', 'State1', 'State2', 'Count'])
    for ID in ID_list:
        data_ID = data[data[0] == ID]
        data_ID = data_ID.sort_values(by=1, ascending=True)
        data_ID = data_ID.reset_index(drop=True)

        # Filter out values that repeat. E.g. B >> B >> C, becomes B >> C
        data_ID[2] = data_ID[data_ID[2] != data_ID.loc[:, 2].shift(1)][2]
        data_ID = data_ID[pd.notnull(data_ID[2])]
        data_ID = data_ID.reset_index(drop=True)

        data_to_summarise = data_ID
        data_to_summarise[3] = data_ID[2].shift(periods=-1)  # Take previous rating

        data_summarised = data_to_summarise.groupby([0, 2, 3])[
            1].count()  # group by ID, Rating now, Rating before and count
        data_summarised = data_summarised.reset_index(drop=False)
        data_summarised.columns = ['ID', 'State1', 'State2', 'Count']

        trans_counts = trans_counts.append(data_summarised, ignore_index=True)

    return trans_counts


@timer
def group_transition_counts(trans_counts, state_list):
    """
    Group counts and fill in non occurring transitions

    Returns:
        total_trans_counts - total number of transitions summed over every id
    """
    total_trans_counts = trans_counts.groupby(['State1', 'State2'])['Count'].sum()
    total_trans_counts = total_trans_counts.reset_index()

    # consider every possible transition combination
    # Find any Non Occurring Transitions, give them count 0 and add them to the transition matrix

    all_state_combinations = pd.DataFrame(product(state_list, state_list), columns=['State1', 'State2'])

    # left join on transition counts and give non occuring values 0
    total_trans_counts = all_state_combinations.merge(total_trans_counts, how ='left',on=['State1', 'State2'])
    total_trans_counts['Count'].fillna(0, inplace=True)

    # We ignore non-transitions, that is dealt with in calculate_non_transition_probability
    total_trans_counts = total_trans_counts[total_trans_counts['State1'] != total_trans_counts['State2']]
    total_trans_counts = total_trans_counts.sort_values(by=['State1', 'State2']).reset_index()

    return total_trans_counts


@timer
def count_per_time(total_trans_counts, total_time_in_state):
    """
    Divides counts of transitions by total time spent in the State.
    """

    count_time = pd.merge(total_trans_counts, total_time_in_state, left_on=['State1'], right_on=['State'])
    count_time['countperTime'] = count_time['Count'] / count_time['TimeinState']

    count_time = count_time.drop(['Count', 'State', 'TimeinState'], axis=1)
    count_time.columns = ['State1', 'State2', 'Probability']
    # Fill any fields with Nan with 0. Accounts for probabilities that have 0 time in state
    count_time['Probability'] = count_time['Probability'].fillna(0)

    return count_time


@timer
def calculate_non_transition_probability(count_time):
    '''
    Calculate the probability of staying in state and create full transition probability table
    '''

    sum_per_state = count_time.groupby('State1')['Probability'].sum()
    sum_per_state = sum_per_state.reset_index()
    sum_per_state['State2'] = sum_per_state['State1']
    sum_per_state['NonTranProb'] = - sum_per_state['Probability']
    sum_per_state = sum_per_state.drop('Probability', axis=1)
    sum_per_state.columns = ['State1', 'State2', 'Probability']

    transition_probability = count_time.append(sum_per_state, ignore_index=True)

    return transition_probability


def trans_prob(data: pd.DataFrame, date_format_string: str, start_date: str = None,
               end_date: str = None) -> pd.DataFrame:
    """
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

    """
    # -------------- Check that Dataset is in desired format ------------------------------------------#

    assert (data.shape[1] == 3), "Input data must only have 3 columns"

    data.columns = [0, 1, 2]

    assert (pd.api.types.is_datetime64_any_dtype(data[1])), "Date Column must be in datetime64 format"

    print('Transprob input data checks complete')
    # -------------- Call functions ------------------------------------------#

    # Calculate start and end dates from the data if not previously specified
    start_date_calculated, end_date_calculated, time_period = calculate_total_time_period(data, start_date,
                                                                            end_date, date_format_string)

    # Filter data on specified dates
    data = filter_data_with_dates(data, start_date_calculated, end_date_calculated)

    # Calculate the total time spent in each rating
    total_time_in_rating = time_spent_in_rating(data, end_date_calculated)

    trans_counts_out = ID_transition_count(data)

    unique_states = data[2].unique()

    total_trans_counts_out = group_transition_counts(trans_counts_out, unique_states)

    count_per_time_out = count_per_time(total_trans_counts_out, total_time_in_rating)

    transition_probability = calculate_non_transition_probability(count_per_time_out)

    # -------------- Test Output dataset ------------------------------------------#

    trans_prob_out = pd.pivot_table(transition_probability, values='Probability', index='State1', columns='State2')
    trans_prob_out = pd.DataFrame(expm(np.array(trans_prob_out)))

    # Check that the total probability of transitions from a state is 1 
    for _, row in trans_prob_out.iterrows():
        assert abs(row.sum()) - 1 < 0.0001, "Output state probabilities do not sum to 1"

    return trans_prob_out
