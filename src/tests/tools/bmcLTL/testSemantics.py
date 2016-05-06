'''
This test module validates the behavior of the BE generation translating the
bounded semantics of LTL as defined in :mod:`tools.bmcLTL.ast`
'''

from unittest                    import TestCase
from tests                       import utils as tests
from pynusmv.init                import init_nusmv, deinit_nusmv
from pynusmv.glob                import load_from_file 
from pynusmv.bmc.glob            import go_bmc, bmc_exit, master_be_fsm
from pynusmv.be.expression       import Be 
from tools.bmcLTL                import ast
from tools.bmcLTL.parsing        import parseLTL

from pynusmv.bmc                 import ltlspec
from pynusmv.bmc                 import utils as bmcutils
from pynusmv.parser              import parse_ltl_spec
from pynusmv.node                import Node

class TestSemantics(TestCase):
    
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
    
    def test_successor(self):
        # when time is smaller than bound
        self.assertEqual(4, ast.successor(3, 5, 2))
        # when time reaches the bound and needs to jump back to the beginning
        # of the loop.
        self.assertEqual(2, ast.successor(5, 5, 2))
    
    def test_loop_condition(self):
        enc   = self.enc
        a     = enc.by_name['a']
        b     = enc.by_name['b']
        
        # self looping on zero
        _,k,l = 0,0,0
        loop_cond = ast.loop_condition(enc, k, l)
        # note: frozen and ivar are not taken into account
        manual    = a.at_time[0].boolean_expression.iff(a.at_time[0].boolean_expression) &\
                    b.at_time[0].boolean_expression.iff(b.at_time[0].boolean_expression)
        nusmv     = bmcutils.loop_condition(enc, k, l)
                
        s_tool   = tests.canonical_cnf(loop_cond)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
        
        # simple k-l loop 5 - 0
        _,k,l = 0,5,0
        loop_cond = ast.loop_condition(enc, k, l)
        
        manual    = a.at_time[5].boolean_expression.iff(a.at_time[0].boolean_expression) &\
                    b.at_time[5].boolean_expression.iff(b.at_time[0].boolean_expression)
        nusmv     = bmcutils.loop_condition(enc, k, l)
                
        s_tool   = tests.canonical_cnf(loop_cond)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
        
        # simple k-l loop 5 - 0
        _,k,l = 0,5,2
        loop_cond = ast.loop_condition(enc, k, l)
        
        manual    = a.at_time[5].boolean_expression.iff(a.at_time[2].boolean_expression) &\
                    b.at_time[5].boolean_expression.iff(b.at_time[2].boolean_expression)
        nusmv     = bmcutils.loop_condition(enc, k, l)
                
        s_tool   = tests.canonical_cnf(loop_cond)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
        
    
    def test_constant_noloop(self):
        expr = ast.Constant("TRUE")
        self.assertEqual(Be.true(self.mgr), expr.semantic_no_loop(self.enc, 0, 5))
        
        expr = ast.Constant("FALSE")
        self.assertEqual(Be.false(self.mgr), expr.semantic_no_loop(self.enc, 0, 5))
        
    def test_constant_with_loop(self):
        expr = ast.Constant("TRUE")
        self.assertEqual(Be.true(self.mgr), expr.semantic_with_loop(self.enc, 0, 5, 2))
        
        expr = ast.Constant("FALSE")
        self.assertEqual(Be.false(self.mgr), expr.semantic_with_loop(self.enc, 0, 5, 2))
        
    def test_variable_noloop(self):
        expr = ast.Variable("a")
        self.assertEqual(
                self.enc.by_name['a'].at_time[3].boolean_expression, 
                expr.semantic_no_loop(self.enc, 3, 5))
        # bound has little impact on the BE for a variable
        self.assertEqual(
                self.enc.by_name['a'].at_time[3].boolean_expression, 
                expr.semantic_no_loop(self.enc, 3, 3))
    
    def test_variable_withloop(self):
        # bound and loop have no impact on the way BE for a variable is 
        # generated (successor index not enforced)
        expr = ast.Variable("a")
        self.assertEqual(
                self.enc.by_name['a'].at_time[3].boolean_expression, 
                expr.semantic_with_loop(self.enc, 3, 5, 2))
        self.assertEqual(
                self.enc.by_name['a'].at_time[3].boolean_expression, 
                expr.semantic_with_loop(self.enc, 3, 3, 3))
    
    def test_not_noloop(self):
        # constant
        expr = ast.Not(ast.Constant("TRUE"))
        self.assertEqual(
            ast.Constant("FALSE").semantic_no_loop(self.enc, 2, 3),
            expr.semantic_no_loop(self.enc, 2, 3))
        
        # variable
        expr = ast.Not(ast.Variable("a"))
        self.assertEqual(
            -ast.Variable("a").semantic_no_loop(self.enc, 2, 3),
            expr.semantic_no_loop(self.enc, 2, 3))
        
        # not
        expr = ast.Not(ast.Not(ast.Variable("a")))
        self.assertEqual(
            ast.Variable("a").semantic_no_loop(self.enc, 2, 3),
            expr.semantic_no_loop(self.enc, 2, 3))
        
        # expression: and
        expr = ast.Not(ast.And(ast.Variable("a"), ast.Variable("b")))
        self.assertEqual(
            -( ast.Variable("a").semantic_no_loop(self.enc, 2, 3) 
             & ast.Variable("b").semantic_no_loop(self.enc, 2, 3)),
            expr.semantic_no_loop(self.enc, 2, 3))
        
        # expression: weak until
        expr = ast.WeakUntil(ast.Variable("a"), ast.Variable("b"))
        nega = ast.Not(expr)
        self.assertEqual(
            -expr.semantic_no_loop(self.enc, 2, 3),
             nega.semantic_no_loop(self.enc, 2, 3))
    
    def test_not_with_loop(self):
        # constant
        expr = ast.Not(ast.Constant("TRUE"))
        self.assertEqual(
            ast.Constant("FALSE").semantic_with_loop(self.enc, 2, 3, 1),
            expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        # variable
        expr = ast.Not(ast.Variable("a"))
        self.assertEqual(
            -ast.Variable("a").semantic_with_loop(self.enc, 2, 3, 1),
            expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        # not
        expr = ast.Not(ast.Not(ast.Variable("a")))
        self.assertEqual(
            ast.Variable("a").semantic_with_loop(self.enc, 2, 3, 1),
            expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        # expression: and
        expr = ast.Not(ast.And(ast.Variable("a"), ast.Variable("b")))
        self.assertEqual(
            -( ast.Variable("a").semantic_with_loop(self.enc, 2, 3, 1) 
             & ast.Variable("b").semantic_with_loop(self.enc, 2, 3, 1)),
            expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        # expression: weak until
        expr = ast.WeakUntil(ast.Variable("a"), ast.Variable("b"))
        nega = ast.Not(expr)
        self.assertEqual(
            -expr.semantic_with_loop(self.enc, 2, 3, 1),
             nega.semantic_with_loop(self.enc, 2, 3, 1))
        
    def test_and_noloop(self):
        expr = ast.And(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                ( ast.Variable("a").semantic_no_loop(self.enc, 2, 3)
                & ast.Variable("b").semantic_no_loop(self.enc, 2, 3)),
                expr.semantic_no_loop(self.enc, 2, 3))
        
        expr = ast.And(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                ( ast.Globally(ast.Variable("a")).semantic_no_loop(self.enc, 2, 3)
                & ast.Eventually(ast.Variable("b")).semantic_no_loop(self.enc, 2, 3)),
                expr.semantic_no_loop(self.enc, 2, 3))
    
    def test_and_with_loop(self):
        expr = ast.And(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                ( ast.Variable("a").semantic_with_loop(self.enc, 2, 3, 1)
                & ast.Variable("b").semantic_with_loop(self.enc, 2, 3, 1)),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        expr = ast.And(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                ( ast.Globally(ast.Variable("a")).semantic_with_loop(self.enc, 2, 3, 1)
                & ast.Eventually(ast.Variable("b")).semantic_with_loop(self.enc, 2, 3, 1)),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        
    def test_or_noloop(self):
        expr = ast.Or(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                ( ast.Variable("a").semantic_no_loop(self.enc, 2, 3)
                | ast.Variable("b").semantic_no_loop(self.enc, 2, 3)),
                expr.semantic_no_loop(self.enc, 2, 3))
        
        expr = ast.Or(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                ( ast.Globally(ast.Variable("a")).semantic_no_loop(self.enc, 2, 3)
                | ast.Eventually(ast.Variable("b")).semantic_no_loop(self.enc, 2, 3)),
                expr.semantic_no_loop(self.enc, 2, 3))
    
    def test_or_with_loop(self):
        expr = ast.Or(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                ( ast.Variable("a").semantic_with_loop(self.enc, 2, 3, 1)
                | ast.Variable("b").semantic_with_loop(self.enc, 2, 3, 1)),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        expr = ast.Or(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                ( ast.Globally(ast.Variable("a")).semantic_with_loop(self.enc, 2, 3, 1)
                | ast.Eventually(ast.Variable("b")).semantic_with_loop(self.enc, 2, 3, 1)),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
    def test_imply_noloop(self):
        expr = ast.Imply(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                ( ast.Variable("a").semantic_no_loop(self.enc, 2, 3).imply(
                  ast.Variable("b").semantic_no_loop(self.enc, 2, 3))),
                expr.semantic_no_loop(self.enc, 2, 3))
        
        expr = ast.Imply(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                (-ast.Globally(ast.Variable("a")).semantic_no_loop(self.enc, 2, 3)
                | ast.Eventually(ast.Variable("b")).semantic_no_loop(self.enc, 2, 3)),
                expr.semantic_no_loop(self.enc, 2, 3))
    
    def test_imply_with_loop(self):
        expr = ast.Imply(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                (-ast.Variable("a").semantic_with_loop(self.enc, 2, 3, 1)
                | ast.Variable("b").semantic_with_loop(self.enc, 2, 3, 1)),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        expr = ast.Imply(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                (-ast.Globally(ast.Variable("a")).semantic_with_loop(self.enc, 2, 3, 1)
                | ast.Eventually(ast.Variable("b")).semantic_with_loop(self.enc, 2, 3, 1)),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
    def test_iff_noloop(self):
        expr = ast.Equiv(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                ( ast.Variable("a").semantic_no_loop(self.enc, 2, 3).iff(
                  ast.Variable("b").semantic_no_loop(self.enc, 2, 3))),
                expr.semantic_no_loop(self.enc, 2, 3))
        
        expr = ast.Equiv(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                ( ast.Globally(ast.Variable("a")).semantic_no_loop(self.enc, 2, 3).iff(
                  ast.Eventually(ast.Variable("b")).semantic_no_loop(self.enc, 2, 3))),
                expr.semantic_no_loop(self.enc, 2, 3))
        
    def test_iff_with_loop(self):
        expr = ast.Equiv(ast.Variable("a"), ast.Variable("b"))
        self.assertEqual(
                ( ast.Variable("a").semantic_with_loop(self.enc, 2, 3, 1).iff(
                  ast.Variable("b").semantic_with_loop(self.enc, 2, 3, 1))),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
        expr = ast.Equiv(ast.Globally(ast.Variable("a")), ast.Eventually(ast.Variable("b")))
        self.assertEqual(
                ( ast.Globally(ast.Variable("a")).semantic_with_loop(self.enc, 2, 3, 1).iff(
                  ast.Eventually(ast.Variable("b")).semantic_with_loop(self.enc, 2, 3, 1))),
                expr.semantic_with_loop(self.enc, 2, 3, 1))
        
    def test_until_noloop(self):
        enc  = self.enc
        a    = ast.Variable("a")
        b    = ast.Variable("b")

        expr = ast.Until(a, b)
        tool = expr.semantic_no_loop(enc, 0, 2)
        
        manual = ( b.semantic_no_loop(enc, 0, 2) 
               | (a.semantic_no_loop(enc, 0, 2) & (b.semantic_no_loop(enc, 1, 2)
               | (a.semantic_no_loop(enc, 1, 2) & (b.semantic_no_loop(enc, 2, 2))))))
        
        
        spec  = Node.from_ptr(parse_ltl_spec("a U b"))
        nusmv = ltlspec.bounded_semantics(self.fsm, spec, bound=2, loop=bmcutils.no_loopback())
        
        # normalized string representation of the BE's (make them comparable)
        s_tool  = tests.canonical_cnf(tool)
        s_nusmv = tests.canonical_cnf(nusmv)
        s_manual= tests.canonical_cnf(manual)
        
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
        
    def test_until_with_loop(self):
        enc  = self.enc
        i,k,l= 0,2,0
        a    = ast.Variable("a")
        b    = ast.Variable("b")

        expr = ast.Until(a, b)
        tool = expr.semantic_with_loop(enc, i,k,l)
        
        manual = b.semantic_with_loop(enc, i, k, l) | \
                    (a.semantic_with_loop(enc, i, k, l) & b.semantic_with_loop(enc, i+1, k, l))
        
        
        spec  = Node.from_ptr(parse_ltl_spec("a U b"))
        nusmv = ltlspec.bounded_semantics(self.fsm, spec, bound=k, loop=l)
        
        tool   &= bmcutils.loop_condition(enc, k, l)
        manual &= bmcutils.loop_condition(enc, k, l)
        
        # normalized string representation of the BE's (make them comparable)
        s_tool  = tests.canonical_cnf(tool)
        s_nusmv = tests.canonical_cnf(nusmv)
        s_manual= tests.canonical_cnf(manual)
        
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
        
    def test_weak_until_noloop(self):
        enc  = self.enc
        a    = ast.Variable("a")
        b    = ast.Variable("b")

        expr = ast.WeakUntil(a, b)
        tool = expr.semantic_no_loop(enc, 0, 2)
        
        manual = ( b.semantic_no_loop(enc, 0, 2) 
               | (a.semantic_no_loop(enc, 0, 2) & (b.semantic_no_loop(enc, 1, 2)
               | (a.semantic_no_loop(enc, 1, 2) & (b.semantic_no_loop(enc, 2, 2))))))
        
        
        spec  = Node.from_ptr(parse_ltl_spec("a U b"))
        nusmv = ltlspec.bounded_semantics(self.fsm, spec, bound=2, loop=bmcutils.no_loopback())
        
        # normalized string representation of the BE's (make them comparable)
        s_tool  = tests.canonical_cnf(tool)
        s_nusmv = tests.canonical_cnf(nusmv)
        s_manual= tests.canonical_cnf(manual)
        
        self.assertEqual(s_tool, s_manual)
        self.assertEqual(s_tool, s_nusmv)
        
    def test_weak_until_with_loop(self):
        enc  = self.enc
        mgr  = enc.manager
        i,k,l= 0,2,0
        a    = ast.Variable("a")
        b    = ast.Variable("b")

        expr = ast.WeakUntil(a, b)
        tool = expr.semantic_with_loop(enc, i,k,l)
        
        manual = b.semantic_with_loop(enc, i, k, l) | \
                    (a.semantic_with_loop(enc, i, k, l) & \
                        (b.semantic_with_loop(enc, i+1, k, l) | \
                            a.semantic_with_loop(enc, i+1, k, l) & Be.true(mgr)
                        )
                     )
        
        # normalized string representation of the BE's (make them comparable)
        s_tool  = tests.canonical_cnf(tool)
        s_manual= tests.canonical_cnf(manual)
        
        self.assertEqual(s_tool, s_manual)
        
    def test_globally_no_loop(self):
        i,k     = 0,2
        enc     = self.enc
        mgr     = enc.manager
        a       = ast.Variable("a")
        formula = ast.Globally(a)
        
        tool = formula.semantic_no_loop(enc, i, k)
        self.assertEqual(Be.false(mgr), tool)
        
    def test_globally_with_loop(self):
        i,k,l   = 0,2,0
        enc     = self.enc
        a       = ast.Variable("a")
        formula = ast.Globally(a)
        tool    = formula.semantic_with_loop(enc, i, k, l) &\
                    bmcutils.loop_condition(enc, k, l)
        
        nusmv   = ltlspec.bounded_semantics(
                        self.fsm, Node.from_ptr(parse_ltl_spec("G a")), k, l)
        
        manual  = a.semantic_with_loop(enc, i, k, l)   &\
                  a.semantic_with_loop(enc, i+1, k, l) &\
                  bmcutils.loop_condition(enc, k, l)
        
        # normalized string representation of the BE's (make them comparable)
        s_tool  = tests.canonical_cnf(tool)
        s_nusmv = tests.canonical_cnf(nusmv)
        s_manual= tests.canonical_cnf(manual)
        
        self.assertEqual(s_nusmv,  s_tool)
        self.assertEqual(s_manual, s_tool)
        
    def test_eventually_no_loop(self):
        i,k     = 0,2
        enc     = self.enc
        a       = ast.Variable("a")
        formula = ast.Eventually(a)
        
        tool    = formula.semantic_no_loop(enc, i, k)
        
        manual  = a.semantic_no_loop(enc, i+2, k)   |\
                  a.semantic_no_loop(enc, i+1, k) |\
                  a.semantic_no_loop(enc, i, k) 
        
        nusmv   = ltlspec.bounded_semantics(
                    self.fsm, Node.from_ptr(parse_ltl_spec("F a")), 
                    bound = k, 
                    loop  = bmcutils.no_loopback())
        
        # normalized string representation of the BE's (make them comparable)
        s_tool  = tests.canonical_cnf(tool)
        s_nusmv = tests.canonical_cnf(nusmv)
        s_manual= tests.canonical_cnf(manual)
        
        self.assertEqual(s_nusmv,  s_tool)
        self.assertEqual(s_manual, s_tool)
        
    def test_eventually_with_loop(self):
        i,k,l   = 0,2,0
        enc     = self.enc
        a       = ast.Variable("a")
        formula = ast.Eventually(a)
        
        tool    = formula.semantic_with_loop(enc, i, k, l)
        
        manual  = a.semantic_with_loop(enc, i+1, k, l) |\
                  a.semantic_with_loop(enc, i  , k, l) 
        
        nusmv   = ltlspec.bounded_semantics(
                    self.fsm, Node.from_ptr(parse_ltl_spec("F a")), 
                    bound = k, 
                    loop  = l)
        
        # normalized string representation of the BE's (make them comparable)
        loop_cond = bmcutils.loop_condition(enc, k, l)
        s_tool  = tests.canonical_cnf(tool   & loop_cond)
        s_manual= tests.canonical_cnf(manual & loop_cond)
        s_nusmv = tests.canonical_cnf(nusmv)
        
        self.assertEqual(s_nusmv,  s_tool)
        self.assertEqual(s_manual, s_tool)
        
    def test_next_noloop(self):
        i,k     = 0,2
        enc     = self.enc
        # One step
        a       = ast.Variable("a")
        formula = ast.Next(a)
        tool    = formula.semantic_no_loop(enc, i, k)
        manual  = a.semantic_no_loop(enc, 1, k)
        nusmv   = ltlspec.bounded_semantics(self.fsm, 
                                            Node.from_ptr(parse_ltl_spec("X a")),
                                            bound = k, 
                                            loop  = bmcutils.no_loopback())
        
        s_tool   = tests.canonical_cnf(tool)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
        
        self.assertEqual(s_tool, s_nusmv)
        self.assertEqual(s_tool, s_manual)
        
        # two steps
        formula = ast.Next(ast.Next(a))
        tool    = formula.semantic_no_loop(enc, i, k)
        manual  = a.semantic_no_loop(enc, 2, k)
        nusmv   = ltlspec.bounded_semantics(self.fsm, 
                                            Node.from_ptr(parse_ltl_spec("X X a")),
                                            bound = k, 
                                            loop  = bmcutils.no_loopback())
        
        s_tool   = tests.canonical_cnf(tool)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
        
        self.assertEqual(s_tool, s_nusmv)
        self.assertEqual(s_tool, s_manual)
        
        # Three steps (getting over k)
        formula = ast.Next(ast.Next(ast.Next(a)))
        tool    = formula.semantic_no_loop(enc, i, k)
        manual  = Be.false(enc.manager)
        nusmv   = ltlspec.bounded_semantics(self.fsm, 
                                            Node.from_ptr(parse_ltl_spec("X X X a")),
                                            bound = k, 
                                            loop  = bmcutils.no_loopback())
        
        s_tool   = tests.canonical_cnf(tool)
        s_manual = tests.canonical_cnf(manual)
        s_nusmv  = tests.canonical_cnf(nusmv)
        
        self.assertEqual(s_tool, s_nusmv)
        self.assertEqual(s_tool, s_manual)
        
    def test_next_with_loop(self):
        i,k,l   = 0,2,0
        enc     = self.enc
        
        # One step
        a       = ast.Variable("a")
        formula = ast.Next(a)
        tool    = formula.semantic_with_loop(enc, i, k, l)
        manual  = a.semantic_with_loop(enc, 1, k, l)
        nusmv   = ltlspec.bounded_semantics(self.fsm, 
                                            Node.from_ptr(parse_ltl_spec("X a")),
                                            bound = k, 
                                            loop  = l)
        
        loop_cond = bmcutils.loop_condition(enc, k, l)
        s_tool  = tests.canonical_cnf(tool   & loop_cond)
        s_manual= tests.canonical_cnf(manual & loop_cond)
        s_nusmv = tests.canonical_cnf(nusmv)
        
        self.assertEqual(s_tool, s_nusmv)
        self.assertEqual(s_tool, s_manual)
        
        # two steps
        formula = ast.Next(ast.Next(a))
        tool    = formula.semantic_with_loop(enc, i, k, l)
        manual  = a.semantic_with_loop(enc, 0, k, l)
        nusmv   = ltlspec.bounded_semantics(self.fsm, 
                                            Node.from_ptr(parse_ltl_spec("X X a")),
                                            bound = k, 
                                            loop  = l)
        
        loop_cond = bmcutils.loop_condition(enc, k, l)
        s_tool  = tests.canonical_cnf(tool   & loop_cond)
        s_manual= tests.canonical_cnf(manual & loop_cond)
        s_nusmv = tests.canonical_cnf(nusmv)
        
        self.assertEqual(s_tool, s_nusmv)
        self.assertEqual(s_tool, s_manual)
         
        # Three steps (getting over k)
        formula = ast.Next(ast.Next(ast.Next(a)))
        tool    = formula.semantic_with_loop(enc, i, k, l)
        manual  = a.semantic_with_loop(enc, 1, k, l)
        nusmv   = ltlspec.bounded_semantics(self.fsm, 
                                            Node.from_ptr(parse_ltl_spec("X X X a")),
                                            bound = k, 
                                            loop  = l)
        
        loop_cond = bmcutils.loop_condition(enc, k, l)
        s_tool  = tests.canonical_cnf(tool   & loop_cond)
        s_manual= tests.canonical_cnf(manual & loop_cond)
        s_nusmv = tests.canonical_cnf(nusmv)
        
        self.assertEqual(s_tool, s_nusmv)
        self.assertEqual(s_tool, s_manual)
    
    
    def validate_bounded_semantics(self, bound, custom_text, nusmv_text):
        fsm     = self.fsm
        # formulae
        formula = parseLTL(custom_text)
        fml_node= Node.from_ptr(parse_ltl_spec(nusmv_text))
        
        tool = formula.bounded_semantics(fsm.encoding, bound)
        smv  = ltlspec.bounded_semantics(fsm, fml_node, bound)
        # canonical forms        
        s_tool  = tests.canonical_cnf(tool)
        s_smv   = tests.canonical_cnf(smv)
         
        self.assertEqual(s_tool, s_smv)
      
    def test_bounded_semantics(self):
        # length 0
        self.validate_bounded_semantics(0, "<>(a <=> !b)", "F (a <-> !b)")
        self.validate_bounded_semantics(0, "[](a <=> !b)", "G (a <-> !b)")
        self.validate_bounded_semantics(0, "(a U b)", "(a U b)")
        self.validate_bounded_semantics(0, "a => () b", "a -> (X b)")
        
        # length 1
        self.validate_bounded_semantics(1, "<>(a <=> !b)", "F (a <-> !b)")
        self.validate_bounded_semantics(1, "[](a <=> !b)", "G (a <-> !b)")
        self.validate_bounded_semantics(1, "(a U b)", "(a U b)")
        self.validate_bounded_semantics(1, "a => () b", "a -> (X b)")
        
        # length 2
        self.validate_bounded_semantics(1, "<>(a <=> !b)", "F (a <-> !b)")
        self.validate_bounded_semantics(1, "[](a <=> !b)", "G (a <-> !b)")
        self.validate_bounded_semantics(1, "(a U b)", "(a U b)")
        self.validate_bounded_semantics(1, "a => () b", "a -> (X b)")
        
    def test_nnf_constant(self):
        formula = parseLTL("TRUE")
        self.assertEqual("Constant(TRUE)",  str(formula.nnf(False)))
        self.assertEqual("Constant(FALSE)", str(formula.nnf(True)))
        
    def test_nnf_variable(self):
        formula = parseLTL("a")
        self.assertEqual("Variable(a)",       str(formula.nnf(False)))
        self.assertEqual("(Not Variable(a))", str(formula.nnf(True)))
        
    def test_nnf_not(self):
        formula = parseLTL("!a")
        self.assertEqual("Variable(a)",       str(formula.nnf(True)))
        self.assertEqual("(Not Variable(a))", str(formula.nnf(False)))
    
    def test_nnf_and(self):
        # when the operands dont need to be nnf-ed
        formula = parseLTL("a & b")

        negated = "((Not Variable(a)) Or (Not Variable(b)))"
        self.assertEqual(negated,       str(formula.nnf(True)))
        
        not_neg = "(Variable(a) And Variable(b))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        # when the operands need to be nnf-ed
        formula = parseLTL("a & !b")

        negated = "((Not Variable(a)) Or Variable(b))"
        self.assertEqual(negated,       str(formula.nnf(True)))
        
        not_neg = "(Variable(a) And (Not Variable(b)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
    
    def test_nnf_or(self):
        # when the operands dont need to be nnf-ed
        formula = parseLTL("a | b")

        negated = "((Not Variable(a)) And (Not Variable(b)))"
        self.assertEqual(negated,       str(formula.nnf(True)))
        
        not_neg = "(Variable(a) Or Variable(b))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        # when the operands need to be nnf-ed
        formula = parseLTL("a | !b")

        negated = "((Not Variable(a)) And Variable(b))"
        self.assertEqual(negated,       str(formula.nnf(True)))
        
        not_neg = "(Variable(a) Or (Not Variable(b)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
    def test_nnf_imply(self):
        # when the operands dont need to be nnf-ed
        formula = parseLTL("a => b")
        
        not_neg = "((Not Variable(a)) Or Variable(b))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "(Variable(a) And (Not Variable(b)))"
        self.assertEqual(negated, str(formula.nnf(True)))
        
        # when the operands need to be nnf-ed
        formula = parseLTL("a => !b")
        
        not_neg = "((Not Variable(a)) Or (Not Variable(b)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "(Variable(a) And Variable(b))"
        self.assertEqual(negated, str(formula.nnf(True)))
    
    def test_nnf_equiv(self):
        # when the operands dont need to be nnf-ed
        formula = parseLTL("a <=> b")
        
        #          (!a | b) & (!b | a)
        not_neg = "(((Not Variable(a)) Or Variable(b)) And ((Not Variable(b)) Or Variable(a)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        #          (a & !b) | (b & !a)
        negated = "((Variable(a) And (Not Variable(b))) Or (Variable(b) And (Not Variable(a))))"
        self.assertEqual(negated, str(formula.nnf(True)))
         
        # when the operands need to be nnf-ed
        formula = parseLTL("a <=> !b")
        
        #          (!a | !b) & (b | a)
        not_neg = "(((Not Variable(a)) Or (Not Variable(b))) And (Variable(b) Or Variable(a)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        #          (a & b) | (!b & !a) 
        negated = "((Variable(a) And Variable(b)) Or ((Not Variable(b)) And (Not Variable(a))))"
        self.assertEqual(negated, str(formula.nnf(True)))
    
    def test_nnf_until(self):
        # rules of pseudo duality:
        #     (p U q) <-> (!q W (!p & !q))
        #     (p W q) <-> (!q U (!p & !q))
        
        # without operands nnfing
        formula = parseLTL("(p U q)")
        not_neg = "(Variable(p) Until Variable(q))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "((Not Variable(q)) WeakUntil ((Not Variable(p)) And (Not Variable(q))))"
        self.assertEqual(negated, str(formula.nnf(True)))
        
        # wit operands nnfing
        formula = parseLTL("((!p) U (!q))")
        not_neg = "((Not Variable(p)) Until (Not Variable(q)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "(Variable(q) WeakUntil (Variable(p) And Variable(q)))"
        self.assertEqual(negated, str(formula.nnf(True)))
                
    def test_nnf_weakuntil(self):
        # rules of pseudo duality:
        #     (p U q) <-> (!q W (!p & !q))
        #     (p W q) <-> (!q U (!p & !q))
        
        # without operands nnfing
        formula = parseLTL("(p W q)")
        not_neg = "(Variable(p) WeakUntil Variable(q))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "((Not Variable(q)) Until ((Not Variable(p)) And (Not Variable(q))))"
        self.assertEqual(negated, str(formula.nnf(True)))
        
        # wit operands nnfing
        formula = parseLTL("((!p) W (!q))")
        not_neg = "((Not Variable(p)) WeakUntil (Not Variable(q)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "(Variable(q) Until (Variable(p) And Variable(q)))"
        self.assertEqual(negated, str(formula.nnf(True)))
        
    def test_nnf_globally(self):
        formula = parseLTL("[] a")
        not_neg = "(Globally Variable(a))"
        self.assertEqual(not_neg, str(formula.nnf(False)))

        negated = "(Eventually (Not Variable(a)))"
        self.assertEqual(negated, str(formula.nnf(True)))
        
        # when members need nnfing too
        formula = parseLTL("[] (!a)")
        not_neg = "(Globally (Not Variable(a)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))

        negated = "(Eventually Variable(a))"
        self.assertEqual(negated, str(formula.nnf(True)))

    def test_nnf_eventually(self):
        formula = parseLTL("<> a")
        not_neg = "(Eventually Variable(a))"
        self.assertEqual(not_neg, str(formula.nnf(False)))

        negated = "(Globally (Not Variable(a)))"
        self.assertEqual(negated, str(formula.nnf(True)))
        
        # when members need nnfing too
        formula = parseLTL("<> (!a)")
        not_neg = "(Eventually (Not Variable(a)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))

        negated = "(Globally Variable(a))"
        self.assertEqual(negated, str(formula.nnf(True)))
    
    def test_nnf_next(self):
        formula = parseLTL("() a")
        # w/o member nnf-ing
        not_neg = "(Next Variable(a))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "(Next (Not Variable(a)))"
        self.assertEqual(negated, str(formula.nnf(True)))
        
        # w/ member nnf-ing
        formula = parseLTL("() !a")
        not_neg = "(Next (Not Variable(a)))"
        self.assertEqual(not_neg, str(formula.nnf(False)))
        
        negated = "(Next Variable(a))"
        self.assertEqual(negated, str(formula.nnf(True)))
    