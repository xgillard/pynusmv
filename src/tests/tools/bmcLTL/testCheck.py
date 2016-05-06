'''
This module validates the behavior of the utility functions defined in the 
module :mod:`tools.bmcLTL.check`.
'''

from unittest             import TestCase
from tests                import utils as tests
from pynusmv.init         import init_nusmv
from pynusmv.glob         import load 
from pynusmv.bmc.glob     import BmcSupport

from tools.bmcLTL.parsing import parseLTL
from tools.bmcLTL         import check # the tested module 
class TestCheck(TestCase):
    
    def test_GLOBALLY_check_ltl_onepb(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/example.smv")
            with BmcSupport():
                formula      = parseLTL("[](a <=> !b)")
                for k in range(10):
                    status,trace = check.check_ltl_onepb(formula, k)
                    self.assertEqual("Ok", status)
                    self.assertIsNone(trace)
                
                # already violated in the initial state
                formula      = parseLTL("[](a <=> b)")
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Violation", status)
                self.assertIsNotNone(trace)
                self.assertEqual(0, len(trace))
                    
                
    def test_EVENTUALLY_check_ltl_onepb(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/example.smv")
            with BmcSupport():         
                # proving a violation of this prop necessitates at least two
                # steps: flip --> flop --> flip 
                formula      = parseLTL("<>(a <=> b)")
                
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 1)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                # a loop is identified
                status,trace = check.check_ltl_onepb(formula, 2)
                self.assertEqual("Violation", status)
                self.assertIsNotNone(trace)
                self.assertEqual(2, len(trace))
                
                # valid in the initial state (hence for any bound)
                formula      = parseLTL("<>(a | b)")
                for k in range(10):
                    status,trace = check.check_ltl_onepb(formula, k)
                    self.assertEqual("Ok", status)
                    self.assertIsNone(trace)
                    
    def test_NEXT_check_ltl_onepb(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/example.smv")
            with BmcSupport():         
                # false in the initial state
                formula      = parseLTL("() a")
                
                # however the violation is not detected when no move is allowed
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 1)
                self.assertEqual("Violation", status)
                self.assertIsNotNone(trace)
                self.assertEqual(1, len(trace))
                
                # true in the initial state
                formula      = parseLTL("()() a")
                # not reachable
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                # not quite yet
                status,trace = check.check_ltl_onepb(formula, 1)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                # ok
                status,trace = check.check_ltl_onepb(formula, 2)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                # and even for longer traces
                status,trace = check.check_ltl_onepb(formula, 3)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
    def test_WEAKUNTIL_check_ltl_onepb(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/never_b.smv")
            with BmcSupport():         
                # entailed by the automaton
                formula      = parseLTL("a W b")
                
                # not reachable
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                # already looping but no counter example
                status,trace = check.check_ltl_onepb(formula, 1)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                # true in the initial state
                formula      = parseLTL("b W a")
                
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 1)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 2)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 3)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                # violated right away
                formula      = parseLTL("b W !a")
                
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Violation", status)
                self.assertIsNotNone(trace)
                self.assertEqual(0, len(trace))
                
    def test_UNTIL_check_ltl_onepb(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/never_b.smv")
            with BmcSupport():         
                # entailed by the automaton
                formula      = parseLTL("a U b")
                
                # not reachable
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                # this is where U differs from W: at infinity, b must hold
                status,trace = check.check_ltl_onepb(formula, 1)
                self.assertEqual("Violation", status)
                self.assertIsNotNone(trace)
                self.assertEqual(1, len(trace))
                
                # true in the initial state
                formula      = parseLTL("b U a")
                
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 1)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 2)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                status,trace = check.check_ltl_onepb(formula, 3)
                self.assertEqual("Ok", status)
                self.assertIsNone(trace)
                
                # violated right away
                formula      = parseLTL("b U !a")
                
                status,trace = check.check_ltl_onepb(formula, 0)
                self.assertEqual("Violation", status)
                self.assertIsNotNone(trace)
                self.assertEqual(0, len(trace))
                
    def test_GLOBALLY_check_ltl(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/example.smv")
            with BmcSupport():
                status,l,trace = check.check_ltl(parseLTL("[](a <=> !b)"), 5)
                self.assertEqual('Ok', status)
                self.assertEqual(5, l)
                self.assertIsNone(trace)
                
                status,l,trace = check.check_ltl(parseLTL("[](a & b)"), 5)
                self.assertEqual('Violation', status)
                self.assertEqual(0, l)
                self.assertIsNotNone(trace)
                
    def test_EVENTUALLY_check_ltl(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/example.smv")
            with BmcSupport():
                status,l,trace = check.check_ltl(parseLTL("<>(a <=> !b)"), 5)
                self.assertEqual('Ok', status)
                self.assertEqual(5, l)
                self.assertIsNone(trace)
                
                status,l,trace = check.check_ltl(parseLTL("<>(a & b)"), 5)
                self.assertEqual('Violation', status)
                self.assertEqual(2, l)
                self.assertIsNotNone(trace)
                
    def test_NEXT_check_ltl(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/example.smv")
            with BmcSupport():
                status,l,trace = check.check_ltl(parseLTL("()() a"), 5)
                self.assertEqual('Ok', status)
                self.assertEqual(5, l)
                self.assertIsNone(trace)
                
                status,l,trace = check.check_ltl(parseLTL("() a"), 5)
                self.assertEqual('Violation', status)
                self.assertEqual(1, l)
                self.assertIsNotNone(trace)
                
    def test_WEAKUNTIL_check_ltl(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/never_b.smv")
            with BmcSupport():
                status,l,trace = check.check_ltl(parseLTL("a W b"), 5)
                self.assertEqual('Ok', status)
                self.assertEqual(5, l)
                self.assertIsNone(trace)
                
                status,l,trace = check.check_ltl(parseLTL("b W a"), 5)
                self.assertEqual('Ok', status)
                self.assertEqual(5, l)
                self.assertIsNone(trace)
                
                status,l,trace = check.check_ltl(parseLTL("b W !a"), 5)
                self.assertEqual('Violation', status)
                self.assertEqual(0, l)
                self.assertIsNotNone(trace)
                
    def test_UNTIL_check_ltl(self):
        with init_nusmv():
            load(tests.current_directory(__file__)+"/never_b.smv")
            with BmcSupport():
                status,l,trace = check.check_ltl(parseLTL("b U a"), 5)
                self.assertEqual('Ok', status)
                self.assertEqual(5, l)
                self.assertIsNone(trace)
                
                status,l,trace = check.check_ltl(parseLTL("a U b"), 5)
                self.assertEqual('Violation', status)
                self.assertEqual(1, l)
                self.assertIsNotNone(trace)
                
                status,l,trace = check.check_ltl(parseLTL("b W !a"), 5)
                self.assertEqual('Violation', status)
                self.assertEqual(0, l)
                self.assertIsNotNone(trace)