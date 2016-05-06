from pynusmv.be.expression import Be

def model_problem(fsm, bound):
    """
    Computes the unrolled transition relation [[M]]_{k}
    """
    enc   = fsm.encoding
    # initial state
    init0 = enc.shift_to_time(fsm.init, 0)
    # transition relation (unrolled k steps)
    trans = Be.true(enc.manager)
    for k in range(bound):
        trans = trans & enc.shift_to_time(fsm.trans, k)
    
    return init0 & trans

def generate_problem(fml, fsm, k=10):
    """
    Generates a formula representing a SAT problem that is satisfiable iff
    the the `fsm` violates the formula represented in `formula_text`.
    
    Mathematically, this function computes the following formula:
    .. math:: [[M, f]]_{k}
    
    :param fml: an LTL formula parsed with `tools.bmcLTL.parsing` (hence the 
        abstract syntax tree of that formula). Note, this is *NOT* the NuSMV
        format (Node).
    :param fsm: the FSM representing the model.
    :return: a Be expression that is satisfiable iff the fsm can violate the 
        stated property [[M, f]]_{k}
    """
    enc     = fsm.encoding
    negated = fml.nnf(True)
    return model_problem(fsm, k) & negated.bounded_semantics(enc, k)