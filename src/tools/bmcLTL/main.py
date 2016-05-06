#! /usr/local/bin/python3
"""
This module is the entry point of a simple sat based bounded model checker for
the Linear Temporal Logic (LTL) implemented using the PyNuSMV library.
"""
import sys
import argparse

from pynusmv.init         import init_nusmv
from pynusmv.glob         import load
from pynusmv.bmc.glob     import BmcSupport
from tools.bmcLTL.parsing import parseLTL
from tools.bmcLTL.check   import check_ltl 

def arguments():
    """
    Creates the arguments parser and manages to react to wrong usage.
    
    :returns: an object having field to store each of the command line arguments
    """
    parser = argparse.ArgumentParser(description="a PyNuSMV backed LTL sat based bmc verifier for LTL")
    parser.add_argument("-k", "--bound", type=int, default=10, help="the maximum number of steps in a verified path")
    parser.add_argument("-s", "--spec",  type=str, help="the LTL specification to verify")
    parser.add_argument("model", type=str, help="the name of a file containing an SMV model")
    
    return parser.parse_args()

def check(formula, args):
    try:
        parsed_fml          = parseLTL(formula.strip())
        status,length,trace = check_ltl(parsed_fml, args.bound)
        if status != 'Ok':
            print("-- {} for length {}".format(status, length))
            print(trace)
    except Exception as e:
        print("The specification contains a syntax error")
        print(e)

if __name__ == "__main__":
    """
    The main program.
    """
    args = arguments()
    with init_nusmv():
        load(args.model)
         
        with open(args.model) as f:
            print(f.read())
        
        with BmcSupport():
            if args.spec is not None: 
                check(args.spec, args)
            else:
                print("Enter LTL properties, one per line:")
                for line in sys.stdin:
                    check(line, args)
        
        