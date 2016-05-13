#! /usr/local/bin/python3
"""
This module implements a simple verification tool able to perform a 
diagnosability test as explained in:: 
    
    Formal verification of diagnosability via symbolic model checking.
    Pecheur, C., Cimatti, A., & Cimatti, R. (2002, July). 
    In Workshop on Model Checking and Artificial Intelligence (MoChArt-2002), 
    Lyon, France.

Beyond the verification proper, this tool provides an illustrative example to 
show how the SAT-BMC addition to PyNuSMV may be used in order to perform 
verification scenarios which were initially not present in NuSMV.
"""
import sys
import argparse
from functools             import reduce

from pynusmv.init          import init_nusmv
from pynusmv.glob          import load, master_bool_sexp_fsm
from pynusmv.parser        import parse_simple_expression
from pynusmv.node          import Node  
from pynusmv.bmc.glob      import BmcSupport, master_be_fsm
from pynusmv.be.expression import Be
from pynusmv.bmc.utils     import BmcModel,                    \
                                  make_nnf_boolean_wff,        \
                                  generate_counter_example,    \
                                  booleanize
                                  
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
    args.add_argument("-o", "--observable", action="append",
                      default=[], 
                      help="Make the symbol passed as argument visible in the " +\
                      "current diagnosability test. This option can be repeated"+\
                      "at will to have multiple visible variables. (By default "+\
                      "only the input variables IVAR are considered visible)")
    args.add_argument("-k", "--bound",
                      type=int,
                      default=10,
                      help="The problem bound (max number of steps in a trace)")
    
    return args.parse_args()

def mk_observable_set(var_names):
    """
    Creates the list of the variables that are considered observable in the 
    context of this diagnosability test.
    
    :param var_names: a list of string containing the names of the vars that 
        should be visible
    :return: a list of untimed boolean expressions standing for the various bits
        of the observable variables.
    """
    if not var_names:
        # by default use the input variables
        return master_be_fsm().encoding.input_variables
    else:
        # otherwise use the user specified set of actions
        encoding         = master_be_fsm().encoding
        boolean_varnames = reduce(lambda x,y: x+y, map(booleanize, var_names), [])
        be_variables     = list(map(lambda x: encoding.by_name[str(x)],boolean_varnames))
        return be_variables

def mk_specs_nodes(spec):
    """
    Creates the Nodes(:see:`pynusmv.node.Node`), that represent the diagnosability
    condition to be verified. 
    
    .. note::
        
        The diagnosability condition *must* be expressed as a pair of boolean 
        expression (propositional formulas) that are separated by a semicolon.
        
        Example::
            
            status = active ; status = highlighted

    :param spec: the diagnosability condition to be evaluated.
    :return: a tuple representing the diagnosability condition to be verified.
        (This tuple is composed of two Nodes, which stand for the NuSMV way of
        representing formulas)
    """
    splitted = spec.split(';')
    if len(splitted) < 2:
        raise ValueError("The two parts of the diagnosability condition need to be separated with a semicolon")
    to_node = lambda x: Node.from_ptr(parse_simple_expression(x))
    return tuple(map(to_node, splitted))

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

def constraint_same_observations(observable_vars, offset_path1, offset_path2, length):
    """
    Generates a boolean expression stating that the observable state of both 
    paths should be the same (all input vars are equivalent).
    
    :param observable_vars: the list of the boolean variables that are considered
        visible in the scope of this diagnosability test
    :param offset_path1: the offset at which path 1 is supposed to start (should be 0)
    :param offset_path2: the offset at which path 2 is supposed to start (must not intersect with path1)
    :param length: the length of the path
    :return: an expression describing the fact that observations must be the 
        exact same along the two paths.
    """
    fsm = master_be_fsm()
    constraint = Be.true(fsm.encoding.manager)
    for time_ in range(length+1):
        for v in observable_vars:
            ep1 = v.at_time[time_ + offset_path1].boolean_expression
            ep2 = v.at_time[time_ + offset_path2].boolean_expression
            constraint &= ep1.iff(ep2)
    return constraint

