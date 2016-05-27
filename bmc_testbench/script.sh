:


function testbench_main {
	local nphilo=$1
	local bound=$2
	local spec=$3

	local model="philo/philo_$nphilo.smv"

	local elapsed=$( TIMEFORMAT="%R"; { time ../src/tools/bmcLTL/main.py -s "$spec" -k $bound $model > /dev/null 2> /dev/null ; } 2>&1 )

	echo "$elapsed"
}

function testbench_nusmv {
	local nphilo=$1
	local bound=$2
	local spec=$3

	local model="philo/philo_$nphilo.smv"

	local elapsed=$( TIMEFORMAT="%R"; { time ../src/nusmv/NuSMV -bmc -sat_solver minisat -bmc_length $bound $model > /dev/null 2> /dev/null ; } 2>&1 )

	echo "$elapsed"
}

#for bound in `seq 10 35`; do
#	printf "$bound ; "
#	for i in `seq 2 10`; do
#		printf "$(testbench_main $i $bound '[] (p1.waiting => <> ! p1.waiting)') ;"
#	done
#	printf "\n"
#done

for bound in `seq 10 35`; do
	printf "$bound ; "
	for i in `seq 2 10`; do
		printf "$(testbench_nusmv $i $bound ) ;"
	done
	printf "\n"
done
