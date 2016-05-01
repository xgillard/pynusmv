%module(package="pynusmv.nusmv.sat.solvers") solvers

%include ../../global.i

%{
#include "../../../../nusmv/nusmv-config.h"
#include "../../../../nusmv/src/utils/defs.h"
#include "../../../../nusmv/src/utils/object.h"

#include "../../../../nusmv/src/sat/SatSolver.h"
#include "../../../../nusmv/src/sat/SatIncSolver.h"
/************************ MiniSat ************************/
#include "../../../../nusmv/src/sat/solvers/SatMiniSat.h"          /* public features of minisat  */ 
#include "../../../../nusmv/src/sat/solvers/satMiniSatIfc.h"       /* RAW minisat                 */

/************************ ZChaff ************************/
#include "../../../../zchaff/zchaff64/SAT_C.h"
#include "../../../../nusmv/src/sat/solvers/SatZchaff.h"           /* public features of zchaff   */
#include "../../../../nusmv/src/sat/solvers/satZChaffIfc.h"        /* RAW zchaff                  */
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../nusmv/src/utils/defs.h
%include ../../../../nusmv/src/utils/object.h
%include "../../../../nusmv/src/sat/solvers/SatMiniSat.h"
%include "../../../../nusmv/src/sat/solvers/satMiniSatIfc.h"

// Ignore functions not implemented in ZChaff
%ignore SAT_SetClsDeletionInterval;
%ignore SAT_SetMaxUnrelevance;
%ignore SAT_SetMinClsLenForDelete;
%ignore SAT_SetMaxConfClsLenAllowed;
%include "../../../../nusmv/src/sat/solvers/SatZChaff.h"
%include "../../../../nusmv/src/sat/solvers/satZChaffIfc.h"

%inline %{

	/* casting solvers pointers to their 'parent' type */
	SatIncSolver_ptr SatMinisat_ptr_cast_to_SatIncSolver(SatMinisat_ptr ptr){
		return (SatIncSolver_ptr) ptr;
	}
	SatIncSolver_ptr SatZchaff_ptr_cast_to_SatIncSolver(SatZchaff_ptr ptr){
		return (SatIncSolver_ptr) ptr;
	}
%}