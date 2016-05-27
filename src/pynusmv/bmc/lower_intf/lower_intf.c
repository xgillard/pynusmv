#include "lower_intf.h"

#include <stdlib.h>

#include <parser/symbols.h>
#include <node/node.h>
#include <be/be.h>
#include <fsm/be/BeFsm.h>

#include <enc/enc.h>
#include <compile/compile.h>

#include <bmc/bmcConv.h>


/****** REAL STUFF COMPUTATION ********************************************************************
 * BEWARE, these functions are not memoized (but these are the ones that actually DO PERFORM
 * the heavy lifting). If your need to give a look at the memoized versions of these functions,
 * they are declared at the very end of this file.
 **************************************************************************************************/

be_ptr proposition_at_time(BeEnc_ptr enc, node_ptr formula, int time){
  BddEnc_ptr bddenc = Enc_get_bdd_encoding();
  Expr_ptr   bexpr  = Compile_detexpr2bexpr(bddenc, formula);
  be_ptr     expr   = Bmc_Conv_Bexp2Be(enc, (node_ptr) bexpr);

  return BeEnc_untimed_expr_to_timed(enc, expr, time);
}

int succ(int k, int l, int time){
  return time < k -1 ? time + 1 : l;
}

be_ptr fairness_constraint(BeFsm_ptr fsm, int k, int l){
  BeEnc_ptr      enc     = BeFsm_get_be_encoding(fsm);
  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);

  if (Bmc_Utils_IsNoLoopback(l)){
    return Be_Falsity(manager);
  }

  be_ptr constraint = Be_Truth(manager);
  if (k == 0){
    return constraint;
  }

  node_ptr iter = BeFsm_get_fairness_list(fsm);
  while(iter != NULL){
    be_ptr fairness = (be_ptr) car(iter);
    be_ptr expr     = BeEnc_untimed_to_timed_or_interval(enc, fairness, l, k-1);
    constraint      = Be_And(manager, constraint, expr);
    /* next */
    iter = cdr(iter);
  }

  return constraint;
}

be_ptr loop_condition(BeEnc_ptr enc, int k, int l){
  int iter = BeEnc_get_first_untimed_var_index(enc, BE_VAR_TYPE_CURR);

  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);
  be_ptr cond = Be_Truth(manager);

  while (BeEnc_is_var_index_valid(enc, iter)) {
    be_ptr vl = BeEnc_index_to_timed(enc, iter, l);
    be_ptr vk = BeEnc_index_to_timed(enc, iter, k);
    cond = Be_And(manager, cond, Be_Iff(manager, vl, vk));
    iter = BeEnc_get_next_var_index(enc, iter, BE_VAR_TYPE_CURR);
  }

  return cond;
}

be_ptr NO_MEMOIZE_sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset){
  BeEnc_ptr      enc     = BeFsm_get_be_encoding(fsm);
  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);

  if(time > bound){
    return Be_Falsity(manager);
  }
  switch(node_get_type(formula)){
  case AND:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_And(manager, left, right);
    }
  case OR:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Or(manager, left, right);
    }
  case XOR:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Xor(manager, left, right);
    }
  case NOT:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    return Be_Not(manager, left);
    }
  case IMPLIES:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Implies(manager, left, right);
    }
  case IFF:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Iff(manager, left, right);
    }
  case OP_NEXT:
    return sem_no_loop_offset(fsm, car(formula), time+1, bound, offset);
  case OP_GLOBAL:
    return Be_Falsity(manager);
  case OP_FUTURE:
    {
    be_ptr now = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr then= sem_no_loop_offset(fsm, formula, time+1, bound, offset);
    return Be_Or(manager, now, then);
    }
  case UNTIL:
    {
    be_ptr psi = sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    be_ptr phi = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr then= sem_no_loop_offset(fsm, formula, time+1, bound, offset);
    return Be_Or(manager, psi, Be_And(manager, phi, then));
    }
  case RELEASES:
    {
    be_ptr psi = sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    be_ptr phi = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr then= sem_no_loop_offset(fsm, formula, time+1, bound, offset);
    return Be_And(manager, psi, Be_Or(manager, phi, then));
    }
  default:
    {
    return proposition_at_time(enc, formula, time + offset);
    }
  }
  /* never reached */
  return NULL;
}