def constraint_eventually_critical_pair(formula_nodes, offset_path1, offset_path2, length):
    """
    Generates a boolean expression representing the critical pair condition.
    That is to say, it generates a condition that verifies if it is possible that
    the two belief states are inconsistent wrt `formula`.
    
    :param formula_nodes: the formula whose diagnosability is verified.
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
        

def generate_sat_problem(observable_vars, formula_nodes, length):
    """
    Generates a SAT problem which is satisfiable iff the given `formula` is 
    *NOT* diagnosable for the loaded model for traces of length `length`.
    
    :param observable_vars: the list of the boolean variables that are considered
        visible in the scope of this diagnosability test
    :param formula: the node (NuSMV ast representation) representing the formula
        whose diagnosability is under verification
    :param length: the maximum length of the generated traces.
    :return: a SAT problem which is satisfiable iff the given formula is not
        diagnosable on the loaded model.
    """
    offset_1  = 0
    offset_2  = length +1
    
    problem = generate_path(offset_1, length) & generate_path(offset_2, length) \
            & constraint_same_observations(
                                    observable_vars, offset_1, offset_2, length) \
            & constraint_eventually_critical_pair(
                                    formula_nodes, offset_1, offset_2, length)
    return problem

def verify_for_size_exactly_k(observable_vars, formula_nodes, k):
    """
    Performs the verification of the diagnosability problem for `formula_node`
    when a maximum of `k` execution steps are allowed.
    
    :param observable_vars: the list of the boolean variables that are considered
        visible in the scope of this diagnosability test
    :param formula: the node (NuSMV ast representation) representing the formula
        whose diagnosability is under verification
    :param k: the maximum length of the generated traces.
    :return: the text 'No Violation' if no counter example could be found, 
        and a counter example when one could be identified.
    """
    problem = generate_sat_problem(observable_vars, formula_nodes, k)
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
    
def sanitize_counter_example(args, cnt_ex):
    """
    Removes all invisible state variables from the counter example trace so that
    only the visible behavior can be seen from the trace.
    """
    scalar_fsm = master_bool_sexp_fsm()
    observable = args.observable if   args.observable \
                                 else list(map(lambda x: str(x), cnt_ex.input_vars))
    counter_ex = Trace.create(
                    "Violation Trace", TraceType.COUNTER_EXAMPLE, 
                    scalar_fsm.symbol_table, 
                    scalar_fsm.symbols_list, 
                    True)
    counter = 1
    for step in cnt_ex:
        addition = False
        for symbol in cnt_ex.symbols:
            value = step.value[symbol]
            if (value is not None) and (str(symbol) in observable):
                try:
                    counter_ex.steps[counter].assign(symbol, value)
                    addition = True
                except: 
                    counter_ex.append_step().assign(symbol, value)
                    addition = True
        if addition:
            counter+=1
    return counter_ex

def check(args, condition_text):
    """
    Performs the verification of the diagnosability of the condition represented
    by `condition_text` and print its result to stdout.
    
    :param args: the arguments that were given on the command line
    :param condition_text: a string representing the diagnosability condition to
        be verified in the format 'c1 ; c2'.
    """
    try:
        observable_vars          = mk_observable_set(args.observable)
        diagnosability_condition = mk_specs_nodes(condition_text)
        for k in range(args.bound+1):
            result = verify_for_size_exactly_k(observable_vars, diagnosability_condition, k) 
            if "No Violation" != str(result):
                print("-- {} is *NOT* diagnosable for length {}".format(diagnosability_condition, k))
                print(sanitize_counter_example(args, result))
                return
        print("-- No counter example found for executions of length <= {}".format(k))
        
    except Exception as e:
        print("The specified condition contains a syntax error")
        print(e)

def proceed(args):
    """Actually proceeds to the verification"""
    with init_nusmv():
        with open(args.model) as m:
            print(m.read())
        load(args.model)
        with BmcSupport():
            if args.spec is not None:
                check(args, args.spec)
            else:
                print("Enter diagnosability condition, one per line in the format: 'c1 ; c2'")
                for line in sys.stdin:
                    check(args, line)

if __name__ == "__main__":
    proceed(arguments())
    