:


function testbench_alt2 {
	local depth=$1
	local nphilo=$2
	local bound=$3
	local spec=$4

	local model="philo_depth$depth/philo_$nphilo.smv"

	local elapsed=$( TIMEFORMAT="%R"; { time ../src/tools/bmcLTL/alternative2.py -s "$spec" -k $bound $model > /dev/null 2> /dev/null ; } 2>&1 )

	echo "$elapsed"
}

function alt2_alltests {
	for depth in `seq 2 3`; do
		output="alt2_depth$depth.csv"

		# clear the content
		echo "" > $output

		# for each bound
		for bound in `seq 10 30`; do
			printf "$bound ; " >> $output
			# for each model
			for i in `seq 2 10`; do
				if [ $depth = 2 ]; then
					printf "$(testbench_alt2 $depth $i $bound 'G (p1.waiting -> F ! p1.waiting)') ;" >> $output
				else
					printf "$(testbench_alt2 $depth $i $bound 'F G (p1.waiting -> F ! p1.waiting)') ;" >> $output
				fi
			done
			printf "\n" >> $output
		done
	done
}

alt2_alltests
