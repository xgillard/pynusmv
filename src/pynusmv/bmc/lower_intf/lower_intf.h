#ifndef __PYNUSMV_BMC_LOWER_IFACE_H__
#define __PYNUSMV_BMC_LOWER_IFACE_H__

#include <stdlib.h>
#include <nusmv-config.h>
#include <utils/defs.h>

#include <bmc/bmc.h>

be_ptr proposition_at_time(BeEnc_ptr enc, node_ptr formula, int time);
int succ(int k, int l, int time);
be_ptr loop_condition(BeEnc_ptr enc, int k, int l);
be_ptr fairness_constraint(BeFsm_ptr fsm, int k, int l);

be_ptr sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset);
be_ptr sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset);


node_ptr MEMOIZER_key(node_ptr wff, int time, int k, int l);
be_ptr MEMOIZER_get(node_ptr key);
void MEMOIZER_put(node_ptr key, be_ptr be);
void MEMOIZER_clear();

be_ptr NO_MEMOIZE_sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset);
be_ptr NO_MEMOIZE_sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset);

#endif
