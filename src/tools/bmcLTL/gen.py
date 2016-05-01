from pynusmv.be.expression import Be

from tools.bmcLTL.parsing import parseLTL

def loop_condition(enc, k, l):
    """
    This function generates a Be expression representing the loop condition
    which is necessary to determine that k->l is a backloop.
    
    Formally, the returned constraint is denoted _{l}L_{k}
    
    Because the transition relation is encoded in Nusmv as formula (and not as
    a relation per-se), we determine the existence of a backloop between 
    l < k and forall var, var(i) == var(k)
     
    That is to say: if it is possible to encounter two times the same state
    (same state being all variables have the same value in both states) we know
    there is a backloop on the path
    
    :param fsm: the fsm on which the condition will be evaluated
    :param k: the highest time
    :param l: the time where the loop is assumed to start
    :return: a Be expression representing the loop condition that verifies that
        k-l is a loop path.
    """
    cond = Be.true(enc.manager)
    for v in enc.curr_variables: # for all untimed variable
        vl   = v.at_time[l].boolean_expression
        vk   = v.at_time[k].boolean_expression
        cond = cond & ( vl.iff(vk) )
    return cond

def model_problem(fsm, bound):
    """
    Computes the unrolled transition relation [[M]]_{k}
    """
    enc   = fsm.encoding
    # initial state
    init0 = enc.shift_to_time(fsm.init, 0)
    # transition relation (unrolled k steps)
    trans = Be.true(enc.manager)
    for k in range(bound+1):
        trans = trans & enc.shift_to_time(fsm.trans, k)
    
    return init0 & trans

def generate_problem(formula_text, fsm, k=10):
    """
    Generates a formula representing a SAT problem that is satisfiable iff
    the the `fsm` violates the formula represented in `formula_text`.
    
    Mathematically, this function computes the following formula:
    .. math:: [[M, f]]_{k}
    
    :param formula_text: an LTL formula written with the symbolic syntax
        (not that of NuSMV)
    :param fsm: the FSM representing the model.
    :return: a Be expression that is satisfiable iff the fsm can violate the 
        stated property [[M, f]]_{k}
    """
    enc = fsm.encoding
    fml = parseLTL(formula_text)
    
    # if there is no Loop on the path
    Lk  = loop_condition(enc, k, k)
    for l in  range(k): Lk = Lk | loop_condition(enc, k, l)
    exp = fml.semantic_no_loop(enc, 0, k)
    exp_no_loop = ((-Lk) & exp)
    
    # if there is a loop (try all possible start points)
    exp = Be.false(enc.manager) # see inductive step of Definition 8 in Biere et al.
    for l in range(k+1):
        exp = exp | (loop_condition(enc, k, l) & fml.semantic_with_loop(enc, 0, k, l))
    exp_with_loop = exp
    
    # unroll the transition relation
    mdl_pb = model_problem(fsm, k)
    
    # verify if formula is falsifiable on the given fsm
    prop = exp_no_loop | exp_with_loop
    return mdl_pb & -prop