'''
This module validates the behavior of the functions composing the tool verifying
the diagnosability of some property using bounded model checking.
'''

from unittest                  import TestCase
from tests                     import utils as tests
                               
from pynusmv.init              import init_nusmv, deinit_nusmv
from pynusmv.glob              import load 
from pynusmv.bmc.glob          import go_bmc, bmc_exit, master_be_fsm
                               
from pynusmv.be.expression     import Be
from pynusmv.bmc               import utils as bmcutils

from pynusmv.node              import Node 
from pynusmv.parser            import parse_simple_expression 
from pynusmv.sat               import SatSolverFactory, SatSolverResult, Polarity
from pynusmv.trace             import Trace                                 
from tools                     import diagnosability

class TestDiagnosability(TestCase):
    
    def model(self):
        return tests.current_directory(__file__)+"/input.smv"
    
    def setUp(self):
        init_nusmv()
        load(self.model())
        go_bmc()
        
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
    
    def test_generate_path_only_valid_offset_params(self):
        # must combine an initial state w/ 'length' unrolling
        with self.assertRaises(ValueError):
            diagnosability.generate_path(-1, 5)
        
        with self.assertRaises(ValueError):
            diagnosability.generate_path(0, -5)
            
    def test_generate_path_offset_zero(self):
        # when offset is 0 path is just your regular path
        
        # - test 1 - just the initial state
        regular = bmcutils.BmcModel().path(0)
        tool    = diagnosability.generate_path(0, 0)
        self.assertEqual(regular, tool)
        
        # - test 2 - more steps unrolled
        regular = bmcutils.BmcModel().path(3)
        tool    = diagnosability.generate_path(0, 3)
        self.assertEqual(regular, tool)
        
    def test_generate_path_offset_x(self):
        # must combine an initial state w/ 'length' unrolling
        model   = bmcutils.BmcModel()
        manual  = model.init[5] & model.unrolling(5, 10)
        tool    = diagnosability.generate_path(5, 5)
        self.assertEqual(manual, tool)
    
    def test_constraint_same_observations(self):
        constraint = diagnosability.constraint_same_observations(0, 5, 5)
        model      = bmcutils.BmcModel()
        
        manual     = Be.true(model._fsm.encoding.manager)
        for i in range(6): # because we want to go from 0 through 5
            for v in model._fsm.encoding.input_variables:
                v_1 = v.at_time[i].boolean_expression
                v_2 = v.at_time[5+i].boolean_expression
                manual &= v_1.iff(v_2)
        
        self.assertEqual(manual, constraint)
        
    def test_eventually_critical_pair(self):
        enc= master_be_fsm().encoding
        f1 = Node.from_ptr(parse_simple_expression("status = active"))
        f2 = Node.from_ptr(parse_simple_expression("status = highlight"))
        
        constraint = diagnosability.constraint_eventually_critical_pair((f1, f2), 0, 5, 5)
        
        nnf1   = bmcutils.make_nnf_boolean_wff(f1).to_be(enc)
        nnf2   = bmcutils.make_nnf_boolean_wff(f2).to_be(enc)
        manual = Be.false(enc.manager)
        
        for i in range(6): # again, from 0 to 5
            manual |= ( enc.shift_to_time(nnf1 , i)
                      & enc.shift_to_time(nnf2 , 5+i))
        
        # observing the clauses generated in both cases, one observes that 
        # the generated clauses are the same except that the number of the cnf
        # literals do not match, example:
        #                        [-59, -24, 58]
        #                        [-65, -24, 64]
        # This is due to the fact that some 'fresh' cnf literals are used in the
        # generation of the epxression. Therefore, a comparison (even on the 
        # canonical form of the CNF) is not feasible.
        #
        # Satisfiability is just an indication but at least that is .. something
        solver_c = SatSolverFactory.create()
        cnf      = constraint.to_cnf()
        solver_c+= cnf
        solver_c.polarity(cnf, Polarity.POSITIVE)
        result_c = solver_c.solve()
        
        solver_m = SatSolverFactory.create()
        cnf      = manual.to_cnf()
        solver_m+= cnf
        solver_m.polarity(cnf, Polarity.POSITIVE)
        result_m = solver_m.solve()
        
        self.assertEqual(result_c, result_m)
        
    def test_generate_sat_problem(self):
        f1 = Node.from_ptr(parse_simple_expression("status = active"))
        f2 = Node.from_ptr(parse_simple_expression("status = inactive"))
         
        for i in range(5):
            problem = diagnosability.generate_sat_problem((f1, f2), i)
            solver  = SatSolverFactory.create()
            cnf     = problem.to_cnf()
            solver += cnf
            solver.polarity(cnf, Polarity.POSITIVE)
            self.assertEqual(SatSolverResult.UNSATISFIABLE, solver.solve())
             
        f1 = Node.from_ptr(parse_simple_expression("status = active"))
        f2 = Node.from_ptr(parse_simple_expression("status = highlight"))
         
        for i in range(1, 4): 
            # length zero has no input => only an initial state and the 
            # diagnosability condition is not checked
            problem = diagnosability.generate_sat_problem((f1, f2), i)
            solver  = SatSolverFactory.create()
            cnf     = problem.to_cnf()
            solver += cnf
            solver.polarity(cnf, Polarity.POSITIVE)
            self.assertEqual(SatSolverResult.SATISFIABLE, solver.solve())

    def test_verify_exactly(self):
        f1 = Node.from_ptr(parse_simple_expression("status = active"))
        f2 = Node.from_ptr(parse_simple_expression("status = inactive"))
        
        for i in range(5):
            res = diagnosability.verify_for_size_exactly_k((f1, f2), i)
            self.assertEqual("No Violation", res)
        
        f1 = Node.from_ptr(parse_simple_expression("status = active"))
        f2 = Node.from_ptr(parse_simple_expression("status = highlight"))
        
        res = diagnosability.verify_for_size_exactly_k((f1, f2), 0)
        self.assertEqual("No Violation", res)
        
        res = diagnosability.verify_for_size_exactly_k((f1, f2), 1)
        self.assertIsInstance(res, Trace)
        
        res = diagnosability.verify_for_size_exactly_k((f1, f2), 2)
        self.assertIsInstance(res, Trace)
        
        res = diagnosability.verify_for_size_exactly_k((f1, f2), 3)
        self.assertIsInstance(res, Trace)
        