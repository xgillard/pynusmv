'''
This module defines a few decorators and (potentially) other useful functions
that makes the writing/reading of test cases clearer and easier to track.
'''
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