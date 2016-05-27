.PHONY: cudd zchaff minisat nusmv bmc_lower pynusmv test


SF=$(shell getconf LONG_BIT)
ifeq ($(SF), 64)
SF=_64bit
else
SF=
endif

SYS=$(shell gcc -dumpmachine)
ifneq (,$(findstring darwin,$(SYS)))
OS=_os_x
else ifneq (,$(findstring mingw,$(SYS)))
OS=_mingw
else
OS=
endif

ifndef PYTHON
PYTHON=python3
endif

ifndef SWIG
ifneq ($(wildcard ../dep/swig-2.0.6/swig),)
SWIG=../dep/swig-2.0.6/swig
endif
endif

ifndef SWIG_LIB
ifneq ($(wildcard ../dep/swig-2.0.6/swig),)
export SWIG_LIB=../dep/swig-2.0.6/Lib/
endif
endif



all: cudd zchaff nusmv bmc_lower pynusmv


cudd:
	$(get-sf)
	$(get-os)
	make -C cudd-2.4.1.1 -f Makefile$(OS)$(SF)

zchaff:
	@if [ ! -f zchaff_v2007.3.12/SAT_C.h ]; then \
		cd zchaff; \
		./build.sh; \
	fi

minisat:
	@if [ ! -f MiniSat_v070721/libMiniSat.a ]; then \
		cd MiniSat; \
		./build.sh; \
	fi

nusmv: cudd zchaff minisat
	@if [ ! -f nusmv/NuSMV ]; then \
		cd nusmv; \
		if [ ! -f Makefile ]; then \
			./configure --enable-zchaff --enable-minisat CFLAGS="-g -O2 -fPIC"; \
		fi; \
		make; \
	fi

bmc_lower:
	gcc -c pynusmv/bmc/lower_intf/lower_intf.c -o pynusmv/bmc/lower_intf/lower_intf.o -Inusmv -Inusmv/src -Icudd-2.4.1.1/include

pynusmv: nusmv bmc_lower
ifneq ($(SWIG),)
	@if [ ! -f lib/libnusmv.so ]; then ./build_libnusmv.sh; fi; \
	$(PYTHON) setup.py build_ext --inplace --swig=$(SWIG)
else
ifneq ($(wildcard ../dep/swig-2.0.6/swig),)
	@if [ ! -f lib/libnusmv.so ]; then ./build_libnusmv.sh; fi; \
	$(PYTHON) setup.py build_ext --inplace --swig=../dep/swig-2.0.6/swig
else
	@if [ ! -f lib/libnusmv.so ]; then ./build_libnusmv.sh; fi; \
	$(PYTHON) setup.py build_ext --inplace
endif
endif

test: pynusmv
	$(PYTHON) -m unittest discover
