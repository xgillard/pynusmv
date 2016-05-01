"""
This module contains the class definition of the different classes that may 
compose an LTL abstract syntax tree. 
"""

from pynusmv.be.expression import Be

###############################################################################
# Useful to generate a problem: 
###############################################################################
def successor(i, k, l):
    """
    Computes the successor of time `i` in a k-l loop.
    
    .. note::
        References, see Definition 6 
        in Biere et al - ``Bounded Model Checking'' - 2003 
        
    :param i: the current time
    :param k: the maximum (horizon/bound) time of the problem
    :param l: the time where the loop starts 
    
    :return: the k-l loop successor of i
    """
    return i+1 if i < k else l

###############################################################################
# Abstract ast nodes
###############################################################################
class Formula:
    """An abstract base class meant to be the parent of all the AST nodes"""
    
    def semantic_no_loop(self, enc, i, k):
        """
        All nodes of the AST must implement this function. 
        Concretely, the role of this function is to generate a propositional
        equivalent to the bounded LTL semantic of this node when there is no
        loop on the path from state(time) to state(bound)
        
        ..math::
            [[self]]_{k}^{i}
        
        :param enc: the encoding used to store and organize the variables (used 
            ie to shift vars)
        :param i: the time at which the generated expression will be considered
        :param k: the last time that exists in the universe of this expression  
        :return: a boolean expression conform to the ltl bounded semantics of
            this node when there is no loop on the path from i to k
        """
        pass

    def semantic_with_loop(self, enc, i, k, l):
        """
        All nodes of the AST must implement this function. 
        Concretely, the role of this function is to generate a propositional
        equivalent to the bounded LTL semantic of this node when there is no
        loop on the path from state(time) to state(bound)
        
        ..math::
            _{l}[[self]]_{k}^{i}
        
        .. note::
            There are essentially two cases for the loop:
            
                1. i < l         (not yet entered in the loop)
                2. l <= i < k    (inside the loop)
                
            Therefore, l is allowed to range from 0 to k. However, you don't 
            need to deal with all the positions for yourself: the propblem
            generation method is responsible to call you with all the possible
            values of `l`. You may however compare l and k to test if you have
            reached the horizon of your bounded problem generation.  
        
        :param enc: the encoding used to store and organize the variables (used 
            ie to shift vars)
        :param i: the time at which the generated expression will be considered
        :param k: the last time that exists in the universe of this expression
        :param l: l is the time position where the loop starts.
        :return: a boolean expression conform to the ltl bounded semantics of
            this node when there is no loop on the path from i to k
        """
        pass

class Atomic(Formula):
    """An abstract base class representing AST of an atomic proposition""" 
    def __init__(self, x):
        self.id = x
        
    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.id)

class Unary(Formula):
    """An abstract base class representing AST of an unary proposition"""
    def __init__(self, prop):
        self.prop = prop
        
    def __repr__(self):
        return "({} {})".format(type(self).__name__, self.prop)

class Binary(Formula):
    """An abstract base class representing AST of a binary proposition"""
    def __init__(self, lhs=None, rhs=None):
        self.lhs = lhs
        self.rhs = rhs
    
    def __repr__(self):
        return "({} {} {})".format(self.lhs, type(self).__name__, self.rhs)

###############################################################################
# Propositional logic ast nodes
###############################################################################
class Constant(Atomic):
    def semantic_no_loop(self, enc, i, k):
        if self.id == "TRUE":
            return Be.true(enc.manager)
        else:
            return Be.false(enc.manager)
    
    def semantic_with_loop(self, fsm, i, k, l):
        return self.semantic_no_loop(fsm, i, k)
    
class Variable(Atomic):
    def semantic_no_loop(self, enc, i, k):
        return enc.by_name[self.id].at_time[i].boolean_expression
    
    def semantic_with_loop(self, fsm, i, k, l):
        return self.semantic_no_loop(fsm, i, k)

class Not(Unary):
    def semantic_no_loop(self, enc, i, k):
        return - self.prop.semantic_no_loop(enc, i, k)
    
    def semantic_with_loop(self, enc, i, k, l):
        return -self.prop.semantic_with_loop(enc, i, k, l)

class And(Binary):
    def semantic_no_loop(self, enc, i, k):
        lhs = self.lhs.semantic_no_loop(enc, i, k)
        rhs = self.rhs.semantic_no_loop(enc, i, k)
        return lhs & rhs
    
    def semantic_with_loop(self, enc, i, k, l):
        lhs = self.lhs.semantic_with_loop(enc, i, k, l)
        rhs = self.rhs.semantic_with_loop(enc, i, k, l)
        return lhs & rhs

class Or(Binary):
    def semantic_no_loop(self, enc, i, k):
        lhs = self.lhs.semantic_no_loop(enc, i, k)
        rhs = self.rhs.semantic_no_loop(enc, i, k)
        return lhs | rhs
    
    def semantic_with_loop(self, enc, i, k, l):
        lhs = self.lhs.semantic_with_loop(enc, i, k, l)
        rhs = self.rhs.semantic_with_loop(enc, i, k, l)
        return lhs | rhs
        
