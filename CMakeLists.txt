# minimum version required
cmake_minimum_required(VERSION 3.14)

# cached variables
set(CMAKE_BUILD_TYPE RELEASE CACHE STRING "Either DEBUG or RELEASE")
set(CMAKE_Fortran_FLAGS_RELEASE "-O3 -DNDEBUG" CACHE STRING "Compilation flags for release build.")
set(CMAKE_Fortran_FLAGS_DEBUG "-g" CACHE STRING "Compilation flags for debug build.")

# project initialization
project(geoclaw-landspill Fortran)
include(GNUInstallDirs)

# set the output of make
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_COLOR_MAKEFILE ON)

# add flags based on compiler vendor: GNU
if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
    set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -cpp -std=legacy")
    set(CMAKE_Fortran_FLAGS_DEBUG "${CMAKE_Fortran_FLAGS_DEBUG} -fbounds-check")
endif()

# haven't checked Intel Fortran
if(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
    message(FATAL_ERROR "Intel Fortran compiler not yet supported.") 
endif()

# haven't checked PGI Fortran
if(CMAKE_Fortran_COMPILER_ID MATCHES "PGI")
    message(FATAL_ERROR "PGI Fortran compiler not yet supported.") 
endif()

# find openmp flags and add the flag if found
find_package(OpenMP REQUIRED)

if (${OpenMP_Fortran_FOUND})
    set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} ${OpenMP_Fortran_FLAGS}")
endif()

# set the fixed paths
set(AMRLIB "${CMAKE_SOURCE_DIR}/third_party/amrclaw/src/2d")
set(RIEMANNLIB "${CMAKE_SOURCE_DIR}/third_party/riemann/src")
set(GEOLIB "${CMAKE_SOURCE_DIR}/third_party/geoclaw/src/2d/shallow")
set(LANDSPILLLIB "${CMAKE_SOURCE_DIR}/src")