be_ptr NO_MEMOIZE_sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset){
  BeEnc_ptr      enc     = BeFsm_get_be_encoding(fsm);
  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);

  if(bound == 0){
    return Be_Falsity(manager);
  }
  if(time > bound){
    return Be_Falsity(manager);
  }
  switch(node_get_type(formula)){
  case AND:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_And(manager, left, right);
    }
  case OR:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Or(manager, left, right);
    }
  case XOR:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Xor(manager, left, right);
    }
  case NOT:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    return Be_Not(manager, left);
    }
  case IMPLIES:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Implies(manager, left, right);
    }
  case IFF:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Iff(manager, left, right);
    }
  case OP_NEXT:
    return sem_with_loop_offset(fsm, car(formula), succ(bound, loop, time), bound, loop, offset);
  case OP_GLOBAL:
    {
      int i;
      be_ptr result = Be_Truth(manager);
      for(i = min(time, loop); i<bound; i++){
        result = Be_And(manager, result, sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset));
      }
      return result;
    }
  case OP_FUTURE:
    {
      int i;
      be_ptr result = Be_Falsity(manager);
      for(i = min(time, loop); i<bound; i++){
        result = Be_Or(manager, result, sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset));
      }
      return result;
    }
  case UNTIL:
    {
      int i;
      be_ptr result = Be_Falsity(manager);
      /* Go reverse ! */
      for(i = bound-1; i>=min(time, loop); i--){
          be_ptr psi    = sem_with_loop_offset(fsm, cdr(formula), i, bound, loop, offset);
          be_ptr phi    = sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset);
          result        = Be_Or(manager, psi, Be_And(manager, phi, result));
      }
      return result;
    }
  case RELEASES:
    {
      int i;
      be_ptr result = Be_Falsity(manager);
      /* Go reverse ! */
      for(i = bound-1; i>=min(time, loop); i--){
          be_ptr psi    = sem_with_loop_offset(fsm, cdr(formula), i, bound, loop, offset);
          be_ptr phi    = sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset);
          result        = Be_And(manager, psi, Be_Or(manager, phi, result));
      }
      return result;
    }
  default:
    {
    return proposition_at_time(enc, formula, time + offset);
    }
  }
  /* never reached */
  return NULL;
}

/****** MEMOIZATION *******************************************************************************
 * These functions do not do anything on their own, they only serve the purpose of caching the
 * results of some of the functions declared above.
 **************************************************************************************************/

/* NOTE: we might want to memoize the loop_condition */

be_ptr sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset){
  node_ptr key    = MEMOIZER_key(formula, time+offset, bound, Bmc_Utils_GetNoLoopback());
  be_ptr   result = MEMOIZER_get(key);

  if (result == (be_ptr) NULL){
    result = NO_MEMOIZE_sem_no_loop_offset(fsm, formula, time, bound, offset);
    MEMOIZER_put(key, result);
  }

  return result;
}

be_ptr sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset){
  node_ptr key    = MEMOIZER_key(formula, time+offset, bound, loop);
  be_ptr   result = MEMOIZER_get(key);

  if (result == (be_ptr) NULL){
    result = NO_MEMOIZE_sem_with_loop_offset(fsm, formula, time, bound, loop, offset);
    MEMOIZER_put(key, result);
  }

  return result;
}

/****** MEMOIZATION *******************************************************************************
 * Private memoization functions
 **************************************************************************************************/
static hash_ptr MEMOIZER = (hash_ptr) NULL;

node_ptr MEMOIZER_key(node_ptr wff, int time, int k, int l) {
  return find_node(CONS, wff,
                   find_node(CONS, PTR_FROM_INT(node_ptr, time),
                             find_node(CONS, PTR_FROM_INT(node_ptr, k),
                                       PTR_FROM_INT(node_ptr, l))));
}

be_ptr MEMOIZER_get(node_ptr key){
  if (MEMOIZER == (hash_ptr) NULL) {
    MEMOIZER = new_assoc();
  }
  return (be_ptr) find_assoc(MEMOIZER, key);
}
void MEMOIZER_put(node_ptr key, be_ptr be){
  if (MEMOIZER == (hash_ptr) NULL) {
    MEMOIZER = new_assoc();
  }
  insert_assoc(MEMOIZER, key, (node_ptr) be);
}
void MEMOIZER_clear(){
  if (MEMOIZER != (hash_ptr) NULL) {
    free_assoc(MEMOIZER);
    MEMOIZER = (hash_ptr) NULL;
  }
}
