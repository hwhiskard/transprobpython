# transprobpython
Transition probability function for Markov Chains developed in python.
Inspiration from the matlab transprob function, not previously replicated in MATLAB

Calculates probabilities using Duration algorithm   
    Inputs:-  nx3 table with columns as Id, Date and State
           - Optional input for start and end date to limit calculations.
           
    Output: transition probability matrix k x k, where k is the total number of states 
