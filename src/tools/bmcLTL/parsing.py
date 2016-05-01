"""
This module contains the class definition of the symbols and grammar of an LTL
formula
"""

import pyparsing as pp
import tools.bmcLTL.ast as ast

# an internal stack meant to easily resolve the operands of the n-ary expressions
_stack = []

def retpush(x):
    """
    Pushes the symbol `x` on the stack and returns it. (This function is used
    for its side effect only)
    
    :param x: the param to push on the stack
    :return: the parameter `x`
    """
    _stack.append(x)
    return x


###############################################################################
# Symbols and keywords
###############################################################################

# terminals
variable = pp.Regex("[a-zA-Z_@]+[a-zA-Z0-9_@]*").setParseAction(lambda t: retpush(ast.Variable(t[0])))
true     = pp.Keyword("TRUE" ).setParseAction(lambda t: retpush(ast.Constant("TRUE")))
false    = pp.Keyword("FALSE").setParseAction(lambda t: retpush(ast.Constant("FALSE")))

# unary operators
op_not   = pp.Keyword("!")
op_G     = pp.Keyword("[]")
op_F     = pp.Keyword("<>")
op_X     = pp.Keyword("()")

# binary operators
op_and   = pp.Keyword("&")
op_or    = pp.Keyword("|")
op_impl  = pp.Keyword("=>")
op_iff   = pp.Keyword("<=>")

op_U     = pp.Keyword("U")
op_W     = pp.Keyword("W")

# misc
ropen_   = pp.Keyword("(")
rclose_  = pp.Keyword(")")
sopen_   = pp.Keyword("[")
sclose_  = pp.Keyword("]")

###############################################################################
# Grammar rules
###############################################################################

LTL      = pp.Forward() # This is the grammar axiom
LTL_     = pp.Forward() # handle left recursion

# Unit productions
literal  = (true | false | variable)

#
LTL   << ( (literal+ LTL_ )
         | (ropen_ + LTL + rclose_ + LTL_)
         | (sopen_ + LTL + sclose_ + LTL_)
         | (op_not + LTL + LTL_).setParseAction(lambda t: retpush(ast.Not(_stack.pop())))
         # temporal modalities         
         | (op_G   + LTL + LTL_).setParseAction(lambda t: retpush(ast.Globally(_stack.pop())))
         | (op_F   + LTL + LTL_).setParseAction(lambda t: retpush(ast.Eventually(_stack.pop())))
         | (op_X   + LTL + LTL_).setParseAction(lambda t: retpush(ast.Next(_stack.pop())))
         )

LTL_  << ( (op_and + LTL ).setParseAction(lambda t: retpush(ast.And(rhs=_stack.pop(), lhs=_stack.pop())))
         | (op_or  + LTL ).setParseAction(lambda t: retpush(ast.Or(rhs=_stack.pop(), lhs=_stack.pop())))
         | (op_impl+ LTL ).setParseAction(lambda t: retpush(ast.Imply(rhs=_stack.pop(), lhs=_stack.pop())))
         | (op_iff + LTL ).setParseAction(lambda t: retpush(ast.Equiv(rhs=_stack.pop(), lhs=_stack.pop())))
         | (op_U + LTL ).setParseAction(lambda t: retpush(ast.Until(rhs=_stack.pop(), lhs=_stack.pop())))
         | (op_W + LTL ).setParseAction(lambda t: retpush(ast.WeakUntil(rhs=_stack.pop(), lhs=_stack.pop())))
         # finite recursions
         | pp.Empty()
         )

def parseLTL(text):
    """
    Parses an LTL string and returns the corresponding AST
    
    :param text: the text to be parsed
    :return: an LTL ast corresponding to the parsed LTL expression
    """
    LTL.parseString(text)
    return _stack.pop()
