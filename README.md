geoclaw-landspill
=================

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/barbagroup/geoclaw-landspill/raw/master/LICENSE)
[![Travis CI](https://img.shields.io/travis/com/barbagroup/geoclaw-landspill/master?label=Travis%20CI)](https://travis-ci.com/barbagroup/geoclaw-landspill)
[![GitHub Action CI](https://img.shields.io/github/workflow/status/barbagroup/geoclaw-landspill/CI/master?label=GitHub%20Action%20CI)](https://github.com/barbagroup/geoclaw-landspill/actions?query=workflow%3ACI)
[![status](https://joss.theoj.org/papers/fb7b012799a70c9b4c55eb4bb0f36f97/status.svg)](https://joss.theoj.org/papers/fb7b012799a70c9b4c55eb4bb0f36f97)
[![Conda](https://anaconda.org/barbagroup/geoclaw-landspill/badges/installer/conda.svg)](https://anaconda.org/barbagroup/geoclaw-landspill)

***Note: if looking for content of `geoclaw-landspill-cases`, please checkout tag
`v0.1`. This repository has been converted to a fully working solver package.***

*geoclaw-landspill* is a package for running oil overland flow simulations for
applications in pipeline risk management. It includes a numerical solver and
some pre-/post-processing utilities.

<center><img src="./doc/sample.gif" /></center>

The numerical solver is a modified version of
[GeoClaw](http://www.clawpack.org/geoclaw.html).
GeoClaw solves full shallow-water equations. We added several new features and
utilities to it and make it usable to simulate the overland flow from pipeline
ruptures. These features include:

* adding point sources to mimic the rupture points
* adding evaporation models
* adding Darcy-Weisbach bottom friction models with land roughness
* adding temperature-dependent viscosity
* recording detail locations and time of oil flowing into in-land waterbodies
* downloading topography and hydrology data automatically (the US only)
* generating CF-1.7 compliant NetCDF files

## Documentation
1. [Dependencies, installation, and tests](doc/deps_install_tests.md)
2. [Usage](doc/usage.md)
3. [Configuration file: `setrun.py`](doc/configuration.md)
4. [Example cases](cases/README.md)
5. [Containers: Docker and Singularity](doc/container.md)

------------------------------------------------------------------------
## Quick start

We only maintain compatibility with Linux. Though using `pip` or building from
source may still work in Mac OS or Windows (e.g., through WSL), we are not able
to help with the installation issues on these two systems.

Beyond this quick start, to see more details, please refer to the
[documentation](#documentation) section.

### 1. Installation

The fast way to install *geoclaw-landspill* is through
[Anaconda](https://www.anaconda.com/)'s `conda` command. The following command
creates a conda environment (called `landspill`) and installs the package and
dependencies:

```
$ conda create \
    -n landspill -c barbagroup -c conda-forge \
    python=3.8 geoclaw-landspill
```

Then use `conda activate landspill` or
`source <conda installation prefix>/bin/activate landspill` to activate the
environment. Type `geoclaw-landspill --help` in the terminal to see if
*geoclaw-landspill* is correctly installed.

### 2. Running an example case

To run an example case under the folder `cases`, users have to clone this
repository. We currently don't maintain another repository for cases. After
cloning this repository, run
```
$ geoclaw-landspill run <path to an example case folder>
```
For example, to run `utal-flat-maya`:
```
$ geoclaw-landspill run ./cases/utah-flat-maya
```
Users can use environment variable `OMP_NUM_THREADS` to control how many CPU
threads the simulation should use for OpenMP parallelization.

### 3. Creating a CF-compliant NetCDF raster file

After a simulation is done, users can convert flow depth in raw simulation data
into a CF-compliant NetCDF raster file. For example,
```
$ geoclaw-landspill createnc ./case/utah-flat-maya
```
Replace `./cases/utah-flat-maya` with the path to another desired case.

QGIS and ArcGIS should be able to read the resulting NetCDF raster file.

------------------------------------------------------------------------
## Third-party codes and licenses

* amrclaw: https://github.com/clawpack/amrclaw
  ([BSD 3-Clause License](https://github.com/clawpack/amrclaw/blob/ee85c1fe178ec319a8403503e779d3f8faf22840/LICENSE))
* geoclaw: https://github.com/clawpack/geoclaw
  ([BSD 3-Clause License](https://github.com/clawpack/geoclaw/blob/3593cb1b418fd52739c186a8845a288037c8f575/LICENSE))
* pyclaw: https://github.com/clawpack/pyclaw
  ([BSD 3-Clause License](https://github.com/clawpack/pyclaw/blob/a85a01a5f20be1a18dde70b7bb37dc1cdcbd0b26/LICENSE))
* clawutil: https://github.com/clawpack/clawutil
  ([BSD 3-Clause License](https://github.com/clawpack/clawutil/blob/116ffb792e889fbf0854d7ac599657039d7b1f3e/LICENSE))
* riemann: https://github.com/clawpack/riemann
  ([BSD 3-Clause License](https://github.com/clawpack/riemann/blob/597824c051d56fa0c8818e00d740867283329b24/LICENSE))

------------------------------------------------------------------------
## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

------------------------------------------------------------------------
## Contact

Pi-Yueh Chuang: pychuang@gwu.edu
