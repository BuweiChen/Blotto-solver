import scipy
from scipy.optimize import linprog
from itertools import *

def get_pure_strategies(units, values):
    """ get a list of pure strategies

    Args:
        units (int): the number of units to distribute for each player
        values (list): a list of values of each battlefield

    Returns:
        list: list of pure strategies, where each pure strategy is a list of the 
        number of units assigned to each battlefield
    """
    num_battlefields = len(values)
    pure_strategies = []

    for combo in product(range(units + 1), repeat=num_battlefields):
        if sum(combo) == units:
            pure_strategies.append(list(combo))

    return pure_strategies

def get_expected_value_pure_strategies(strategy1, strategy2, values):
    """ get the expected value for player with strategy1 when going up against someone using strategy2

    Args:
        strategy1 (list): strategy of player 1
        strategy2 (list): strategy of player 2
        values (list): a list of values of each battlefield

    Returns:
        float: expected value of player 1 score
    """
    num_battlefields = len(values)
    expected_value = 0
    for i in range(num_battlefields):
        p1_curr_battle_outcome = 0
        if strategy1[i] > strategy2[i]:
            p1_curr_battle_outcome = values[i]
        elif strategy1[i] == strategy2[i]:
            p1_curr_battle_outcome = values[i]/2
        expected_value += p1_curr_battle_outcome
        
    return expected_value

def get_expected_value_general_strategies(g_strategy1, g_strategy2, values):
    """get the expected value of player with g_strategy1 when going up against someone using gstrategy2

    Args:
        g_strategy1 (list): a list where each entry is a pure strategy followed by the probability of playing that strategy
        g_strategy2 (list): a list where each entry is a pure strategy followed by the probability of playing that strategy
        values (list): a list of values of each battlefield

    Returns:
        float: expected value of player 1 score
    """
    num_battlefields = len(values)
    expected_value = 0
    for pure_strategy1 in g_strategy1:
        prob_of_p_strat_1 = pure_strategy1[num_battlefields] # retrieves last element of array
        for pure_strategy2 in g_strategy2:
            prob_of_p_strat_2 = pure_strategy2[num_battlefields]
            expected_value += get_expected_value_pure_strategies(pure_strategy1, pure_strategy2, values) * prob_of_p_strat_1 * prob_of_p_strat_2
    
    return expected_value

gs1 = [[1,1,3, 0.7],
       [5,0,0, 0.3]]
gs2 = [[3,2,0, 0.5],
       [3,1,1, 0.4],
       [0,0,5, 0.1]]
print(get_expected_value_general_strategies(gs1, gs2, [5,2,1]))