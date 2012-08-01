from pyparsing import Suppress, SkipTo, Forward, ZeroOrMore, Literal

from .ast import (Atom, Not, And, Or, Implies, Iff, 
                  AaF, AaG, AaX, AaU, AaW,
                  EaF, EaG, EaX, EaU, EaW)
                  
                  
def _left_(clss, tokens):
    """
    Parse tokens and return an AST, assuming left associativity.
    
    Given a list of tokens [v1, op, v2, op, ..., op, vn],
    return res, a hierarchy of instances of clss such that
    res = clss(clss(...clss(v1, v2), ..., vn).
    
    This is a helper function to parse logical operators.
    """
    if len(tokens) == 1:
        return tokens[0]
    else:
        return clss(_left_(clss, tokens[:-2]), tokens[-1])


def _right_(clss, tokens):
    """
    Parse tokens and return an AST, assuming right associativity.
    
    Given a list of tokens [v1, op, v2, op, ..., op, vn],
    return res, a hierarchy of instances of clss such that
    res = clss(v1, clss(v2, ..., vn)...).
    
    This is a helper function to parse logical operators.
    """
    if len(tokens) == 1:
        return tokens[0]
    else:
        return clss(tokens[0], _right_(clss, tokens[2:]))
        
        
def _logicals_(atomic):
    """
    Return a new parser parsing logical expressions on atomics.
    
    This parser recognizes the following grammar, with precedences
    parser := atomic | '~' parser | parser '&' parser | parser '|' parser |
              parser '->' parser | parser '<->' parser
              
    Returned AST uses .ast package's classes.
    """
    parser = Forward()

    atom = (atomic | Suppress("(") + parser + Suppress(")"))

    notstrict = "~" + atom
    notstrict.setParseAction(lambda tokens: Not(tokens[1]))
    not_ = notstrict | atom
    and_ = not_ + ZeroOrMore("&" + not_)
    and_.setParseAction(lambda tokens: _left_(And, tokens))
    or_ = and_ + ZeroOrMore("|" + and_)
    or_.setParseAction(lambda tokens: _left_(Or, tokens))
    implies = ZeroOrMore(or_ + "->") + or_
    implies.setParseAction(lambda tokens: _right_(Implies, tokens))
    iff = implies + ZeroOrMore("<->" + implies)
    iff.setParseAction(lambda tokens: _left_(Iff, tokens))

    parser << iff
    
    return parser
        

"""
ARCTL parsing tool.

_arctl       := _atom | _logical | _temporal
_logical     := '~' _arctl | '(' _logical ')' | _arctl '&' _arctl |
                _arctl '|' _arctl | _arctl '->' _arctl | _arctl '<->' _arctl
_temporal    := 'A' '<' _action '>' 'F' _arctl |
                'A' '<' _action '>' 'G' _arctl |
                'A' '<' _action '>' 'X' _arctl |
                'A' '<' _action '>' '[' _arctl 'U' _arctl ']' |
                'A' '<' _action '>' '[' _arctl 'W' _arctl ']' |
                'E' '<' _action '>' 'F' _arctl |
                'E' '<' _action '>' 'G' _arctl |
                'E' '<' _action '>' 'X' _arctl |
                'E' '<' _action '>' '[' _arctl 'U' _arctl ']' |
                'E' '<' _action '>' '[' _arctl 'W' _arctl ']'
_action      := _atom | '(' _action ')' | '~' _action | _action '&' _action |
                _action '|' _action | _action '->' _action |
                _action '<->' _action
               
_atom is defined by any string surrounded by single quotes.

_action and _logical are specified with usual precedences and associativity,
i.e.
prec : ~, &, |, ->, <->
assoc : &, |, <-> left assoc, ->, ~ right assoc


The parser returns a structure embedding the structure of the parsed
expression, represented using AST classes of .ast module.
"""

_arctl = None

def parseArctl(spec):
    """Parse the spec and return its AST."""
    global _arctl
    if _arctl is None:
        atom = "'" + SkipTo("'") + "'"
        atom.setParseAction(lambda tokens: Atom(tokens[1]))
        
        action = _logicals_(atom)
        
        _arctl = Forward()


        formula = (atom | Suppress("(") + _arctl + Suppress(")"))


        temporal = Forward()

        e = Literal("E") + "<" + action + ">"
        a = Literal("A") + "<" + action + ">"

        eax = e + "X" + temporal
        eax.setParseAction(lambda tokens: EaX(tokens[2], tokens[5]))
        aax = a + "X" + temporal
        aax.setParseAction(lambda tokens: AaX(tokens[2], tokens[5]))
        
        eaf = e + "F" + temporal
        eaf.setParseAction(lambda tokens: EaF(tokens[2], tokens[5]))
        aaf = a + "F" + temporal
        aaf.setParseAction(lambda tokens: AaF(tokens[2], tokens[5]))
        
        eag = e + "G" + temporal
        eag.setParseAction(lambda tokens: EaG(tokens[2], tokens[5]))
        aag = a + "G" + temporal
        aag.setParseAction(lambda tokens: AaG(tokens[2], tokens[5]))
        
        eau = e + "[" + _arctl + "U" + _arctl + "]"
        eau.setParseAction(lambda tokens: EaU(tokens[2], tokens[5], tokens[7]))
        aau = a + "[" + _arctl + "U" + _arctl + "]"
        aau.setParseAction(lambda tokens: AaU(tokens[2], tokens[5], tokens[7]))
        
        eaw = e + "[" + _arctl + "W" + _arctl + "]"
        eaw.setParseAction(lambda tokens: EaW(tokens[2], tokens[5], tokens[7]))
        aaw = a + "[" + _arctl + "W" + _arctl + "]"
        aaw.setParseAction(lambda tokens: AaW(tokens[2], tokens[5], tokens[7]))


        temporal << (formula | eax | aax | eaf | aaf | eag | aag |
                     eau | aau | eaw | aaw)
      
        logical = _logicals_(temporal)

        _arctl << logical
    
    return _arctl.parseString(spec, parseAll = True)