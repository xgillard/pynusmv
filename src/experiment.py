"""
DISREGARD THE CONTENT OF THIS FILE, IT ONLY CONTAINS EXPERIMENTS AND INCOMPLETE
IDEAS THAT I TRIED/AM IN THE PROCESS OF TRYING. SOME/ALL OF IT MAY SIMPLY NOT
WORK.
"""
from pynusmv.init           import init_nusmv
from pynusmv.glob           import load_from_string, master_bool_sexp_fsm
from pynusmv.bmc.glob       import BmcSupport, master_be_fsm

from pynusmv.be.encoder     import BeEnc
from pynusmv.be.expression  import Be
from pynusmv.nusmv.enc.be   import be    as _beenc 
from pynusmv.nusmv.enc.base import base  as _baseenc 

from pynusmv.nusmv.compile.symb_table import symb_table as _stable

from pynusmv.nusmv.fsm.sexp import sexp as _sexpfsm
from pynusmv.collections import NodeList

from enum import IntEnum


def mk_new_encoder(sexp_fsm):
    """
    Creates a fresh new boolean encoder containing all the variables (declared
    in all the layers) of the symbol table associated with the given `sexp_fsm`
    
    One such fresh encoder *THE* object you need when you need to model one 
    execution path in the scope of a BMC verification.
    
    :param sexp_fsm: the scalar expression for which a new encoding is required
    :return: a fresh fsm containing all the variables etc.. declared in the sexp
        model.
    """
    # create a fresh instance
    bool_enc     = _sexpfsm.BoolSexpFsm_get_bool_enc(sexp_fsm._ptr)
    encoder_ptr  = _beenc.BeEnc_create(sexp_fsm.symbol_table._ptr, bool_enc)
    
    # copy all existing layers
    base_ptr     = _beenc.BeEnc_ptr_to_BaseEnc_ptr(encoder_ptr)
    for layer_name in sexp_fsm.symbol_table.layer_names:
        # do it iff it is not committed yet
        if not bool(_baseenc.BaseEnc_layer_occurs(base_ptr, layer_name)):
            _baseenc.BaseEnc_commit_layer(base_ptr, layer_name)
    # your instance is ready
    return BeEnc(encoder_ptr, freeit=True)

class SymbolTableType(IntEnum):
    """
    An enum representing (at a coarse level) the kind of symbols that may 
    appear in a NuSmv symbol table.
    """
    NONE           = _stable.STT_NONE,
    ALL            =  _stable.STT_ALL,
    CONSTANT       = _stable.STT_CONSTANT,
    VARIABLE       = _stable.STT_VAR,
    STATE_VAR      = _stable.STT_STATE_VAR,
    INPUT_VAR      = _stable.STT_INPUT_VAR,
    FROZEN_VAR     = _stable.STT_FROZEN_VAR,
    DEFINE         = _stable.STT_DEFINE,
    ARRAY_DEFINE   = _stable.STT_ARRAY_DEFINE,
    PARAMETER      = _stable.STT_PARAMETER,
    FUNCTION       = _stable.STT_FUNCTION,
    VARIABLE_ARRAY = _stable.STT_VARIABLE_ARRAY

def layer_content(symbol_table, layer_name, mask=SymbolTableType.ALL):
    """
    Lists the content of `layer_name` in `symbol_table` according to the given
    symbol table type mask.
    
    :param symbol_table: the symbol table whose layers are being inspected
    :param layer_name: the name of the layer whose content is wished.
    :param mask: a bit mask indicating what values to return based on their
        abstract symbol type
    :return: a NodeList containing the various symbols contained in the layer
        satisfying the given mask.
    """
    _layer= symbol_table._get_layer(layer_name) 
    _iter = _stable.gen_iter(_layer, mask)
    _lst  = NodeList(_stable.SymbLayer_iter_to_list(_layer, _iter),freeit=False)
    return _lst    

with init_nusmv():
    load_from_string("""
        MODULE main
        VAR
            x : boolean;
            y : boolean;
        ASSIGN
            init(x) := FALSE;
            next(x) := !x;
    """)
    with BmcSupport():

        sexp_fsm = master_bool_sexp_fsm()
        symb_tbl = sexp_fsm.symbol_table
        
        # make two parallel FSMs.
        fsm1 = master_be_fsm()
        enc1 = fsm1.encoding
        
        formula = enc1.by_name['x'].boolean_expression & \
                  enc1.by_name['y'].boolean_expression
        
        subst   = [ v.at_time[1].index for v in enc1.untimed_variables] 
        print(subst)
        xformed = Be(_beenc.substitute_in_formula(enc1._ptr, formula._ptr, subst), enc1.manager)
        
        print(formula.to_cnf())
        print(xformed.to_cnf())