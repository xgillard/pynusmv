'''
This module is simply meant to convert the CMU SMV models to NuSMV acceptable syntax.
This is needed because many times, the NuSMV type checking is stronger than that of
CMU SMV and hence, the original models cannot be processed.
'''
import re
import argparse

def arguments():
	parser = argparse.ArgumentParser()

	parser.add_argument("model")
	parser.add_argument("-o", "--output", default="a.out.smv")

	return parser.parse_args()

def sanitize_model(model, output):
	with open(output, 'w') as out:
		with open(model) as f:
			for l in f:
				cln = re.sub("_brokenproba := ", "-- _brokenproba :=", l)
				cln = re.sub("_brokencount := ", "-- _brokencount :=", cln)
				cln = re.sub(r"\b0\b", "FALSE", cln)
				cln = re.sub(r"\b1\b", "TRUE", cln)
				print(re.sub("([a-z])(-)([a-z])", r"\1_\3", cln), file=out, end="")

if __name__ == "__main__":
	args = arguments()
	sanitize_model(args.model, args.output)
