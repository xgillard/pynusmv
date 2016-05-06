'''
This test module validates the behavior of the SAT problem generation 
translating the bounded semantics verification of LTL properties as defined 
in :mod:`tools.bmcLTL.gen`
'''
from unittest                    import TestCase
from tests                       import utils as tests
from pynusmv.init                import init_nusmv, deinit_nusmv
from pynusmv.glob                import load_from_file 
from pynusmv.bmc.glob            import go_bmc, bmc_exit, master_be_fsm
from tools.bmcLTL                import gen

from pynusmv.bmc                 import ltlspec
from pynusmv.bmc                 import utils as bmcutils
from pynusmv.parser              import parse_ltl_spec
from pynusmv.node                import Node
from tools.bmcLTL.parsing        import parseLTL
from pynusmv.sat                 import SatSolverFactory, Polarity

class TestGen(TestCase):
 
    def setUp(self):
        init_nusmv()
        load_from_file(tests.current_directory(__file__)+"/example.smv")
        go_bmc()
        self.fsm = master_be_fsm()
        self.enc = self.fsm.encoding
        self.mgr = self.enc.manager
      
    def tearDown(self):
        bmc_exit()
        deinit_nusmv()
         
    def test_model_problem(self):
        enc = self.enc
        # no step taken
        bound = 0
         
        tool  = gen.model_problem(self.fsm, bound)
        manual= enc.shift_to_time(self.fsm.init, 0)
         
        nusmv = bmcutils.BmcModel().path(bound, with_init=True)
         
        s_tool   = tests.canonical_cnf(tool)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
         
        self.assertEqual(s_tool, s_nusmv)
        self.assertEqual(s_tool, s_manual)
         
        # one step taken
        bound = 1
         
        tool  = gen.model_problem(self.fsm, bound)
        manual= enc.shift_to_time(self.fsm.trans,0) &\
                enc.shift_to_time(self.fsm.init, 0)
         
        nusmv = bmcutils.BmcModel().path(bound, with_init=True)
         
        s_tool   = tests.canonical_cnf(tool)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
         
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
         
        # two steps
        bound = 2
         
        tool  = gen.model_problem(self.fsm, bound)
        manual= enc.shift_to_time(self.fsm.init, 0) &\
                enc.shift_to_time(self.fsm.trans,0) &\
                enc.shift_to_time(self.fsm.trans,1)
         
        nusmv = bmcutils.BmcModel().path(bound, with_init=True)
         
        s_tool   = tests.canonical_cnf(tool)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
         
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
 
    def satisfiability(self, problem):
        solver = SatSolverFactory.create()
        solver+= problem.to_cnf()
        solver.polarity(problem.to_cnf(), Polarity.POSITIVE)
        return solver.solve()
       
    def validate_generate_problem(self, bound, custom_text, nusmv_text):
        fsm     = self.fsm
        # formulae
        formula = parseLTL(custom_text)
        fml_node= Node.from_ptr(parse_ltl_spec(nusmv_text))
         
        # IMPORTANT NOTE: each instantiation of the problem creates new CNF 
        #   literal which appears in the clauses list (even in canonical form)
        #   hence, the canonical forms of the different instantiations cannot
        #   simply be compared as there is no a priori way to know what CNF 
        #   literal reconcile with what other.
        #   However, the different expressions should all have the exact same
        #   satisfiability. So, that's how this test proceeds.
          
        smv     = ltlspec.generate_ltl_problem(fsm, fml_node, bound)
        tool    = gen.generate_problem(formula, fsm, bound)
        manual  = gen.model_problem(fsm, bound) &\
                  formula.nnf(True).bounded_semantics(fsm.encoding, bound)
         
        sat_smv = self.satisfiability(smv)
        sat_tool= self.satisfiability(tool)
        sat_man = self.satisfiability(manual)
         
        self.assertEqual(sat_tool, sat_man)
        self.assertEqual(sat_tool, sat_smv)
         
    def test_generate_problem(self):
        # length 0
        self.validate_generate_problem(0, "<>(a <=> !b)", "F (a <-> !b)")
        self.validate_generate_problem(0, "[](a <=> !b)", "G (a <-> !b)")
        self.validate_generate_problem(0, "(a U b)", "(a U b)")
        self.validate_generate_problem(0, "a => () b", "a -> (X b)")
        # length 1
        self.validate_generate_problem(1, "<>(a <=> !b)", "F (a <-> !b)")
        self.validate_generate_problem(1, "[](a <=> !b)", "G (a <-> !b)")
        self.validate_generate_problem(1, "(a U b)", "(a U b)")
        self.validate_generate_problem(1, "a => () b", "a -> (X b)")
        # length 2
        self.validate_generate_problem(2, "<>(a <=> !b)", "F (a <-> !b)")
        self.validate_generate_problem(2, "[](a <=> !b)", "G (a <-> !b)")
        self.validate_generate_problem(2, "(a U b)", "(a U b)")
        self.validate_generate_problem(2, "a => () b", "a -> (X b)")
        # length 3
        self.validate_generate_problem(3, "<>(a <=> !b)", "F (a <-> !b)")
        self.validate_generate_problem(3, "[](a <=> !b)", "G (a <-> !b)")
        self.validate_generate_problem(3, "(a U b)", "(a U b)")
        self.validate_generate_problem(3, "a => () b", "a -> (X b)")
        