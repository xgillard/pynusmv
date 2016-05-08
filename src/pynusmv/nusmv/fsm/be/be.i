%module(package="pynusmv.nusmv.fsm.be") be

%include ../../global.i

%{
#include "../../../../nusmv/nusmv-config.h"
#include "../../../../nusmv/src/utils/defs.h"
#include "../../../../nusmv/src/fsm/be/BeFsm.h" 
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../nusmv/src/utils/defs.h
%include ../../../../nusmv/src/fsm/be/BeFsm.h

%inline %{
	
be_ptr node_ptr_to_be_ptr(node_ptr node){
	return (be_ptr) node;
}
	
%}