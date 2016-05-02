import argparse

from pynusmv.init          import init_nusmv
from pynusmv.glob          import load, master_bool_sexp_fsm
from pynusmv.parser        import parse_simple_expression
from pynusmv.node          import Node  
from pynusmv.bmc.glob      import BmcSupport, master_be_fsm
from pynusmv.be.expression import Be
from pynusmv.bmc.utils     import BmcModel,                    \
                                  make_nnf_boolean_wff,        \
                                  generate_counter_example
from pynusmv.sat           import SatSolverFactory,            \
                                  Polarity,                    \
                                  SatSolverResult 
from pynusmv.trace         import Trace, TraceType
 
def arguments():
    """
    Thus function takes care of setting up the machinery to parse the command
    line arguments and return an object containing the parsed args. It moreover
    takes care of displaying an error message / help message whenever needed.
    
    :return: an object containing the parsed command-line arguments.
    """
    args = argparse.ArgumentParser(description="""
        This tool implements a diagnosability test verifier with SAT BMC.
    """)
    args.add_argument("model", 
                    help="The model to load")
    args.add_argument("-s", "--spec", 
                      help="The property whose diagnosability needs to be verified"+\
                           "diagnosability condition *NEED* to be separated by a semicolon")
    args.add_argument("-k", "--bound",
                      type=int,
                      default=10,
                      help="The problem bound (max number of steps in a trace)")
    
    return args.parse_args()

def generate_path(offset, length):
    """
    Returns a boolean expression representing a path of length `length` in the
    fsm described by the loaded model.
    
    :param length: the length of the path in the fsm
    :param offset: the offset at which the path should be starting
    :return: a boolean expression representing a path of length `length` in the
        loaded fsm.
    """
    model = BmcModel()
    path  = model.init[offset] & model.unrolling(offset, offset + length)
    return path

def constraint_same_observations(offset_path1, offset_path2, length):
    """
    Generates a boolean expression stating that the observable state of both 
    paths should be the same (all input vars are equivalent).
    
    :param offset_path1: the offset at which path 1 is supposed to start (should be 0)
    :param offset_path2: the offset at which path 2 is supposed to start (must not intersect with path1)
    :param length: the length of the path
    :return: an expression describing the fact that observations must be the 
        exact same along the two paths.
    """
    fsm = master_be_fsm()
    constraint = Be.true(fsm.encoding.manager)
    for time_ in range(length+1):
        for v in fsm.encoding.input_variables:
            ep1 = v.at_time[time_ + offset_path1].boolean_expression
            ep2 = v.at_time[time_ + offset_path2].boolean_expression
            constraint &= ep1.iff(ep2)
    return constraint

def constraint_eventually_inconsistent_belief_states(formula_nodes, offset_path1, offset_path2, length):
    """
    Generates a boolean expression representing the critical pair condition.
    That is to say, it generates a condition that verifies if it is possible that
    the two belief states are inconsistent wrt `formula`.
    
    :param formula: the formula whose diagnosability is verified.
    :param offset_path1: the offset at which path 1 is supposed to start (should be 0)
    :param offset_path2: the offset at which path 2 is supposed to start (must not intersect with path1)
    :param length: the length of the path
    :return: an expression describing the 'critical pair' condition.
    """
    enc = master_be_fsm().encoding
    yes = make_nnf_boolean_wff(formula_nodes[0]).to_be(enc)
    no  = make_nnf_boolean_wff(formula_nodes[1]).to_be(enc)
    
    constraint = Be.false(enc.manager)
    for time_ in range(length+1):
        constraint |= ( enc.shift_to_time(yes, time_ + offset_path1)
                      & enc.shift_to_time(no , time_ + offset_path2) ) 
    return constraint
        

def generate_sat_problem(formula_nodes, length):
    """
    Generates a SAT problem which is satisfiable iff the given `formula` is 
    *NOT* diagnosable for the loaded model for traces of length `length`.
    
    :param formula: the node (NuSMV ast representation) representing the formula
        whose diagnosability is under verification
    :param length: the maximum length of the generated traces.
    :return: a SAT problem which is satisfiable iff the given formula is not
        diagnosable on the loaded model.
    """
    offset_1  = 0
    offset_2  = length +1
    
    problem = generate_path(offset_1, length) & generate_path(offset_2, length) \
            & constraint_same_observations(offset_1, offset_2, length)          \
            & constraint_eventually_inconsistent_belief_states(
                                    formula_nodes, offset_1, offset_2, length)
    return problem

def verify_for_size_exactly_k(formula_nodes, k):
    """
    Performs the verification of the diagnosability problem for `formula_node`
    when a maximum of `k` execution steps are allowed.
    
    :param formula: the node (NuSMV ast representation) representing the formula
        whose diagnosability is under verification
    :param k: the maximum length of the generated traces.
    :return: the text 'No Violation' if no counter example could be found, 
        and a counter example when one could be identified.
    """
    problem = generate_sat_problem(formula_nodes, k)
    problem_= problem.inline(True)  # remove potentially redundant information
    cnf     = problem_.to_cnf()
    
    solver  = SatSolverFactory.create()
    solver += cnf
    solver.polarity(cnf, Polarity.POSITIVE)
    
    if solver.solve() == SatSolverResult.SATISFIABLE:
        fsm = master_be_fsm()
        return generate_counter_example(fsm, problem, solver, k, "Violation trace")
    else:
        return "No Violation"
    
def sanitize_counter_example(cnt_ex):
    """
    Removes all invisible state variables from the counter example trace so that
    only the visible behavior can be seen from the trace.
    """
    scalar_fsm = master_bool_sexp_fsm()
    counter_ex = Trace.create(
                    "Violation Trace", TraceType.COUNTER_EXAMPLE, 
                    scalar_fsm.symbol_table, 
                    scalar_fsm.symbols_list, 
                    True)
    counter = 0
    for step in cnt_ex:
        for symbol in cnt_ex.input_vars:
            value = step.value[symbol]
            if value is not None:
                try:
                    counter_ex.steps[counter].assign(symbol, value)
                except: 
                    counter_ex.append_step().assign(symbol, value)
        counter += 1
                
    return counter_ex 

def mk_specs_nodes(args):
    """
    Creates the Nodes(:see:`pynusmv.node.Node`), that represent the diagnosability
    condition to be verified. 
    
    .. note::
        
        The diagnosability condition *must* be expressed as a pair of boolean 
        expression (propositional formulas) that are separated by a semicolon.
        
        Example::
            
            status = active ; status = highlighted
            
    :return: a tuple representing the diagnosability condition to be verified.
        (This tuple is composed of two Nodes, which stand for the NuSMV way of
        representing formulas)
    """
    splitted = args.spec.split(';')
    if len(splitted) < 2:
        raise ValueError("The two parts of the diagnosability condition need to be separated with a semicolon")
    to_node = lambda x: Node.from_ptr(parse_simple_expression(x))
    return tuple(map(to_node, splitted))

def proceed(args):
    """Actually proceeds to the verification"""
    with init_nusmv():
        with open(args.model) as m:
            print(m.read())
        load(args.model)
        with BmcSupport():
            diagnosability_condition = mk_specs_nodes(args)
            for k in range(args.bound+1):
                result = verify_for_size_exactly_k(diagnosability_condition, k) 
                if "No Violation" != str(result):
                    print("-- {} is *NOT* diagnosable for length {}".format(diagnosability_condition, k))
                    print(sanitize_counter_example(result))
                    return
            print("-- No counter example found for executions of length <= {}".format(k))

if __name__ == "__main__":
    proceed(arguments())