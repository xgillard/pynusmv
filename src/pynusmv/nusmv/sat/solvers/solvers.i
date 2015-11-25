%module(package="pynusmv.nusmv.sat.solvers") solvers

%include ../../global.i

%{
#include "../../../../nusmv/nusmv-config.h"
#include "../../../../nusmv/src/utils/defs.h"
#include "../../../../nusmv/src/utils/object.h"

/************************ MiniSat ************************/
#include "../../../../nusmv/src/sat/solvers/SatMiniSat.h"
#include "../../../../nusmv/src/sat/solvers/satMiniSatIfc.h"

/************************ ZChaff ************************/
#include "../../../../zchaff/zchaff64/SAT_C.h"
#include "../../../../nusmv/src/sat/solvers/SatZchaff.h"
#include "../../../../nusmv/src/sat/solvers/satZChaffIfc.h"
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