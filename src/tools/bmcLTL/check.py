"""
This module contains the functions to perform the bounded model checking of a 
given LTL property. 
"""
from pynusmv.bmc.glob   import master_be_fsm
from pynusmv.sat        import SatSolverResult, SatSolverFactory, Polarity
from pynusmv.bmc.utils  import generate_counter_example
from tools.bmcLTL.gen   import generate_problem

def check_ltl_onepb(fml, length):
    """
    This function verifies that the given FSM satisfies the given property
    (specified as text) for paths with an exact length of `length`.
    
    :param fml: an LTL formula parsed with `tools.bmcLTL.parsing` (hence the 
        abstract syntax tree of that formula). Note, this is *NOT* the NuSMV
        format (Node).
    :param length: the exact length of the considered paths
    :return: a tuple ('OK', None) if the property is satisfied on all paths of 
        length `length`
    :return: a tuple ('Violation', counter_example) if the property is violated. 
        The counter_example passed along is a trace leading to a violation of
        the property
    """
    fsm    = master_be_fsm()
    pb     = generate_problem(fml, fsm, length)
    cnf    = pb.to_cnf(Polarity.POSITIVE)
    
    solver = SatSolverFactory.create()
    solver+= cnf
    solver.polarity(cnf, Polarity.POSITIVE)
    
    if solver.solve() == SatSolverResult.SATISFIABLE:
        cnt_ex = generate_counter_example(fsm, pb, solver, length, str(fml))
        return ("Violation", cnt_ex)
    else:
        return ("Ok", None)
    
def check_ltl(fml, bound):
    """
    This function performs the bounded model checking of the formula given in 
    text format (as specified per the grammar in `parsing` module). It verifies
    that the property holds for all path lengths from 0 to bound.
    
    :param fml: an LTL formula parsed with `tools.bmcLTL.parsing` (hence the 
        abstract syntax tree of that formula). Note, this is *NOT* the NuSMV
        format (Node).
    :param bound: the maximum length of a path in the verification.
    :return: a tuple (status, len, trace) where status is 'Ok', len = bound and
        trace is None when no counter example was identified. Otherwise, 
        status = 'Violation', len the number of steps to reach a violation and
        trace is a counter example leading to a property violation.
    """
    for i in range(bound+1):
        status, trace = check_ltl_onepb(fml, i) 
        if status != "Ok":
            return (status, i, trace)
        else:
            print("-- No problem at length {}".format(i))
            
    return ("Ok", bound, None)
    