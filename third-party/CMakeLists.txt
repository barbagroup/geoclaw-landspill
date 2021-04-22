# amrclaw
set(AMRCLAW "${CMAKE_CURRENT_SOURCE_DIR}/amrclaw")
set(AMRCLAW_FORTRAN "${AMRCLAW}/src/2d")
set(AMRCLAW_PYTHON "${AMRCLAW}/src/python/amrclaw")

# riemann
set(RIEMANN_FORTRAN "${CMAKE_CURRENT_SOURCE_DIR}/riemann/src")

# geoclaw
set(GEOCLAW "${CMAKE_CURRENT_SOURCE_DIR}/geoclaw")
set(GEOCLAW_FORTRAN "${GEOCLAW}/src/2d/shallow")
set(GEOCLAW_PYTHON "${GEOCLAW}/src/python/geoclaw")

# pyclaw
set(PYCLAW "${CMAKE_CURRENT_SOURCE_DIR}/pyclaw")
set(PYCLAW_PYTHON "${PYCLAW}/src/pyclaw")

# clawutil
set(CLAWUTIL "${CMAKE_CURRENT_SOURCE_DIR}/clawutil")
set(CLAWUTIL_PYTHON "${CLAWUTIL}/src/python/clawutil")

# lump all fortran dependencies into one single library
add_library(geoclaw-landspill-third-party STATIC
    ${AMRCLAW_FORTRAN}/amr_module.f90
    ${AMRCLAW_FORTRAN}/regions_module.f90
    ${AMRCLAW_FORTRAN}/adjoint_module.f90
    ${GEOCLAW_FORTRAN}/utility_module.f90
    ${GEOCLAW_FORTRAN}/geoclaw_module.f90
    ${GEOCLAW_FORTRAN}/topo_module.f90
    ${GEOCLAW_FORTRAN}/qinit_module.f90
    ${GEOCLAW_FORTRAN}/refinement_module.f90
    ${GEOCLAW_FORTRAN}/fixedgrids_module.f90
    ${GEOCLAW_FORTRAN}/fgmax_module.f90
    ${GEOCLAW_FORTRAN}/surge/model_storm_module.f90
    ${GEOCLAW_FORTRAN}/surge/data_storm_module.f90
    ${GEOCLAW_FORTRAN}/surge/storm_module.f90
    ${GEOCLAW_FORTRAN}/gauges_module.f90
    ${GEOCLAW_FORTRAN}/multilayer/multilayer_module.f90
    ${GEOCLAW_FORTRAN}/friction_module.f90
    ${GEOCLAW_FORTRAN}/adjointsup_module.f90
    ${AMRCLAW_FORTRAN}/prefilp.f90
    ${AMRCLAW_FORTRAN}/trimbd.f90
    ${AMRCLAW_FORTRAN}/bound.f90
    ${AMRCLAW_FORTRAN}/intfil.f90
    ${AMRCLAW_FORTRAN}/flagregions2.f90 
    ${AMRCLAW_FORTRAN}/quick_sort1.f
    ${AMRCLAW_FORTRAN}/quick_sort_reals.f
    ${AMRCLAW_FORTRAN}/estdt.f
    ${AMRCLAW_FORTRAN}/check4nans.f90
    ${AMRCLAW_FORTRAN}/init_iflags.f
    ${AMRCLAW_FORTRAN}/igetsp.f
    ${AMRCLAW_FORTRAN}/reclam.f
    ${AMRCLAW_FORTRAN}/birect.f
    ${AMRCLAW_FORTRAN}/cleanup.f
    ${AMRCLAW_FORTRAN}/colate2.f
    ${AMRCLAW_FORTRAN}/bufnst2.f
    ${AMRCLAW_FORTRAN}/flagger.f
    ${AMRCLAW_FORTRAN}/fixcapaq.f
    ${AMRCLAW_FORTRAN}/flglvl2.f
    ${AMRCLAW_FORTRAN}/fluxad.f
    ${AMRCLAW_FORTRAN}/fluxsv.f
    ${AMRCLAW_FORTRAN}/grdfit2.f
    ${AMRCLAW_FORTRAN}/moment.f90
    ${AMRCLAW_FORTRAN}/nestck2.f
    ${AMRCLAW_FORTRAN}/prepc.f
    ${AMRCLAW_FORTRAN}/prepf.f
    ${AMRCLAW_FORTRAN}/projec2.f
    ${AMRCLAW_FORTRAN}/signs.f
    ${AMRCLAW_FORTRAN}/findcut.f
    ${AMRCLAW_FORTRAN}/smartbis.f
    ${AMRCLAW_FORTRAN}/putnod.f
    ${AMRCLAW_FORTRAN}/putsp.f
    ${AMRCLAW_FORTRAN}/regrid.f
    ${AMRCLAW_FORTRAN}/setuse.f
    ${AMRCLAW_FORTRAN}/stst1.f
    ${AMRCLAW_FORTRAN}/nodget.f
    ${AMRCLAW_FORTRAN}/basic.f
    ${AMRCLAW_FORTRAN}/outval.f
    ${AMRCLAW_FORTRAN}/copysol.f
    ${AMRCLAW_FORTRAN}/outvar.f
    ${AMRCLAW_FORTRAN}/outmsh.f
    ${AMRCLAW_FORTRAN}/outtre.f
    ${AMRCLAW_FORTRAN}/domain.f 
    ${AMRCLAW_FORTRAN}/cellave.f
    ${AMRCLAW_FORTRAN}/fdisc.f
    ${AMRCLAW_FORTRAN}/fss.f
    ${AMRCLAW_FORTRAN}/zeroin.f
    ${AMRCLAW_FORTRAN}/setflags.f
    ${AMRCLAW_FORTRAN}/shiftset2.f
    ${AMRCLAW_FORTRAN}/conck.f
    ${AMRCLAW_FORTRAN}/domshrink.f
    ${AMRCLAW_FORTRAN}/domprep.f
    ${AMRCLAW_FORTRAN}/domup.f
    ${AMRCLAW_FORTRAN}/domcopy.f
    ${AMRCLAW_FORTRAN}/setdomflags.f
    ${AMRCLAW_FORTRAN}/setIndices.f
    ${AMRCLAW_FORTRAN}/coarseGridFlagSet.f
    ${AMRCLAW_FORTRAN}/addflags.f
    ${AMRCLAW_FORTRAN}/baseCheck.f
    ${AMRCLAW_FORTRAN}/drivesort.f
    ${AMRCLAW_FORTRAN}/flagcheck.f
    ${AMRCLAW_FORTRAN}/domgrid.f
    ${AMRCLAW_FORTRAN}/setPhysBndryFlags.f
    ${AMRCLAW_FORTRAN}/griddomup.f
    ${AMRCLAW_FORTRAN}/griddomcopy.f
    ${AMRCLAW_FORTRAN}/griddomshrink.f
    ${AMRCLAW_FORTRAN}/intcopy.f
    ${AMRCLAW_FORTRAN}/preintcopy.f
    ${AMRCLAW_FORTRAN}/icall.f
    ${AMRCLAW_FORTRAN}/preicall.f
    ${AMRCLAW_FORTRAN}/inlinelimiter.f
    ${AMRCLAW_FORTRAN}/cstore.f
    ${AMRCLAW_FORTRAN}/saveqc.f
    ${AMRCLAW_FORTRAN}/opendatafile.f
    ${AMRCLAW_FORTRAN}/init_bndryList.f
    ${AMRCLAW_FORTRAN}/resize_bndryList.f
    ${AMRCLAW_FORTRAN}/init_nodes.f90
    ${AMRCLAW_FORTRAN}/restrt_nodes.f90
    ${AMRCLAW_FORTRAN}/resize_nodes.f90
    ${AMRCLAW_FORTRAN}/init_alloc.f90
    ${AMRCLAW_FORTRAN}/restrt_alloc.f90
    ${AMRCLAW_FORTRAN}/resize_alloc.f90
    ${GEOCLAW_FORTRAN}/setprob.f90
    ${GEOCLAW_FORTRAN}/qinit.f90
    ${GEOCLAW_FORTRAN}/topo_update.f90
    ${GEOCLAW_FORTRAN}/cellgridintegrate2.f
    ${GEOCLAW_FORTRAN}/topointegral.f
    ${GEOCLAW_FORTRAN}/bilinearintegral.f
    ${GEOCLAW_FORTRAN}/src1d.f90
    ${GEOCLAW_FORTRAN}/step2.f90
    ${GEOCLAW_FORTRAN}/flux2fw.f
    ${GEOCLAW_FORTRAN}/qad.f
    ${GEOCLAW_FORTRAN}/valout.f90
    ${GEOCLAW_FORTRAN}/filval.f90
    ${GEOCLAW_FORTRAN}/filpatch.f90
    ${GEOCLAW_FORTRAN}/bc2amr.f90
    ${GEOCLAW_FORTRAN}/b4step2.f90
    ${GEOCLAW_FORTRAN}/upbnd.f 
    ${GEOCLAW_FORTRAN}/setgrd.f
    ${GEOCLAW_FORTRAN}/gfixup.f
    ${GEOCLAW_FORTRAN}/ginit.f
    ${GEOCLAW_FORTRAN}/getmaxspeed.f90
    ${GEOCLAW_FORTRAN}/advanc.f
    ${GEOCLAW_FORTRAN}/fgmax_read.f90
    ${GEOCLAW_FORTRAN}/fgmax_frompatch.f90
    ${GEOCLAW_FORTRAN}/fgmax_interp.f90
    ${GEOCLAW_FORTRAN}/fgmax_values.f90
    ${GEOCLAW_FORTRAN}/fgmax_finalize.f90
    ${GEOCLAW_FORTRAN}/check.f
    ${GEOCLAW_FORTRAN}/restrt.f
    ${GEOCLAW_FORTRAN}/errest.f
    ${GEOCLAW_FORTRAN}/errf1.f
    ${GEOCLAW_FORTRAN}/coarsen.f
    ${GEOCLAW_FORTRAN}/auxcoarsen.f
    ${GEOCLAW_FORTRAN}/prepbigstep.f
    ${GEOCLAW_FORTRAN}/prepregstep.f
    ${GEOCLAW_FORTRAN}/set_eta_init.f90
    ${RIEMANN_FORTRAN}/rpn2_geoclaw.f
    ${RIEMANN_FORTRAN}/rpt2_geoclaw.f
    ${RIEMANN_FORTRAN}/geoclaw_riemann_utils.f
)

