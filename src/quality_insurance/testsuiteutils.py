"""
This module provides some convenient utility functions and decorators related 
to the automated testing of code (using testsuites)
"""
import coverage

__all__ = ['not_included', 'with_warnings', 'with_coverage']

#===============================================================================
#====== Warnings ===============================================================
#===============================================================================

# a list containing the warning messages to be displayed at end of an execution
warnings = []

def not_included(module):
    """
    This function creates a warning telling that the given :module: was not 
    tested
    
    :param module: a text indicating what is not included
    """
    warnings.append("## WARNING ## {} not included".format(module))

def print_warnings():
    """prints the warning messages"""
    for w in warnings:
        print(w)
        
def with_warnings(fn):
    """
    Decorator that executes the wrapped function and then prints all registered
    warning messaes
    """
    warnings.clear()
    def wrap(*args):
        fn(*args)
        print_warnings()
    return wrap

#===============================================================================
#====== Code coverage ==========================================================
#===============================================================================
def with_coverage(*modules,**kwargs):
    """
    Decorator that activates the coverage for the wrapped function then prints
    a code coverage report for the modules listed in modules.
    
    :param modules: a list of prefixes indicating what modules need to be 
       included in the coverage report list. 
    """
    def deco(fn):
        def wrap(*args):
            cov = coverage.Coverage()
            cov.start()
            fn(*args)
            cov.stop()
            cov.report(show_missing=False, include=modules)
            
            if "html" in kwargs:
                cov.html_report(include=modules)
        return wrap
    return deco