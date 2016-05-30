def avg_files(r0, r1, r2, r3, r4, out):
    l0 = [ l.split(';') for l in r0 ]
    l1 = [ l.split(';') for l in r1 ]
    l2 = [ l.split(';') for l in r2 ]
    l3 = [ l.split(';') for l in r3 ]
    l4 = [ l.split(';') for l in r4 ]

    for line in range(1, 10):
        for col in range(1, 4):
            value = ( float(l0[line][col]) \
                    + float(l1[line][col]) \
                    + float(l2[line][col]) \
                    + float(l3[line][col]) \
                    + float(l4[line][col]) ) / 5.0
            print('{:.05f} ; '.format(value), end=" ", file=out)
        print(file=out)

def compute_avg(depth, out):
    with open("run_0/results_d{}.csv".format(depth)) as r0:
        with open("run_1/results_d{}.csv".format(depth)) as r1:
            with open("run_2/results_d{}.csv".format(depth)) as r2:
                with open("run_3/results_d{}.csv".format(depth)) as r3:
                    with open("run_4/results_d{}.csv".format(depth)) as r4:
                        avg_files(r0, r1, r2, r3, r4, out)

if __name__ == "__main__":
    with open("avg_hard_d2.csv", "w") as out:
        compute_avg(2, out)

        with open("avg_hard_d3.csv", "w") as out:
            compute_avg(3, out)
