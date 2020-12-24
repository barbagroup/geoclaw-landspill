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
set(CMAKE_VERBOSE_MAKEFILE OFF)
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

# find scikit-build's extension if this is built as a Python package
if(SKBUILD)
    find_package(PythonExtensions REQUIRED)
    message(STATUS "Built using scikit-build -- yes")
    message(STATUS "PYTHON_PREFIX: ${PYTHON_PREFIX}")
    message(STATUS "PYTHON_SITE_PACKAGES_DIR: ${PYTHON_SITE_PACKAGES_DIR}")
    message(STATUS "PYTHON_RELATIVE_SITE_PACKAGES_DIR: ${PYTHON_RELATIVE_SITE_PACKAGES_DIR}")
    message(STATUS "PYTHON_SEPARATOR: ${PYTHON_SEPARATOR}")
    message(STATUS "PYTHON_PATH_SEPARATOR: ${PYTHON_PATH_SEPARATOR}")
    message(STATUS "PYTHON_EXTENSION_MODULE_SUFFIX: ${PYTHON_EXTENSION_MODULE_SUFFIX}")
else()
    message(STATUS "Built using scikit-build - no")
endif()

# third-party
add_subdirectory(third-party)

# main program
add_subdirectory(geoclaw-landspill)

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