# install amrclaw's Python module
install(FILES "${AMRCLAW}/LICENSE" DESTINATION "${DEST}/amrclaw")
install(FILES "${AMRCLAW_PYTHON}/data.py" DESTINATION "${DEST}/amrclaw")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/amrclaw_init.py" DESTINATION "${DEST}/amrclaw" RENAME "__init__.py")

# install geoclaw's Python module
install(FILES "${GEOCLAW}/LICENSE" DESTINATION "${DEST}/geoclaw")
install(FILES "${GEOCLAW_PYTHON}/data.py" DESTINATION "${DEST}/geoclaw")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/geoclaw_init.py" DESTINATION "${DEST}/geoclaw" RENAME "__init__.py")

# install pyclaw's Python module
install(FILES "${PYCLAW}/LICENSE" DESTINATION "${DEST}/pyclaw")
install(FILES "${PYCLAW_PYTHON}/util.py" DESTINATION "${DEST}/pyclaw")
install(FILES "${PYCLAW_PYTHON}/state.py" DESTINATION "${DEST}/pyclaw")
install(FILES "${PYCLAW_PYTHON}/solution.py" DESTINATION "${DEST}/pyclaw")
install(FILES "${PYCLAW_PYTHON}/geometry.py" DESTINATION "${DEST}/pyclaw")
install(FILES "${PYCLAW_PYTHON}/gauges.py" DESTINATION "${DEST}/pyclaw")
install(DIRECTORY "${PYCLAW_PYTHON}/fileio" DESTINATION "${DEST}/pyclaw")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/pyclaw_init.py" DESTINATION "${DEST}/pyclaw" RENAME "__init__.py")

# install clawutil's Python module
install(FILES "${CLAWUTIL}/LICENSE" DESTINATION "${DEST}/clawutil")
install(FILES "${CLAWUTIL_PYTHON}/data.py" DESTINATION "${DEST}/clawutil")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/clawutil_init.py" DESTINATION "${DEST}/clawutil" RENAME "__init__.py")
