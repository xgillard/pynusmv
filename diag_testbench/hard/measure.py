from os import system
from time import time

def nusmv(difficulty, bound):
  start = time()
  system("../../src/nusmv/NuSMV -bmc -sat_solver minisat -bmc_length 30 twins/HardInstance_TWIN_{}.smv".format(difficulty))
  end = time()
  return end-start


def pynusmv(difficulty, bound):
    start = time()
    system('../../src/tools/diagnosability.py HardInstance.smv -o "a.m.value"  -o "b.m.value" -o "c.m.value" -o "d.m.value" -o "e.m.value" -o "f.m.value" -o "g.m.value" -s "(a.c.value + b.c.value + c.c.value + d.c.value + e.c.value + f.c.value + g.c.value) = 0 ; (a.c.value + b.c.value + c.c.value + d.c.value + e.c.value + f.c.value + g.c.value) = {}" -k {}'.format(difficulty, bound))
    end = time()
    return end-start


if __name__ == "__main__":
    bound = 30
    with open("result.csv", "w") as f:
        print("Difficulty ; NuSMV ; Tool", file=f)
        for i in range(2, 46):
            p = pynusmv(i, bound)
            n = nusmv(i, bound)
            print("{} ; {:.5f} ; {:.5f} ".format(i, n, p))
            print("{} ; {:.5f} ; {:.5f} ".format(i, n, p), file=f)
