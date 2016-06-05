from time import time
from os import system

def nusmv(f, bound):
    start = time()
    system("../../src/nusmv/NuSMV -bmc -bmc_length {} -sat_solver minisat {}".format(bound, f))
    end = time()
    return end-start

def toolA(f, bound):
    start = time()
    system("../../src/tools/bmcLTL/main.py -k {} -s '[]( p1.waiting => <> ! p1.waiting )' {}".format(bound, f))
    end = time()
    return end-start

def toolB(f, bound):
    start = time()
    system("../../src/tools/bmcLTL/alternative2.py -k {} -s 'G( p1.waiting -> F ! p1.waiting )' {}".format(bound, f))
    end = time()
    return end-start

#print(nusmv("d2/philo_30.smv", 60))
#print(toolA("d2/philo_2.smv", 45))

bound = 30
with open("result.csv", "w") as f:
    print("N  ; NuSMV ; Tool A ; Tool B", file=f)
    for i in range(2, 60):
        test_file = "d2/philo_{}.smv".format(i)
        n = nusmv(test_file, bound)
        b = toolB(test_file, bound)
        a = toolA(test_file, bound)
        print("{} ; {:.5f} ; {:.5f} ; {:.5f} ".format(i, n, a, b))
        print("{} ; {:.5f} ; {:.5f} ; {:.5f} ".format(i, n, a, b), file=f)