class Imply(Binary):
    def semantic_no_loop(self, enc, i, k):
        lhs = self.lhs.semantic_no_loop(enc, i, k)
        rhs = self.rhs.semantic_no_loop(enc, i, k)
        return lhs.imply(rhs)
    
    def semantic_with_loop(self, enc, i, k, l):
        lhs = self.lhs.semantic_with_loop(enc, i, k, l)
        rhs = self.rhs.semantic_with_loop(enc, i, k, l)
        return lhs.imply(rhs)

class Equiv(Binary):
    def semantic_no_loop(self, enc, i, k):
        lhs = self.lhs.semantic_no_loop(enc, i, k)
        rhs = self.rhs.semantic_no_loop(enc, i, k)
        return lhs.iff(rhs)
    
    def semantic_with_loop(self, enc, i, k, l):
        lhs = self.lhs.semantic_with_loop(enc, i, k, l)
        rhs = self.rhs.semantic_with_loop(enc, i, k, l)
        return lhs.iff(rhs)

###############################################################################
# LTL specific ast nodes
###############################################################################

class Until(Binary):
    def semantic_no_loop(self, enc, i, k):
        """The semantics when there is no loop:: [[lhs U rhs]]_{bound}^{time}"""
        # at infinity, it is false: psi MUST happen at some time
        cond = Be.false(enc.manager)
        for time in reversed(range(i, k+1)):
            psi = self.rhs.semantic_no_loop(enc, time, k)
            phi = self.lhs.semantic_no_loop(enc, time, k)
            cond = psi | (phi & cond)
        return cond

    
    def semantic_with_loop(self, enc, i, k, l):
        """The semantics when there is a loop:: _{l}[[lhs U rhs]]_{bound}^{time}"""
        # two cases : 
        # - either we did not enter the loop yet and (i < l) and therefore
        #   we enumerate i->l and then l->k
        # - or we already entered the loop and then (l <= i <= k) and therefore
        #   it suffices to enumerate from l to k
        #
        # Note, for the sake of making a finite iterative process, we proceed
        # backwards and enumerate from k to start
        start = min(i, l)
        # at infinity, it is false: psi MUST happen at some time
        cond = Be.false(enc.manager)
        for time in reversed(range(start, k+1)):
            psi = self.rhs.semantic_with_loop(enc, time, k, l)
            phi = self.lhs.semantic_with_loop(enc, time, k, l)
            cond = psi | (phi & cond)
        return cond

class WeakUntil(Binary):
    def semantic_no_loop(self, enc, i, k):
        """The semantics when there is no loop:: [[lhs W rhs]]_{bound}^{time}"""
        # at infinity, it is true: psi may never happen but k IS NOT INFINITY
        cond = Be.false(enc.manager)
        for time in reversed(range(i, k+1)):
            psi = self.rhs.semantic_no_loop(enc, time, k)
            phi = self.lhs.semantic_no_loop(enc, time, k)
            cond = psi | (phi & cond)
        return cond
    
    def semantic_with_loop(self, enc, i, k, l):
        """The semantics when there is a loop:: _{l}[[lhs W rhs]]_{bound}^{time}"""
        # two cases : 
        # - either we did not enter the loop yet and (i < l) and therefore
        #   we enumerate i->l and then l->k
        # - or we already entered the loop and then (l <= i <= k) and therefore
        #   it suffices to enumerate from l to k
        #
        # Note, for the sake of making a finite iterative process, we proceed
        # backwards and enumerate from k to start
        start = min(i, l)
        # at infinity, it is true: psi may never happen (in a loop there is 
        # potentially infinite behavior)
        cond = Be.true(enc.manager)
        for time in reversed(range(start, k+1)):
            psi = self.rhs.semantic_with_loop(enc, time, k, l)
            phi = self.lhs.semantic_with_loop(enc, time, k, l)
            cond = psi | (phi & cond)
        return cond

class Globally(Unary):
    def semantic_no_loop(self, enc, i, k):
        return Be.false(enc.manager)
    
    def semantic_with_loop(self, enc, i, k, l):
        start = min(i, l)
        cond  = Be.true(enc.manager) # neutral for the conjunction operator 
        for time in reversed(range(start, k+1)):
            cond = cond & self.prop.semantic_with_loop(enc, time, k, l)
        return cond

class Eventually(Unary):
    def semantic_no_loop(self, enc, i, k):
        cond  = Be.false(enc.manager) 
        for time in reversed(range(i, k+1)):
            cond = cond | self.prop.semantic_no_loop(enc, time, k)
        return cond

    def semantic_with_loop(self, enc, i, k, l):
        start = min(i, l)
        cond  = Be.false(enc.manager) 
        for time in reversed(range(start, k+1)):
            cond = cond | self.prop.semantic_with_loop(enc, time, k, l)
        return cond

class Next(Unary):
    def semantic_no_loop(self, enc, i, k):
        if i == k+1:
            return Be.false(enc.manager)
        else: 
            return self.prop.semantic_no_loop(enc, i+1, k)

    def semantic_with_loop(self, enc, i, k, l):
        if i == k+1:
            return Be.false(enc.manager)
        else: 
            return self.prop.semantic_with_loop(enc, successor(i, k, l), k, l)
        
        