# source files
set(SOURCE
    ${AMRLIB}/amr_module.f90
    ${AMRLIB}/regions_module.f90
    ${AMRLIB}/adjoint_module.f90
    ${GEOLIB}/utility_module.f90
    ${GEOLIB}/geoclaw_module.f90
    ${GEOLIB}/topo_module.f90
    ${GEOLIB}/qinit_module.f90
    ${GEOLIB}/refinement_module.f90
    ${GEOLIB}/fixedgrids_module.f90
    ${GEOLIB}/fgmax_module.f90
    ${GEOLIB}/surge/model_storm_module.f90
    ${GEOLIB}/surge/data_storm_module.f90
    ${GEOLIB}/surge/storm_module.f90
    ${GEOLIB}/gauges_module.f90
    ${GEOLIB}/multilayer/multilayer_module.f90
    ${GEOLIB}/friction_module.f90
    ${GEOLIB}/adjointsup_module.f90
    ${LANDSPILLLIB}/point_source/point_source_module.f90
    ${LANDSPILLLIB}/point_source/point_source_collection_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_abstract_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_constant_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_block_constants_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_cells_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_three_regimes_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_churchill_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_two_regimes_module.f90
    ${LANDSPILLLIB}/darcy_weisbach/darcy_weisbach_module.f90
    ${LANDSPILLLIB}/hydrologic/spm_module.f90
    ${LANDSPILLLIB}/hydrologic/hydro_feature_module.f90
    ${LANDSPILLLIB}/hydrologic/hydro_feature_collection_module.f90
    ${LANDSPILLLIB}/evaporation/evap_base_module.f90
    ${LANDSPILLLIB}/evaporation/fingas1996_module.f90
    ${LANDSPILLLIB}/evaporation/evap_module.f90
    ${LANDSPILLLIB}/landspill_module.f90
    ${AMRLIB}/prefilp.f90
    ${AMRLIB}/trimbd.f90
    ${AMRLIB}/bound.f90
    ${AMRLIB}/intfil.f90
    ${AMRLIB}/flagregions2.f90 
    ${AMRLIB}/quick_sort1.f
    ${AMRLIB}/quick_sort_reals.f
    ${AMRLIB}/estdt.f
    ${AMRLIB}/check4nans.f90
    ${AMRLIB}/init_iflags.f
    ${AMRLIB}/igetsp.f
    ${AMRLIB}/reclam.f
    ${AMRLIB}/birect.f
    ${AMRLIB}/cleanup.f
    ${AMRLIB}/colate2.f
    ${AMRLIB}/bufnst2.f
    ${AMRLIB}/flagger.f
    ${AMRLIB}/fixcapaq.f
    ${AMRLIB}/flglvl2.f
    ${AMRLIB}/fluxad.f
    ${AMRLIB}/fluxsv.f
    ${AMRLIB}/grdfit2.f
    ${AMRLIB}/moment.f90
    ${AMRLIB}/nestck2.f
    ${AMRLIB}/prepc.f
    ${AMRLIB}/prepf.f
    ${AMRLIB}/projec2.f
    ${AMRLIB}/signs.f
    ${AMRLIB}/findcut.f
    ${AMRLIB}/smartbis.f
    ${AMRLIB}/putnod.f
    ${AMRLIB}/putsp.f
    ${AMRLIB}/regrid.f
    ${AMRLIB}/setuse.f
    ${AMRLIB}/stst1.f
    ${AMRLIB}/nodget.f
    ${AMRLIB}/basic.f
    ${AMRLIB}/outval.f
    ${AMRLIB}/copysol.f
    ${AMRLIB}/outvar.f
    ${AMRLIB}/outmsh.f
    ${AMRLIB}/outtre.f
    ${AMRLIB}/domain.f 
    ${AMRLIB}/cellave.f
    ${AMRLIB}/fdisc.f
    ${AMRLIB}/fss.f
    ${AMRLIB}/zeroin.f
    ${AMRLIB}/setflags.f
    ${AMRLIB}/shiftset2.f
    ${AMRLIB}/conck.f
    ${AMRLIB}/domshrink.f
    ${AMRLIB}/domprep.f
    ${AMRLIB}/domup.f
    ${AMRLIB}/domcopy.f
    ${AMRLIB}/setdomflags.f
    ${AMRLIB}/setIndices.f
    ${AMRLIB}/coarseGridFlagSet.f
    ${AMRLIB}/addflags.f
    ${AMRLIB}/baseCheck.f
    ${AMRLIB}/drivesort.f
    ${AMRLIB}/flagcheck.f
    ${AMRLIB}/domgrid.f
    ${AMRLIB}/setPhysBndryFlags.f
    ${AMRLIB}/griddomup.f
    ${AMRLIB}/griddomcopy.f
    ${AMRLIB}/griddomshrink.f
    ${AMRLIB}/intcopy.f
    ${AMRLIB}/preintcopy.f
    ${AMRLIB}/icall.f
    ${AMRLIB}/preicall.f
    ${AMRLIB}/inlinelimiter.f
    ${AMRLIB}/cstore.f
    ${AMRLIB}/saveqc.f
    ${AMRLIB}/opendatafile.f
    ${AMRLIB}/init_bndryList.f
    ${AMRLIB}/resize_bndryList.f
    ${AMRLIB}/init_nodes.f90
    ${AMRLIB}/restrt_nodes.f90
    ${AMRLIB}/resize_nodes.f90
    ${AMRLIB}/init_alloc.f90
    ${AMRLIB}/restrt_alloc.f90
    ${AMRLIB}/resize_alloc.f90
    ${GEOLIB}/setprob.f90
    ${GEOLIB}/qinit.f90
    ${GEOLIB}/topo_update.f90
    ${GEOLIB}/cellgridintegrate2.f
    ${GEOLIB}/topointegral.f
    ${GEOLIB}/bilinearintegral.f
    ${GEOLIB}/src1d.f90
    ${GEOLIB}/step2.f90
    ${GEOLIB}/flux2fw.f
    ${GEOLIB}/qad.f
    ${GEOLIB}/valout.f90
    ${GEOLIB}/filval.f90
    ${GEOLIB}/filpatch.f90
    ${GEOLIB}/bc2amr.f90
    ${GEOLIB}/allowflag.f90 
    ${GEOLIB}/b4step2.f90
    ${GEOLIB}/upbnd.f 
    ${GEOLIB}/setgrd.f
    ${GEOLIB}/gfixup.f
    ${GEOLIB}/ginit.f
    ${GEOLIB}/getmaxspeed.f90
    ${GEOLIB}/advanc.f
    ${GEOLIB}/fgmax_read.f90
    ${GEOLIB}/fgmax_frompatch.f90
    ${GEOLIB}/fgmax_interp.f90
    ${GEOLIB}/fgmax_values.f90
    ${GEOLIB}/fgmax_finalize.f90
    ${GEOLIB}/check.f
    ${GEOLIB}/restrt.f
    ${GEOLIB}/errest.f
    ${GEOLIB}/errf1.f
    ${GEOLIB}/coarsen.f
    ${GEOLIB}/auxcoarsen.f
    ${GEOLIB}/prepbigstep.f
    ${GEOLIB}/prepregstep.f
    ${GEOLIB}/set_eta_init.f90
    ${RIEMANNLIB}/rpn2_geoclaw.f
    ${RIEMANNLIB}/rpt2_geoclaw.f
    ${RIEMANNLIB}/geoclaw_riemann_utils.f
    ${LANDSPILLLIB}/amr2.f90
    ${LANDSPILLLIB}/update.f90 
    ${LANDSPILLLIB}/setaux.f90
    ${LANDSPILLLIB}/src2.f90
    ${LANDSPILLLIB}/tick.f
    ${LANDSPILLLIB}/optimized/stepgrid.f
    ${LANDSPILLLIB}/optimized/flag2refine2.f90 
    )

# executable
add_executable(landspill ${SOURCE})
set_target_properties(
    landspill PROPERTIES 
    Fortran_MODULE_DIRECTORY "${CMAKE_BINARY_DIR}/libs"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# installation rules
install(TARGETS landspill)

# print info
message("")
message("====================================")
message("Config Information:")
message("====================================")
message("")
message("Build type: ${CMAKE_BUILD_TYPE}")
message("Installation path: ${CMAKE_INSTALL_PREFIX}")
message("Compiler: ${CMAKE_Fortran_COMPILER}")
message("Flags: ${CMAKE_Fortran_FLAGS} ${CMAKE_Fortran_FLAGS_${CMAKE_BUILD_TYPE}}")
message("")
