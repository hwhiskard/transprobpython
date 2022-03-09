# import pytest
import pandas as pd
from itertools import product
from src.transprob import time_spent_in_rating, ID_transition_count, group_transition_counts


def test_time_in_rating_state_count():
    """
    Every rating should be accounted for in time_spent
    """
    testdata = 'test/data/creditRatingExample.csv'
    testdata = pd.read_csv(testdata, delimiter=',', header=0, parse_dates=[1])
    testdata.columns = [0, 1, 2]

    end_date = testdata[1].max()
    time_spent = time_spent_in_rating(testdata, end_date)

    unique_codes = testdata[2].unique()
    assert len(time_spent['State']) == len(unique_codes), 'Codes missing'


def test_time_in_rating_totaltime():
    """
    Total time spent in ratings should be equal to total time of data for one ID
    """
    testdata = 'test/data/single_ID.csv'
    testdata = pd.read_csv(testdata, delimiter=',', header=0, parse_dates=[1])
    testdata.columns = [0, 1, 2]

    start_date = testdata[1].min()
    end_date = testdata[1].max()
    time_spent = time_spent_in_rating(testdata, end_date)
    assert abs((time_spent['TimeinState'].sum()) - (
                end_date - start_date).days / 365.25) < 0.00001, 'Time spent in ratings should equal total time'


def test_count_transition_states():
    """
    Make sure all transition states are included. Only tested on one ID
    """
    testdata = 'test/data/single_id.csv'
    testdata = pd.read_csv(testdata, delimiter=',', header=0, parse_dates=[1])
    testdata.columns = [0, 1, 2]

    trans_counts = ID_transition_count(testdata)
    transitions = pd.concat([testdata[2], testdata[2].shift(-1)], axis=1)
    transitions.columns = ['State1', 'State2']
    transitions = transitions[transitions['State1'] != transitions['State2']]
    transitions = transitions.dropna().drop_duplicates()
    assert transitions.shape == trans_counts.loc[:, ['State1', 'State2']].shape, "Incorrect number of transitions"


def test_grouping_transition_counts():

    trans_counts = pd.read_csv('test/data/trans_counts_test.csv')
    states = pd.read_csv('test/data/state_list_test.csv')
    total_trans_counts = group_transition_counts(trans_counts, states)
    total_combos = pd.DataFrame(product(states, states))

    assert total_combos[total_combos[0] != total_combos[1]].shape[0] == total_trans_counts.shape[
        0], "Make sure all state transitions are present"


def test_grouping_transition_count_sum():

    trans_counts = pd.read_csv('test/data/trans_counts_test.csv')

    transitions_before = trans_counts['Count'].sum()
    print(trans_counts)

    states = pd.read_csv('test/data/state_list_test.csv')
    states.columns = ['State']
    total_trans_counts = group_transition_counts(trans_counts, states['State'].unique())

    transitions_after = total_trans_counts['Count'].sum()
    print(total_trans_counts)
    assert transitions_before == transitions_after, "Make number of transitions does not change"
