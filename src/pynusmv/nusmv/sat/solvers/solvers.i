%module(package="pynusmv.nusmv.sat.solvers") solvers

%include ../../global.i

%{
#include "../../../../nusmv/nusmv-config.h"
#include "../../../../nusmv/src/utils/defs.h"
#include "../../../../nusmv/src/utils/object.h"
#include "../../../../nusmv/src/sat/solvers/SatMiniSat.h"
#include "../../../../nusmv/src/sat/solvers/satMiniSatIfc.h"
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../nusmv/src/utils/defs.h
%include ../../../../nusmv/src/utils/object.h
%include "../../../../nusmv/src/sat/solvers/SatMiniSat.h"
%include "../../../../nusmv/src/sat/solvers/satMiniSatIfc.h"