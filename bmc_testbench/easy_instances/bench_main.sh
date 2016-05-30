:


function testbench_main {
	local depth=$1
	local nphilo=$2
	local bound=$3
	local spec=$4

	local model="philo_depth$depth/philo_$nphilo.smv"

	local elapsed=$( TIMEFORMAT="%R"; { time ../src/tools/bmcLTL/main.py -s "$spec" -k $bound $model > /dev/null 2> /dev/null ; } 2>&1 )

	echo "$elapsed"
}

function main_alltests {
	local iteration=$1
	for depth in `seq 2 3`; do
		output="run_$iteration/main_depth$depth.csv"

		# clear the content
		echo "" > $output

		# for each bound
		for bound in `seq 10 30`; do
			printf "$bound ; " >> $output
			# for each model
			for i in `seq 2 10`; do
				if [ $depth = 2 ]; then
					printf "$(testbench_main $depth $i $bound '[] (p1.waiting => <> ! p1.waiting)') ;" >> $output
				else
					printf "$(testbench_main $depth $i $bound '<> [] (p1.waiting => <> ! p1.waiting)') ;" >> $output
				fi
			done
			printf "\n" >> $output
		done
	done
}

function five_times {
	for iter in $(seq 0 4); do
		echo "Starting $iter"
		main_alltests $iter;
		echo "Done $iter"
	done
}

five_times
