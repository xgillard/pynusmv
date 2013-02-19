"""
The :mod:`pynusmv.prop` module contains classes and functions dealing with
properties and specifications of models.

"""


__all__ = ['propTypes', 'Prop', 'PropDb','Spec', 'true', 'false', 'nott',
           'andd', 'orr', 'imply', 'iff', 'ex', 'eg', 'ef', 'eu', 'ew',
           'ax', 'ag', 'af', 'au', 'aw', 'atom']


from .nusmv.prop import prop as nsprop
from .nusmv.parser import parser as nsparser
from .nusmv.node import node as nsnode
from .nusmv.compile.type_checking import type_checking as nstype_checking
from .nusmv.compile.symb_table import symb_table as nssymb_table

from .fsm import BddFsm
from .utils import PointerWrapper     
from . import parser
from .exception import NuSMVParserError, NuSMVTypeCheckingError


propTypes = {
             'NoType' :      nsprop.Prop_NoType,
             'CTL' :         nsprop.Prop_Ctl,
             'LTL' :         nsprop.Prop_Ltl,
             'PSL' :         nsprop.Prop_Psl,
             'Invariant' :   nsprop.Prop_Invar,
             'Compute' :     nsprop.Prop_Compute,
             'Comparison' :  nsprop.Prop_CompId
            }
"""
The possible types of properties. This gives access to NuSMV internal types
without dealing with `pynusmv.nusmv` modules.

"""


class Prop(PointerWrapper):
    """
    Python class for properties.
    
    Properties are NuSMV data structures containing specifications but also
    pointers to models (FSM) and other things.
    
    """
    # Prop do not have to be freed since they come from PropDb.
        
    @property
    def type(self):
        """
        The type of this property. It is one element of :data:`propTypes`.
        
        """
        return nsprop.Prop_get_type(self._ptr)
        
    @property
    def name(self):
        """
        The name of this property, as a string.
        
        """
        return nsprop.Prop_get_name_as_string(self._ptr)
        
    @property
    def expr(self):
        """
        The expression of this property.
        
        :rtype: :class:`Spec`
        
        """
        return Spec(nsprop.Prop_get_expr(self._ptr))
        
    @property
    def exprcore(self):
        """
        The core expression of this property
        
        :rtype: :class:`Spec`
        
        """
        return Spec(nsprop.Prop_get_expr_core(self._ptr))
        
    @property
    def bddFsm(self):
        """
        The BDD-encoded FSM of this property.
        
        :rtype: :class:`BddFsm <pynusmv.fsm.BddFsm>`
        
        """
        return BddFsm(nsprop.Prop_get_bdd_fsm(self._ptr))


class PropDb(PointerWrapper):
    """
    Python class for property database.
    
    A property database is just a list of properties (:class:`Prop`).
    Any PropDb can be used as a Python list.
    """
    # PropDb do not have to be freed.
    
    
    @property
    def master(self):
        """
        The master property of this database.
        
        :rtype: :class:`Prop`
        
        """
        return Prop(nsprop.PropDb_get_master(self._ptr))
    
    
    def get_prop_at_index(self, index):
        """
        Return the property stored at `index`.
        
        :rtype: :class:`Prop`
        
        """
        return Prop(nsprop.PropDb_get_prop_at_index(self._ptr, index))
    
    
    def get_size(self):
        """
        Return the number of properties stored in this database.
        
        """
        return nsprop.PropDb_get_size(self._ptr)
        
    
    def __len__(self):
        """
        Return the length of this database.
        
        """
        return self.get_size()
        
    
    def __getitem__(self, index):
        """
        Return the `index`th property.
        
        :raise: a :exc:`IndexError` if `index` is not in the bounds
        
        """
        if index < -len(self) or index >= len(self):
            raise IndexError("PropDb index out of range")
        if index < 0:
            index = index + len(self)
        return self.get_prop_at_index(index)
        
    
    def __iter__(self):
        """
        Return an iterator on this database.
        
        """
        for i in range(len(self)):
            yield self[i]
            

