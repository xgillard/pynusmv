'''
This module defines a few decorators and (potentially) other useful functions
that makes the writing/reading of test cases clearer and easier to track.
'''
import os
import sys

def todo(fn):
    """
    A decorator to tell a test was foreseen but not implemented
    """
    return _log(fn, "Foreseen but not implemented yet")

def skip(reason):
    """
    A decorator to disable a function and warn it has been manually disabled
    """
    return lambda fn: _log(fn, "Manually disabled : {}".format(reason))

def _log(fn, message):
    """
    Returns a function to log the given message
    """
    msg = "INFO : {}.{} -> {}".format(fn.__module__, fn.__name__, message)
    return lambda *x: print(msg, file=sys.stderr) 

def canonical_cnf(be):
    """
    Returns a canonical string representation of the clauses in `be` (enable 
    comparison of generated be's)
    
    :return: a canonical string representation of the clauses in `be` when converted
        in CNF
    """
    cnf = be.to_cnf()
    clit= cnf.formula_literal
    lst = [ sorted([ item for item in array if abs(item) != clit ]) for array in cnf.clauses_list ]
    return str(sorted(lst))

def current_directory(what):
    """
    Returns the current working directory (as of now, cwd) from which the 
    current test case is loaded. Thanks to the cwd, one can write portable test
    cases as the tests will be able to load a resource relative to themselves
    at any time.
    
    Example use::
    
        def setUp(self):
            init_nusmv()
            load_from_file(tests.current_directory(__file__)+"/example.smv")
    
    :param what: the __file__ variable of the ongoing test
    :return: the cwd
    """
    return os.path.dirname(os.path.realpath(what))
    