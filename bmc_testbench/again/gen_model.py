def gen_header():
	return  """
-------------------------------------------------------------------------------
-- These modules model a version of the well known dining philosophers problem
-- it is based on an implemementation proposed by D. Hoffman from East Carolina
-- University in the scope of SENG6250, session of fall 2015.
-- The video is available online at : https://youtu.be/JBESxiZ5Wao
-------------------------------------------------------------------------------
MODULE main
-- This module is the 'program driver' : it associates the various philosophers
-- with their forks. Another way to consider the role of this 'main' module is
-- to consider as being the table around which the philosophers are dining.
"""

def gen_forks(n):
	values = [str(i+1) for i in range(n)]
	return  "  forks : array 0..{} of {{ {}, nobody}};\n".format((n-1), ", ".join(values))

def gen_philo(i, n):
	return "  p{}    : process philosopher({}, forks[{}], forks[{}]);\n".format(i, i, (i-1), (i%n))

def gen_variables(n):
	result = "VAR\n"
	result+= gen_forks(n)
	for i in range(n):
		result += gen_philo(i+1, n)
	return result+"\n"

def gen_assign(n):
	result = "ASSIGN\n"
	for i in range(n):
		result += "  init(forks[{}]) := nobody;\n".format(i)
	return result

def gen_rest(depth):
	spec = "G (p1.waiting -> F !p1.waiting);" if depth == 2 else \
	       "F G (p1.waiting -> F !p1.waiting);"
	return """
LTLSPEC
  {}

MODULE philosopher(id, left, right)
-- This module models the behavior of one of the philosopher participating to
-- the dinner.
VAR
  status : {{thinking, hungry, eating, done}};
DEFINE
  gotleft := (left=id);
  gotright:= (right=id);
  waiting := ((status = hungry) & gotleft & !gotright);

ASSIGN
  init(status) := thinking;

  next (status) := case
    status = thinking : {{thinking, hungry}};
    status = hungry & gotleft & gotright : eating;
    status = eating : {{eating, done}};
    status = done & !gotleft & !gotright : thinking;
    TRUE : status;
    esac;

  next(left) := case
    status = hungry & left = nobody : id ;
    status = done & gotleft         : nobody;
    TRUE                            : left;
    esac;

  next(right) := case
    status = hungry & gotleft & right = nobody: id;
    status = done   & gotright      : nobody;
    TRUE                            : right;
    esac;

FAIRNESS
  -- This fairness constraint forces NuSMV to consider traces where the
  -- philosophers processes actually do run.
  !waiting;
 """.format(spec)

def generate_model(nb_philo, depth=2):
	""
	model = gen_header()
	model+= gen_variables(nb_philo)
	model+= gen_assign(nb_philo)
	model+= gen_rest(depth)
	return model

if __name__ == "__main__":
	for n in range(2, 60):
		with open("d2/philo_{}.smv".format(n), 'w') as f:
			f.write(generate_model(n, 2))
		with open("d3/philo_{}.smv".format(n), 'w') as f:
			f.write(generate_model(n, 3))
