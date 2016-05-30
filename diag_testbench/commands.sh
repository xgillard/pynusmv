for i in $(seq 1 5); do
	# NUSMV
	rwgs=$( TIMEFORMAT="%R"; { time ../src/nusmv/NuSMV -bmc -sat_solver minisat models/NO_CONTEXT/RWGS/RGWS_TWIN.smv > /dev/null 2> /dev/null       ; } 2>&1 ) 
	valv=$( TIMEFORMAT="%R"; { time ../src/nusmv/NuSMV -bmc -sat_solver minisat models/NO_CONTEXT/VALVE/VALVE_TWIN.smv > /dev/null 2> /dev/null     ; } 2>&1 )
	cbr_=$( TIMEFORMAT="%R"; { time ../src/nusmv/NuSMV -bmc -sat_solver minisat models/NO_CONTEXT/CBR/CBR_TWIN.smv > /dev/null 2> /dev/null         ; } 2>&1 )
	val2=$( TIMEFORMAT="%R"; { time ../src/nusmv/NuSMV -bmc -sat_solver minisat models/NO_CONTEXT/VALVE/alt_valve_TWIN.smv > /dev/null 2> /dev/null ; } 2>&1 )

	echo "$rwgs ; $valv ; $cbr_ ; $val2 " >> nusmv.run.csv
done

for i in $(seq 1 5); do
	# DIAG-TOOL
	rwgs=$( TIMEFORMAT="%R"; { time ../src/tools/diagnosability.py -or "visible.*" -s "! test._broken ; test._broken" models/NO_CONTEXT/RWGS/RWGS.smv -q > /dev/null 2> /dev/null ;  } 2>&1 )
	valv=$( TIMEFORMAT="%R"; { time ../src/tools/diagnosability.py -or "visible.*" -s "! test.faulty ; test.faulty" models/NO_CONTEXT/VALVE/VALVE.smv -q  > /dev/null 2> /dev/null ; } 2>&1 )
	cbr_=$( TIMEFORMAT="%R"; { time ../src/tools/diagnosability.py -or "visible.led_..led_state" -s "! test.cb_7._broken ; test.cb_7._broken" models/NO_CONTEXT/CBR/CBR.smv -q  > /dev/null 2> /dev/null ; } 2>&1 )
	val2=$( TIMEFORMAT="%R"; { time ../src/tools/diagnosability.py -or "visible.*" -s "! test.faulty ; test.faulty" models/NO_CONTEXT/VALVE/alt_valve.smv -s12 "(G (visible.flow = off -> X visible.flow != off)) & (TIMEFORMAT="%R"; {time G (test.mode = closed -> X test.mode != stuck_open))" -q  > /dev/null 2> /dev/null ; } 2>&1 )

	echo "$rwgs ; $valv ; $cbr_ ; $val2 " >> diagtool.run.csv
done