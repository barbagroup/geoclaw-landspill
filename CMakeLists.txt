# minimum version required
cmake_minimum_required(VERSION 3.14)

# cached variables
set(CMAKE_BUILD_TYPE RELEASE CACHE STRING "Either DEBUG, Debug, RELEASE, or Release")
set(CMAKE_Fortran_FLAGS_RELEASE "-O3 -DNDEBUG" CACHE STRING "Compilation flags for release build.")
set(CMAKE_Fortran_FLAGS_Release "-O3 -DNDEBUG" CACHE STRING "Compilation flags for release build.")
set(CMAKE_Fortran_FLAGS_DEBUG "-g" CACHE STRING "Compilation flags for debug build.")
set(CMAKE_Fortran_FLAGS_Debug "-g" CACHE STRING "Compilation flags for debug build.")

# project initialization
project(geoclaw-landspill Fortran)
include(GNUInstallDirs)

# set the output of make
set(CMAKE_VERBOSE_MAKEFILE OFF)
set(CMAKE_COLOR_MAKEFILE ON)

# add flags based on compiler vendor: GNU
if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
    if (CMAKE_GENERATOR MATCHES "Unix Makefiles")
        set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -cpp")
    endif()

    set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -std=legacy")
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

# find scikit-build's extension if this is built as a Python package
if(SKBUILD)
    message(STATUS "Built using scikit-build -- yes")
    find_package(PythonExtensions REQUIRED)  # scikit-build tries to set variables to this package?
    set(DEST "gclandspill")
else()
    message(STATUS "Built using scikit-build -- no")
    set(DEST "${CMAKE_INSTALL_LIBDIR}/gclandspill")
endif()
message(STATUS "Python packages/modules will install to ${DEST}")

# third-party
add_subdirectory(third-party)

# main program
add_subdirectory(gclandspill)

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
