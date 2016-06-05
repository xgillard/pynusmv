"""
Run this script from the src folder.
"""
import os
import time

def timed(fn):
    def decorated(*args,**kwargs):
        start = time.time()
        fn(*args, **kwargs)
        end = time.time()
        return end-start
    return decorated

def fname(depth, size):
    return '../bmc_testbench/hard_instances/philo_depth{}/philo_{}.smv'.format(depth, size)

@timed
def run_main(depth, size, bound):
    instance = fname(depth, size)
    spec     = '[] (p1.waiting => <> ! p1.waiting)' if depth == 2 else \
               '<> [] (p1.waiting => <> ! p1.waiting)'

    os.system("./tools/bmcLTL/main.py -s '{}' -k {} {}".format(spec, bound, instance))

@timed
def run_alt2(depth, size, bound):
    instance = fname(depth, size)
    spec     = 'G (p1.waiting -> F ! p1.waiting)' if depth == 2 else \
               'F G (p1.waiting -> F ! p1.waiting)'

    os.system("./tools/bmcLTL/alternative2.py -s '{}' -k {} {}".format(spec, bound, instance))

@timed
def run_nusmv(depth, size, bound):
    instance = fname(depth, size)

    os.system("./nusmv/NuSMV -bmc -sat_solver minisat -bmc_length {} {}".format(bound, instance))

##########
for run in [2]:#[2, 3, 4]:
    for depth in [2]:#[2, 3]:
        with open("../bmc_testbench/hard_instances/results_bound_d{}.csv".format(depth), "w") as out:
            print("Bound ; NuSMV ; Python ", file=out)
            for bound in range(0, 20):
                print("{} ;".format(bound), end="", file=out)
                print("{:.05f} ; ".format(run_nusmv(depth, 10, bound)), end="", file=out)
                print("{:.05f} ; ".format(run_main(depth,  10, bound)), file=out)
            print("\n", file=out)
