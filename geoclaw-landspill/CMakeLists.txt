# use this variable to shorten the paths
set(LANDSPILLLIB "${CMAKE_SOURCE_DIR}/geoclaw-landspill/src")

# geoclaw-landspill-bin
add_executable(geoclaw-landspill-bin
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
    ${LANDSPILLLIB}/amr2.f90
    ${LANDSPILLLIB}/update.f90 
    ${LANDSPILLLIB}/setaux.f90
    ${LANDSPILLLIB}/src2.f90
    ${LANDSPILLLIB}/tick.f
    ${LANDSPILLLIB}/optimized/stepgrid.f
    ${LANDSPILLLIB}/optimized/flag2refine2.f90 
    )

# location of third-party libs and modules
target_link_libraries(geoclaw-landspill-bin geoclaw-landspill-third-party)
target_include_directories(geoclaw-landspill-bin PRIVATE $<TARGET_PROPERTY:geoclaw-landspill-third-party,BINARY_DIR>)

# installation rules for the fortran executable
install(TARGETS geoclaw-landspill-bin DESTINATION "${DEST}/bin")

# installation rules for python lib
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/__init__.py" DESTINATION "${DEST}")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/__main__.py" DESTINATION "${DEST}")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/_preprocessing.py" DESTINATION "${DEST}")
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/_postprocessing" DESTINATION "${DEST}")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/_misc.py" DESTINATION "${DEST}")
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/data.py" DESTINATION "${DEST}")

# create an executable python script for non-setup.py installation
if (NOT SKBUILD)
    install(
        FILES "${CMAKE_CURRENT_SOURCE_DIR}/__main__.py"
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE
        DESTINATION "${CMAKE_INSTALL_BINDIR}"
        RENAME "geoclaw-landspill"
    )
endif()
