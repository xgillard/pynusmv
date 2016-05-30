:

function testbench_nusmv {
	local depth=$1
	local nphilo=$2
	local bound=$3

	local model="philo_depth$depth/philo_$nphilo.smv"

	local elapsed=$( TIMEFORMAT="%R"; { time ../src/nusmv/NuSMV -bmc -sat_solver minisat -bmc_length $bound $model > /dev/null 2> /dev/null ; } 2>&1 )

	echo "$elapsed"
}

function nusmv_alltests {
	for depth in `seq 2 3`; do
		output="nusmv_depth$depth.csv"

		# clear the content
		echo "" > $output

		# for each bound
		for bound in `seq 10 30`; do
			printf "$bound ; " >> $output
			for i in `seq 2 10`; do
				printf "$(testbench_nusmv $depth $i $bound ) ;" >> $output
			done
			printf "\n" >> $output
		done
	done
}

nusmv_alltests
