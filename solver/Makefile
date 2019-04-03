# the absolute path to the directory where this makefile is
WD := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# path to clawpack
CLAW := $(WD)/clawpack

# path to geoclaw-landspill src directory
GEOLIB := $(WD)/geoclaw-landspill/src/2d/shallow

# makefile for Clawpack code
CLAWMAKE := $(CLAW)/clawutil/src/Makefile.common

# adjust these variables if desired:
# ----------------------------------
CLAW_PKG := geoclaw             # Clawpack package to use
EXE := $(WD)/bin/xgeoclaw      # Executable to create
SETRUN_FILE := setrun.py        # File containing function to make data
OUTDIR := _output               # Directory for output
SETPLOT_FILE := setplot.py      # File containing function to set plots
PLOTDIR := _plots               # Directory for plots

# default Fortran compiler; can be overwritten by an environment variable
FC ?= gfortran

# compiler flags can be specified here or set as an environment variable
FFLAGS ?= -O2 -fopenmp

# source files used for geoclaw-landspill
include $(GEOLIB)/landspill/Makefile.landspill

# package sources excluded
EXCLUDE_MODULES :=
EXCLUDE_SOURCES := \
	stepgrid.f \
	flag2refine2.f90

# custom source files for this program
MODULES :=
SOURCES := \
	$(CLAW)/riemann/src/rpn2_geoclaw.f \
	$(CLAW)/riemann/src/rpt2_geoclaw.f \
	$(CLAW)/riemann/src/geoclaw_riemann_utils.f \
	$(GEOLIB)/landspill/optimized/stepgrid.f \
	$(GEOLIB)/landspill/optimized/flag2refine2.f90

# include makefile containing standard definitions and make options:
include $(CLAWMAKE)
