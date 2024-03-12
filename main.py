from scipy.optimize import *
from itertools import *
from numpy import transpose, ndarray

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

def get_expected_value_pure_strategies(strategy1, strategy2, values, obj):
    """ get the expected value for player with strategy1 when going up against someone using strategy2 with obj as objective

    Args:
        strategy1 (list): strategy of player 1
        strategy2 (list): strategy of player 2
        values (list): a list of values of each battlefield
        obj (string): "win", "score", or "lottery"

    Returns:
        float: expected value of player 1 score
    """
    num_battlefields = len(values)
    expected_value = 0
    if obj == "score":
        for i in range(num_battlefields):
            if strategy1[i] > strategy2[i]:
                expected_value += values[i]
            elif strategy1[i] == strategy2[i]:
                expected_value += values[i]/2
    elif obj == "win":
        p1_score = 0
        p2_score = 0
        for i in range(num_battlefields):
            if strategy1[i] > strategy2[i]:
                p1_score += values[i]
            elif strategy1[i] == strategy2[i]:
                p1_score += values[i]/2
                p2_score += values[i]/2
            else:
                p2_score += values[i]
        if p1_score > p2_score:
            expected_value = 1
        elif p1_score == p2_score:
            expected_value = 0.5
        else:
            expected_value = 0
    
    elif obj == "lottery":
        for i in range(num_battlefields):
            prob_p1_wins = None
            if strategy1[i] == strategy2[i]:
                prob_p1_wins = 1/2
            else:
                prob_p1_wins = strategy1[i] * strategy1[i] / (strategy1[i] * strategy1[i] + strategy2[i] * strategy2[i])
            expected_value += prob_p1_wins * values[i]
    
    return expected_value

def get_expected_value_general_strategies(g_strategy1, g_strategy2, values, obj):
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
            expected_value += get_expected_value_pure_strategies(pure_strategy1, pure_strategy2, values, obj) * prob_of_p_strat_1 * prob_of_p_strat_2
    
    return expected_value

def get_payoff_matrix(pure_strategies, values, obj):
    """gets the payoff matrix of the blotto game associated with units, values, and objective

    Args:
        units (int): the number of units to distribute for each player
        values (list): a list of values of each battlefield
        obj (string): "win", "score", or "lottery"

    Returns:
        list: the payoff matrix
    """
    payoff_matrix = []
    num_pure_strats = len(pure_strategies)
    
    for i in range(num_pure_strats):
        payoff_matrix_row = []
        for j in range(num_pure_strats):
            payoff_matrix_row.append(get_expected_value_pure_strategies(pure_strategies[i], pure_strategies[j], values, obj))
        payoff_matrix.append(payoff_matrix_row)
    
    return payoff_matrix

def get_normalized_probability(probs):
    """gets the same list of probabilities but with their sum normalized to 1

    Args:
        probs (list): list of probabilities

    Returns:
        list: list of probabilities, normalized
    """
    
    sum_probs = sum(probs)
    multiply_factor = 1/sum_probs
    for i in range(len(probs)):
        probs[i] = probs[i] * multiply_factor
    
    return probs

def print_equilibrium_general_strategy(units, values):
    """gets the nash equilibrium general strategy that is optimized for win or score

    Args:
        units (int): the number of units to distribute for each player
        values (list): a list of values of each battlefield

    """
    
    # the nash general strategy must be the best strategy going up against itself
    # it must be at least as good as any pure strategy going up against the nash general strategy
    # let z = expected_value_general_strategies(nash_gstrat, nash_gstrat, values)
    # we must have expected_value_general_strategies(pstrat, nash_gstrat, values) <= z
    # where pstrat is any pure strategy
    
    pure_strategies = get_pure_strategies(units, values)
    payoff_matrix_transpose = ndarray.tolist(transpose(get_payoff_matrix(pure_strategies, values, "score")))
    
    # print(payoff_matrix_transpose)
    # flip all the values and move z to lhs so we can use it to feed lhs_ineq
    lhs_eq = [[]]
    rhs_ineq = []
    obj = []
    bnd = []
    for i in range(len(payoff_matrix_transpose)):
        # make the rhs_ineq
        rhs_ineq.append(0)
        # make the normalization condition: x1 + x2 + x3 + ... = 1
        lhs_eq[0].append(1)
        # set up for minimizing -z
        obj.append(0)
        # set bounds 0 <= x1, x2, x3, ... <= 1
        bnd.append((0, 1))
        for j in range(len(payoff_matrix_transpose)):
            payoff_matrix_transpose[i][j] = -payoff_matrix_transpose[i][j]
        payoff_matrix_transpose[i].append(1)
    
    # add the coefficient for z
    lhs_eq[0].append(0)
    # add the bounds for z
    bnd.append((0, float("inf")))
    lhs_ineq = payoff_matrix_transpose
    rhs_eq = [1]
    
    # goal is to maximize z, so minimize -z
    obj.append(-1)
    
    # print(obj)
    # print(lhs_ineq)
    # print(rhs_ineq)
    # print(lhs_eq)
    # print(rhs_eq)
    # print(bnd)
    
    opt = linprog(c=obj, 
                  A_ub=lhs_ineq, 
                  b_ub=rhs_ineq,
                  A_eq=lhs_eq, 
                  b_eq=rhs_eq, 
                  bounds=bnd,
                  method="highs",
                  options={'primal_feasibility_tolerance': 1e-6})
    
    # print(opt.status)
    
    normalized_probs = get_normalized_probability(opt.x[0:len(opt.x) - 1])
    
    sum_prob = 0
    for i in range(len(pure_strategies)):
        if abs(normalized_probs[i] - 0) <= 1e-12:
            continue
        output_row = ""
        for j in range(len(pure_strategies[i])):
            output_row += str(pure_strategies[i][j]) + ","
        output_row += str(normalized_probs[i])
        sum_prob += normalized_probs[i]
        print(output_row)
        
def verify_equilibrium_general_strategy(g_strategy, units, value, obj):
    """prints PASSED if g_strategy is an equilibrium strategy for both players, and the violation if not

    Args:
        g_strategy (list): a list where each entry is a pure strategy followed by the probability of playing that strategy
        units (int): the number of units to distribute for each player
        values (list): a list of values of each battlefield
        obj (string): "win", "score", or "lottery"
    """
    
    
print_equilibrium_general_strategy(5, [2,4,5])

# s1 = [[0,0,5,0.1999999999999999],
#       [0,1,4,0.15000000000000044],
#       [0,2,3,0.09999999999999985],
#       [0,3,2,0.05000000000000036],
#       [1,0,4,0.04999999999999977],
#       [1,1,3,0.10000000000000005],
#       [1,2,2,0.1500000000000001],
#       [1,3,1,0.19999999999999962]]
# print(get_expected_value_general_strategies(s1, s1, [2,4,5], "score"))

# s2 = [[0,0,5,0.14045462101642173],
# [0,1,4,0.15496211495866577],
# [0,2,3,0.04541673569373383],
# [0,3,2,0.05992422986845587],
# [1,0,4,0.08473480443797905],
# [1,1,3,0.09503788495378677],
# [1,2,2,0.17977268944230548],
# [1,3,1,0.1404546206153363],
# [1,4,0,0.04962114905424416],
# [2,3,0,0.04962114943279007]]
# print(get_expected_value_general_strategies(s2, s2, [2,4,5], "score"))