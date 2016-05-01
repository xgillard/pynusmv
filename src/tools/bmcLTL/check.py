"""
This module contains the functions to perform the bounded model checking of a 
given LTL property. 
"""
from pynusmv.bmc.glob   import master_be_fsm
from pynusmv.sat        import SatSolverResult, SatSolverFactory, Polarity
from pynusmv.bmc.utils  import generate_counter_example, \
                               fill_counter_example,     \
                               print_counter_example
from tools.bmcLTL.gen   import generate_problem

def check_ltl_onepb(text, length):
    """
    This function verifies that the given FSM satisfies the given property
    (specified as text) for paths with an exact length of `length`.
    
    :param text: an LTL formula as specified per the grammar in the 'parsing' module
    :param length: the exact length of the considered paths
    :return: 'OK' if the property is satisfied on all paths of length `length`
    :return: 'Violation' if the property is violated in some cases.
    """
    fsm    = master_be_fsm()
    pb     = generate_problem(text, fsm, length)
    cnf    = pb.to_cnf(Polarity.POSITIVE)
    
    solver = SatSolverFactory.create()
    solver+= cnf
    solver.polarity(cnf, Polarity.POSITIVE)
    
    if solver.solve() == SatSolverResult.SATISFIABLE:
        cnt_ex = generate_counter_example(fsm, pb, solver, length+1, text)
        print(cnt_ex)
        return "Violation"
    else:
        return "Ok"
    
def check_ltl(text, bound):
    """
    This function performs the bounded model checking of the formula given in 
    text format (as specified per the grammar in `parsing` module). It verifies
    that the property holds for all path lengths from 0 to bound.
    
    :param text: the LTL formula in text format
    :param bound: the maximum length of a path in the verification.
    """
    for i in range(1, bound+1):
        if check_ltl_onepb(text, i) != "Ok":
            print("-- Violation for length {}".format(i))
            break
        else:
            print("-- No problem at length {}".format(i))