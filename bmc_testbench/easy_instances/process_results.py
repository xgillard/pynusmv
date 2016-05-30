import sys

def fname(tool, depth, run):
    return 'run_{}/{}_depth{}.csv'.format(run, tool, depth)

def average_csv(run0, run1, run2, run3, run4, out=sys.stdout):
    r0 = [ l.split(';') for l in run0 ]
    r1 = [ l.split(';') for l in run1 ]
    r2 = [ l.split(';') for l in run2 ]
    r3 = [ l.split(';') for l in run3 ]
    r4 = [ l.split(';') for l in run4 ]

    for line in range(1, 22):
        for column in range(10):
            avg_val = (float(r0[line][column]) \
                     + float(r1[line][column]) \
                     + float(r2[line][column]) \
                     + float(r3[line][column]) \
                     + float(r4[line][column])) /5.0
            print("{:.05f} ; ".format(avg_val), end=" ", file=out)
        print("", file=out)


def average(tool, depth, out=sys.stdout):
    run = lambda run: fname(tool, depth, run)
    with open(run(0)) as run0:
        with open(run(1)) as run1:
            with open(run(2)) as run2:
                with open(run(3)) as run3:
                    with open(run(4)) as run4:
                        average_csv(run0,run1,run2,run3,run4, out)

def ratio(a, b, out=sys.stdout):
    ra = [ l.split(';') for l in a ]
    rb = [ l.split(';') for l in b ]

    for line in range(21):
        for column in range(10):
            value = (float(ra[line][column]) / float(rb[line][column]) )
            print("{:.05f} ; ".format(value), end=" ", file=out)
        print("", file=out)


if __name__ == "__main__":
    #for tool in ['main', 'alt2', 'nusmv']:
    #    for depth in [2, 3]:
    #        with open('average_{}_depth{}.csv'.format(tool, depth), 'w') as out:
    #            average(tool, depth, out)
    with open('ratios/src_main.csv') as tool:
        with open('ratios/src_nusmv.csv') as nusmv:
            with open("ratios/ratio_main_nusmv.csv", 'w') as out:
                ratio(tool, nusmv, out)
