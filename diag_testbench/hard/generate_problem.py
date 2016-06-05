def generate_twins(n):
    return """
--
-- This file contains (a totally made up and artificial) model that provides a good case of
-- easy to hard instance for diagnosability test. The parameter that makes the instance harder
-- and harder to solve is the total sum of the c1 or c2.
--
-- COMMAND :
-- time ../../src/nusmv/NuSMV -bmc -sat_solver minisat -bmc_length 30 HardInstance_TWIN.smv
--
-- Author: X. Gillard
--
MODULE Counter
VAR
	value : 0 .. 60;
ASSIGN
	init(value) := 0 .. 5;
	next(value) := value + 1;


MODULE Modulo(cnt, k)
VAR
	value : 0 .. 1;
INVAR
	value = (cnt.value mod k) mod 2;

MODULE Config
VAR
	c : Counter;
	m : Modulo(c, 50);

MODULE Test
VAR
	a : Config;
	b : Config;
	c : Config;
	d : Config;
	e : Config;
	f : Config;
	g : Config;

MODULE Twin
VAR
	a : Config;
	b : Config;
	c : Config;
	d : Config;
	e : Config;
	f : Config;
	g : Config;

MODULE main
VAR
	test : Test;
	twin : Twin;

INVAR
	(test.a.m.value = twin.a.m.value) &
	(test.b.m.value = twin.b.m.value) &
	(test.c.m.value = twin.c.m.value) &
	(test.d.m.value = twin.d.m.value) &
	(test.e.m.value = twin.e.m.value) &
	(test.f.m.value = twin.f.m.value) &
	(test.g.m.value = twin.g.m.value) ;

LTLSPEC
	G ! ( (test.a.c.value + test.b.c.value + test.c.c.value + test.d.c.value + test.e.c.value + test.f.c.value + test.g.c.value = {} )
		& (twin.a.c.value + twin.b.c.value + twin.c.c.value + twin.d.c.value + twin.e.c.value + twin.f.c.value + twin.g.c.value = 0) )
""".format(n).strip()

if __name__ == "__main__":
    for i in range(46):
        with open("HardInstance_TWIN_{}.smv".format(i), "w") as f:
            print(generate_twins(i), file=f)