class Spec(PointerWrapper):
    """
    A CTL specification.
    
    The Spec class implements a NuSMV nodes-based specification.
    No check is made to insure that the node is effectively a specification,
    i.e. the stored pointer is not checked against spec types.
    
    """
    # Specs do not have to be freed.
    
    def __init__(self, ptr, freeit = False):
        """
        Create a new Spec.
        
        :param ptr: the pointer of the specification as a NuSMV node
        :param boolean freeit: whether or not the pointer has to be freed
        
        """
        super().__init__(ptr, freeit = freeit)
        
        
    @property
    def type(self):
        """
        The type of this specification.
        
        """
        return self._ptr.type
    
    @property
    def car(self):
        """
        The left child of this specification.
        
        :rtype: :class:`Spec`
        
        """
        left = nsnode.car(self._ptr)
        if left:
            return Spec(left, freeit = self._freeit)
        else:
            return None
        
    @property
    def cdr(self):
        """
        The right child of this specification.
        
        :rtype: :class:`Spec`
        
        """
        right = nsnode.cdr(self._ptr)
        if right:
            return Spec(right, freeit = self._freeit)
        else:
            return None
            
    def __str__(self):
        """
        Return a string representation of this specification.
        
        """
        return nsnode.sprint_node(self._ptr)

    def __or__(self, other):
        """
        Return the specification `self OR other`.
        
        :rtype: :class:`Spec`
        
        """
        if other is None:
            raise ValueError()
        return Spec(nsnode.find_node(nsparser.OR, self._ptr, other._ptr))
        
    def __and__(self, other):
        """
        Return the specification `self AND other`.
        
        :rtype: :class:`Spec`
        
        """
        if other is None:
            raise ValueError()
        return Spec(nsnode.find_node(nsparser.AND, self._ptr, other._ptr))
        
    def __invert__(self):
        """
        Return the specification `NOT self`.
        
        :rtype: :class:`Spec`
        
        """
        return Spec(nsnode.find_node(nsparser.NOT, self._ptr, None))
        

def true():
    """
    Return a new specification corresponding to `TRUE`.
    
    :rtype: :class:`Spec`
    
    """
    return Spec(nsnode.find_node(nsparser.TRUEEXP, None, None))
    

def false():
    """
    Return a new specification corresponding to `FALSE`.
    
    :rtype: :class:`Spec`
    
    """
    return Spec(nsnode.find_node(nsparser.FALSEEXP, None, None))
    
    
def nott(spec):
    """Return a new specification corresponding to `NOT spec`.
    
    :rtype: :class:`Spec`
    
    """
    if spec is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.NOT, spec._ptr, None))
    

def andd(left, right):
    """
    Return a new specification corresponding to `left AND right`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.AND, left._ptr, right._ptr))
    

def orr(left, right):
    """
    Return a new specification corresponding to `left OR right`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.OR, left._ptr, right._ptr))
       

def imply(left, right):
    """
    Return a new specification corresponding to `left IMPLIES right`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.IMPLIES, left._ptr, right._ptr))
    

def iff(left, right):
    """
    Return a new specification corresponding to `left IFF right`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.IFF, left._ptr, right._ptr))
    
    
def ex(spec):
    """
    Return a new specification corresponding to `EX spec`.
    
    :rtype: :class:`Spec`
    
    """
    if spec is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.EX, spec._ptr, None))
    

def eg(spec):
    """
    Return a new specification corresponding to `EG spec`.
    
    :rtype: :class:`Spec`
    
    """
    if spec is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.EG, spec._ptr, None))
    
    
def ef(spec):
    """
    Return a new specification corresponding to `EF spec`.
    
    :rtype: :class:`Spec`
    
    """
    if spec is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.EF, spec._ptr, None))
    
    
def eu(left, right):
    """
    Return a new specification corresponding to `E[left U right]`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.EU, left._ptr, right._ptr))
    
    
def ew(left, right):
    """
    Return a new specification corresponding to `E[left W right]`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.EW, left._ptr, right._ptr))
    
    
def ax(spec):
    """
    Return a new specification corresponding to `AX spec`.
    
    :rtype: :class:`Spec`
    
    """
    if spec is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.AX, spec._ptr, None))
    

def ag(spec):
    """
    Return a new specification corresponding to `AG spec`.
    
    :rtype: :class:`Spec`
    
    """
    if spec is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.AG, spec._ptr, None))
    
    
def af(spec):
    """
    Return a new specification corresponding to `AF spec`.
    
    :rtype: :class:`Spec`
    
    """
    if spec is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.AF, spec._ptr, None))
    
    
def au(left, right):
    """
    Return a new specification corresponding to `A[left U right]`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.AU, left._ptr, right._ptr))
    
    
def aw(left, right):
    """
    Return a new specification corresponding to `A[left W right]`.
    
    :rtype: :class:`Spec`
    
    """
    if left is None or right is None:
        raise ValueError()
    return Spec(nsnode.find_node(nsparser.AW, left._ptr, right._ptr))


def atom(strrep):
    """
    Return a new specification corresponding to the given atom.
    `strrep` is parsed type checked on the current model. A model needs to be
    read and with variables encoded to be able to type check the atomic
    proposition.
    
    :rtype: :class:`Spec`
    
    """
    
    from . import glob
    
    # Parsing
    node = parser.parse_simple_expression(strrep)
    
    # Type checking
    # TODO Prevent printing a message on stderr
    symb_table = glob.bdd_encoding().symbTable
    # TODO Type check only if symb_table is not None? With a Warning?
    type_checker = nssymb_table.SymbTable_get_type_checker(symb_table._ptr)
    expr_type = nstype_checking.TypeChecker_get_expression_type(
                                                       type_checker, node, None)
    if not nssymb_table.SymbType_is_boolean(expr_type):
        raise NuSMVTypeCheckingError(strrep + " is wrongly typed.")   
    
    return Spec(node)