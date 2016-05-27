%module(package="pynusmv.bmc.lower_intf") lower_intf

%{
#include "../../../nusmv/nusmv-config.h"
#include "../../../nusmv/src/utils/defs.h"
#include "lower_intf.h"
%}

%feature("autodoc", 1);

%include ../../nusmv/typedefs.tpl

%include ../../../nusmv/src/utils/defs.h
%include lower_intf.h
