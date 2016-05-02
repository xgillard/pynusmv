'''
This module tests the behavior of the functionalities defined in the parsing
module :mod:`tools.bmcLTL.parsing`
'''
from unittest              import TestCase

from tools.bmcLTL          import parsing 

class TestParsing(TestCase):
    
    def test_parse_variable(self):
        ast = parsing.parseLTL("phi")
        self.assertEqual("Variable(phi)", str(ast))
    
    def test_parse_constant(self):
        ast = parsing.parseLTL("TRUE")
        self.assertEqual("Constant(TRUE)", str(ast))
        #
        ast = parsing.parseLTL("FALSE")
        self.assertEqual("Constant(FALSE)", str(ast))
        
    def test_parse_not(self):
        ast = parsing.parseLTL("! phi")
        self.assertEqual("(Not Variable(phi))", str(ast))
        
        # spacing is irrelevant
        ast = parsing.parseLTL("!phi")
        self.assertEqual("(Not Variable(phi))", str(ast))
        
        # can be chained
        ast = parsing.parseLTL("! ! ! phi")
        self.assertEqual("(Not (Not (Not Variable(phi))))", str(ast))
        
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("!!!phi")
        self.assertEqual("(Not (Not (Not Variable(phi))))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("!TRUE")
        self.assertEqual("(Not Constant(TRUE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("!(a | b)")
        self.assertEqual("(Not (Variable(a) Or Variable(b)))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("![]a")
        self.assertEqual("(Not (Globally Variable(a)))", str(ast))

    def test_parse_and(self):
        ast = parsing.parseLTL("phi & psi")
        self.assertEqual("(Variable(phi) And Variable(psi))", str(ast))
        
        # spacing is irrelevant
        ast = parsing.parseLTL("phi&psi")
        self.assertEqual("(Variable(phi) And Variable(psi))", str(ast))
        
        # can be chained (right associative)
        ast = parsing.parseLTL("phi&psi&chi")
        self.assertEqual("(Variable(phi) And (Variable(psi) And Variable(chi)))", str(ast))
        
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("phi & psi & chi")
        self.assertEqual("(Variable(phi) And (Variable(psi) And Variable(chi)))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("TRUE & FALSE")
        self.assertEqual("(Constant(TRUE) And Constant(FALSE))", str(ast))
        ast = parsing.parseLTL("TRUE & alpha")
        self.assertEqual("(Constant(TRUE) And Variable(alpha))", str(ast))
        ast = parsing.parseLTL("alpha & FALSE")
        self.assertEqual("(Variable(alpha) And Constant(FALSE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("(a | b) & x")
        self.assertEqual("((Variable(a) Or Variable(b)) And Variable(x))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("[]a & <>b")
        self.assertEqual("(Globally (Variable(a) And (Eventually Variable(b))))", str(ast))
        ast = parsing.parseLTL("[]a & b")
        self.assertEqual("(Globally (Variable(a) And Variable(b)))", str(ast))
        ast = parsing.parseLTL("a & <>b")
        self.assertEqual("(Variable(a) And (Eventually Variable(b)))", str(ast))
        
    def test_parse_or(self):
        ast = parsing.parseLTL("phi | psi")
        self.assertEqual("(Variable(phi) Or Variable(psi))", str(ast))
        # spacing is irrelevant
        ast = parsing.parseLTL("phi|psi")
        self.assertEqual("(Variable(phi) Or Variable(psi))", str(ast))
        # can be chained (right associative)
        ast = parsing.parseLTL("phi | psi | chi")
        self.assertEqual("(Variable(phi) Or (Variable(psi) Or Variable(chi)))", str(ast))
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("phi|psi|chi")
        self.assertEqual("(Variable(phi) Or (Variable(psi) Or Variable(chi)))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("TRUE | FALSE")
        self.assertEqual("(Constant(TRUE) Or Constant(FALSE))", str(ast))
        ast = parsing.parseLTL("TRUE | alpha")
        self.assertEqual("(Constant(TRUE) Or Variable(alpha))", str(ast))
        ast = parsing.parseLTL("alpha | FALSE")
        self.assertEqual("(Variable(alpha) Or Constant(FALSE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("(a | b) | x")
        self.assertEqual("((Variable(a) Or Variable(b)) Or Variable(x))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("[]a | <>b")
        self.assertEqual("(Globally (Variable(a) Or (Eventually Variable(b))))", str(ast))
        ast = parsing.parseLTL("[]a | b")
        self.assertEqual("(Globally (Variable(a) Or Variable(b)))", str(ast))
        ast = parsing.parseLTL("a | <>b")
        self.assertEqual("(Variable(a) Or (Eventually Variable(b)))", str(ast))
        
    def test_parse_imply(self):
        ast = parsing.parseLTL("phi => psi")
        self.assertEqual("(Variable(phi) Imply Variable(psi))", str(ast))
        # spacing is irrelevant
        ast = parsing.parseLTL("phi=>psi")
        self.assertEqual("(Variable(phi) Imply Variable(psi))", str(ast))
        # can be chained (right associative)
        ast = parsing.parseLTL("phi => psi => chi")
        self.assertEqual("(Variable(phi) Imply (Variable(psi) Imply Variable(chi)))", str(ast))
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("phi=>psi=>chi")
        self.assertEqual("(Variable(phi) Imply (Variable(psi) Imply Variable(chi)))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("TRUE => FALSE")
        self.assertEqual("(Constant(TRUE) Imply Constant(FALSE))", str(ast))
        ast = parsing.parseLTL("TRUE => alpha")
        self.assertEqual("(Constant(TRUE) Imply Variable(alpha))", str(ast))
        ast = parsing.parseLTL("alpha => FALSE")
        self.assertEqual("(Variable(alpha) Imply Constant(FALSE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("(a | b) => x")
        self.assertEqual("((Variable(a) Or Variable(b)) Imply Variable(x))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("[]a => <>b")
        self.assertEqual("(Globally (Variable(a) Imply (Eventually Variable(b))))", str(ast))
        ast = parsing.parseLTL("[]a => b")
        self.assertEqual("(Globally (Variable(a) Imply Variable(b)))", str(ast))
        ast = parsing.parseLTL("a => <>b")
        self.assertEqual("(Variable(a) Imply (Eventually Variable(b)))", str(ast))
        
    def test_parse_iff(self):
        ast = parsing.parseLTL("phi <=> psi")
        self.assertEqual("(Variable(phi) Equiv Variable(psi))", str(ast))
        # spacing is irrelevant
        ast = parsing.parseLTL("phi<=>psi")
        self.assertEqual("(Variable(phi) Equiv Variable(psi))", str(ast))
        # can be chained (right associative)
        ast = parsing.parseLTL("phi <=> psi <=> chi")
        self.assertEqual("(Variable(phi) Equiv (Variable(psi) Equiv Variable(chi)))", str(ast))
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("phi<=>psi<=>chi")
        self.assertEqual("(Variable(phi) Equiv (Variable(psi) Equiv Variable(chi)))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("TRUE <=> FALSE")
        self.assertEqual("(Constant(TRUE) Equiv Constant(FALSE))", str(ast))
        ast = parsing.parseLTL("TRUE <=> alpha")
        self.assertEqual("(Constant(TRUE) Equiv Variable(alpha))", str(ast))
        ast = parsing.parseLTL("alpha <=> FALSE")
        self.assertEqual("(Variable(alpha) Equiv Constant(FALSE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("(a | b) <=> x")
        self.assertEqual("((Variable(a) Or Variable(b)) Equiv Variable(x))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("[]a <=> <>b")
        self.assertEqual("(Globally (Variable(a) Equiv (Eventually Variable(b))))", str(ast))
        ast = parsing.parseLTL("[]a <=> b")
        self.assertEqual("(Globally (Variable(a) Equiv Variable(b)))", str(ast))
        ast = parsing.parseLTL("a <=> <>b")
        self.assertEqual("(Variable(a) Equiv (Eventually Variable(b)))", str(ast))
        
    def test_parse_globally(self):
        ast = parsing.parseLTL("[] phi")
        self.assertEqual("(Globally Variable(phi))", str(ast))
        
        # spacing is irrelevant
        ast = parsing.parseLTL("[]phi")
        self.assertEqual("(Globally Variable(phi))", str(ast))
        
        # can be chained
        ast = parsing.parseLTL("[] [] [] phi")
        self.assertEqual("(Globally (Globally (Globally Variable(phi))))", str(ast))
        
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("[][][]phi")
        self.assertEqual("(Globally (Globally (Globally Variable(phi))))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("[]TRUE")
        self.assertEqual("(Globally Constant(TRUE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("[](a | b)")
        self.assertEqual("(Globally (Variable(a) Or Variable(b)))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("[]<>a")
        self.assertEqual("(Globally (Eventually Variable(a)))", str(ast))
    
    def test_parse_eventually(self):
        ast = parsing.parseLTL("<> phi")
        self.assertEqual("(Eventually Variable(phi))", str(ast))
        
        # spacing is irrelevant
        ast = parsing.parseLTL("<>phi")
        self.assertEqual("(Eventually Variable(phi))", str(ast))
        
        # can be chained
        ast = parsing.parseLTL("<> <> <> phi")
        self.assertEqual("(Eventually (Eventually (Eventually Variable(phi))))", str(ast))
        
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("<><><>phi")
        self.assertEqual("(Eventually (Eventually (Eventually Variable(phi))))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("<>TRUE")
        self.assertEqual("(Eventually Constant(TRUE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("<>(a | b)")
        self.assertEqual("(Eventually (Variable(a) Or Variable(b)))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("<>[]a")
        self.assertEqual("(Eventually (Globally Variable(a)))", str(ast))
        
    def test_parse_next(self):
        ast = parsing.parseLTL("() phi")
        self.assertEqual("(Next Variable(phi))", str(ast))
        
        # spacing is irrelevant
        ast = parsing.parseLTL("()phi")
        self.assertEqual("(Next Variable(phi))", str(ast))
        
        # can be chained
        ast = parsing.parseLTL("() () () phi")
        self.assertEqual("(Next (Next (Next Variable(phi))))", str(ast))
        
        # space is irrelevant (even when chained)
        ast = parsing.parseLTL("()()()phi")
        self.assertEqual("(Next (Next (Next Variable(phi))))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("()TRUE")
        self.assertEqual("(Next Constant(TRUE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("()(a | b)")
        self.assertEqual("(Next (Variable(a) Or Variable(b)))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("()[]a")
        self.assertEqual("(Next (Globally Variable(a)))", str(ast))
        
    def test_parse_until(self):
        ast = parsing.parseLTL("phi U psi")
        self.assertEqual("(Variable(phi) Until Variable(psi))", str(ast))

        # operator name is case sensitive (cause parsing to end)
        ast = parsing.parseLTL("phi u psi")
        self.assertEqual("Variable(phi)", str(ast))
        
        # spacing is relevant (U is a keyword, not a literal -> space imposed)
        ast = parsing.parseLTL("phiUpsi")
        self.assertEqual("Variable(phiUpsi)", str(ast))
        # can be chained (right associative)
        ast = parsing.parseLTL("phi U psi U chi")
        self.assertEqual("(Variable(phi) Until (Variable(psi) Until Variable(chi)))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("TRUE U FALSE")
        self.assertEqual("(Constant(TRUE) Until Constant(FALSE))", str(ast))
        ast = parsing.parseLTL("TRUE U alpha")
        self.assertEqual("(Constant(TRUE) Until Variable(alpha))", str(ast))
        ast = parsing.parseLTL("alpha U FALSE")
        self.assertEqual("(Variable(alpha) Until Constant(FALSE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("(a | b) U x")
        self.assertEqual("((Variable(a) Or Variable(b)) Until Variable(x))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("[]a U <>b")
        self.assertEqual("(Globally (Variable(a) Until (Eventually Variable(b))))", str(ast))
        ast = parsing.parseLTL("[]a U b")
        self.assertEqual("(Globally (Variable(a) Until Variable(b)))", str(ast))
        ast = parsing.parseLTL("a U <>b")
        self.assertEqual("(Variable(a) Until (Eventually Variable(b)))", str(ast))
        
    def test_parse_weak_until(self):
        ast = parsing.parseLTL("phi W psi")
        self.assertEqual("(Variable(phi) WeakUntil Variable(psi))", str(ast))

        # operator name is case sensitive (cause parsing to end)
        ast = parsing.parseLTL("phi w psi")
        self.assertEqual("Variable(phi)", str(ast))
        
        # spacing is relevant (U is a keyword, not a literal -> space imposed)
        ast = parsing.parseLTL("phiWpsi")
        self.assertEqual("Variable(phiWpsi)", str(ast))
        # can be chained (right associative)
        ast = parsing.parseLTL("phi W psi W chi")
        self.assertEqual("(Variable(phi) WeakUntil (Variable(psi) WeakUntil Variable(chi)))", str(ast))
        
        # it may accept a constant
        ast = parsing.parseLTL("TRUE W FALSE")
        self.assertEqual("(Constant(TRUE) WeakUntil Constant(FALSE))", str(ast))
        ast = parsing.parseLTL("TRUE W alpha")
        self.assertEqual("(Constant(TRUE) WeakUntil Variable(alpha))", str(ast))
        ast = parsing.parseLTL("alpha W FALSE")
        self.assertEqual("(Variable(alpha) WeakUntil Constant(FALSE))", str(ast))
        
        # it may accept a parenthesized expression
        ast = parsing.parseLTL("(a | b) W x")
        self.assertEqual("((Variable(a) Or Variable(b)) WeakUntil Variable(x))", str(ast))
                
        # it may accept a timed expression
        ast = parsing.parseLTL("[]a W <>b")
        self.assertEqual("(Globally (Variable(a) WeakUntil (Eventually Variable(b))))", str(ast))
        ast = parsing.parseLTL("[]a W b")
        self.assertEqual("(Globally (Variable(a) WeakUntil Variable(b)))", str(ast))
        ast = parsing.parseLTL("a W <>b")
        self.assertEqual("(Variable(a) WeakUntil (Eventually Variable(b)))", str(ast))
        
    def test_parse_parenthesized(self):
        # no impact on vars
        ast = parsing.parseLTL("(a)")
        self.assertEqual("Variable(a)", str(ast))
        
        # it permits to change the side-associativity
        # can be chained (right associative)
        ast = parsing.parseLTL("(phi | psi) | chi")
        self.assertEqual("((Variable(phi) Or Variable(psi)) Or Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("(phi & psi) & chi")
        self.assertEqual("((Variable(phi) And Variable(psi)) And Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("(phi => psi) => chi")
        self.assertEqual("((Variable(phi) Imply Variable(psi)) Imply Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("(phi <=> psi) <=> chi")
        self.assertEqual("((Variable(phi) Equiv Variable(psi)) Equiv Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("([]a) & b")
        self.assertEqual("((Globally Variable(a)) And Variable(b))", str(ast))
        
        ast = parsing.parseLTL("(<>a) & b")
        self.assertEqual("((Eventually Variable(a)) And Variable(b))", str(ast))
        
        ast = parsing.parseLTL("([]a) U (<>b)")
        self.assertEqual("((Globally Variable(a)) Until (Eventually Variable(b)))", str(ast))
        
        ast = parsing.parseLTL("([]a) W (<>b)")
        self.assertEqual("((Globally Variable(a)) WeakUntil (Eventually Variable(b)))", str(ast))
    
    def test_parse_brackets(self):
        # no impact on vars
        ast = parsing.parseLTL("[a]")
        self.assertEqual("Variable(a)", str(ast))
        
        # it permits to change the side-associativity
        # can be chained (right associative)
        ast = parsing.parseLTL("[phi | psi] | chi")
        self.assertEqual("((Variable(phi) Or Variable(psi)) Or Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("[phi & psi] & chi")
        self.assertEqual("((Variable(phi) And Variable(psi)) And Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("[phi => psi] => chi")
        self.assertEqual("((Variable(phi) Imply Variable(psi)) Imply Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("[phi <=> psi] <=> chi")
        self.assertEqual("((Variable(phi) Equiv Variable(psi)) Equiv Variable(chi))", str(ast))
        
        ast = parsing.parseLTL("[[]a] & b")
        self.assertEqual("((Globally Variable(a)) And Variable(b))", str(ast))
        
        ast = parsing.parseLTL("[<>a] & b")
        self.assertEqual("((Eventually Variable(a)) And Variable(b))", str(ast))
        
        ast = parsing.parseLTL("[[]a] U [<>b]")
        self.assertEqual("((Globally Variable(a)) Until (Eventually Variable(b)))", str(ast))
        
        ast = parsing.parseLTL("[[]a] W [<>b]")
        self.assertEqual("((Globally Variable(a)) WeakUntil (Eventually Variable(b)))", str(ast))
        
    def test_parenthesis_and_brackets_can_be_mixed(self):
        ast = parsing.parseLTL("[](<> [a U b])")
        self.assertEqual("(Globally (Eventually (Variable(a) Until Variable(b))))", str(ast))
        