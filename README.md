geoclaw-landspill
=================

***Note: if looking for content of `geoclaw-landspill-cases`, please checkout tag
`v0.1`. This repository has been converted to a fully working solver package.***

*geoclaw-landspill* is a package for running oil overland flow simulations for
the applications in pipeline risk management. It includes a numerical solver and
some pre-/post-processing utilities.

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
* removing unnecessary code to improve AMR performance
* downloading topography and hydrology data automatically (US only)
* generating CF-1.7 compliant NetCDF files

## Content
1. [Installation](#1-installation)
2. [Usage](#2-usage)
3. [Docker usage](#3-docker-usage)
4. [Singularity usage](#4-singularity-usage)
5. [Contact](#5-contact)

------------------------------------------------------------------------
## 1. Installation

The recommended way to use *geoclaw-landspill* is through
[Docker](#4-docker-usage) images or [Singularity](#5-singularity-usage) 
images. But in case both Docker and Singularity are not available, follow the 
instruction in this section to build and install *geoclaw-landspill*.

### 1-1. Prerequisites

The operating system used for development and runtime is Linux, though all
dependencies are handled by [conda](https://www.anaconda.com/). It may also work
under MacOS and Windows. But we have no interest in testing and maintaining the
compatibility to non-Linux OS.

See [requirements.txt](requirements.txt) for conda packages required to build
and install *geocland-landspill*.

To create a conda environment that can be used for *geoclaw-landspill*:

```
$ conda create -n landspill -c defaults -c conda-forge --file requirements
```

Then go into the conda environment through

```
$ conda activate landspill
```

Now we are ready to build and install *geoclaw-landspill*.

### 1-2. Installation

Currently, *geoclaw-landspill* is not yet released on PyPI or conda-forge, users
have to install it manually.

First, pull the repository:

```
$ git clone --recurse-submodules https://github.com/barbagroup/geoclaw-landspill.git
```

Then

```
$ cd geoclaw-landspill
$ python setup.py install -G "Unix Makefiles" -j <number of CPUs to use>
```
Or, if installing *geoclaw-landspill* to users' local Python path is preferred:

```
$ python setup.py install --user -G "Unix Makefiles" -j <number of CPUs to use>
```

`<number of CPUs to use>` refers to the number of processes for parallel
compilization of the Fortran code. If installing to local Python path, by default, it is
installed to `${HOME}/.local`. In this case, it is necessary to add
`${HOME}/.local/bin` to the environment variable `PATH`.

To uninstall *geoclaw-landspill*, do

```
$ pip uninstall geoclaw-landspill
```

------------------------------------------------------------------------
## 2. Usage

To see the help:

```
$ geoclaw-landspill --help
```

### 2-1. Running a case

To run a case, execute

```
$ geoclaw-landspill run <path to a case folder>
```

Example cases can be found in directory `cases`. Currently, there are ten cases.
A case folder must have at least a `setrun.py` that configures the simulation.
This follows the convention of GeoClaw and Clawpack-related projects.

The command `run` automatically downloads (only in the US) topography and
hydrology data from the USGS database if specified data files can not be found.
For example, after running the `utah-flat-maya` case under `cases`, users should
find topography and hydrology files, `utah-flat.asc` and `utah-flat-hydro.asc`,
under the folder `common-files`.

The solver runs with OpenMP-parallelization. By default, the number of threads
involved in a run is system-dependent. Users can explicitly control how many
threads to use for a simulation by environment variable `OMP_NUM_THREADS`. See
OpenMP's documentation. For example, to run the `utah-flat-maya` with 4 threads:

```
$ OMP_NUM_THREADS=4 geoclaw-landspill run <path to utah-flat-maya>
```

Raw simulation results are under folder `<case folder>/_output`. If running a
case multiple times, old `_output` folders are renamed automatically to
`_output.<timestamp>`, so old results are not lost.

Use following commands to generate GIS-software-readable raster files or to
produce quick visualizations.

### 2-2. NetCDF raster files with CF convention

```
$ geoclaw-landspill createnc <path to a case>
```

This command converts raw simulation results to a CF-compliant temporal NetCDF
raster file. At least QGIS and ArcGIS are able to read this file format. The
resulting NetCDF file will be at `<case folder>/_output/<case name>-level<XX>.nc`.
Only the results at one AMR level are used. The default level is the finest AMR
level. Use flag `--level=<number>` to create raster files for other AMR levels.

To see more parameters to control the conversion, use

```
$ geoclaw-landspill createnc --help
```


### 2-3. Visualization of depth

```
$ geoclaw-landspill plotdepth <path to a case>
```

This create flow depth contours for all time frames. Figures are saved to
`<case folder>/_plots/depth/level<xx>`. By default, only the results on the
finest AMR grid level are plotted.

See `--help` for more arguments.

### 2-4. Visualization of elevation data used by AMR grids

```
$ geoclaw-landspill plottopo <path to a case>
```

`plottopo` plots the runtime topography on AMR grids at each time frame of a 
simulation. This is different from plotting the topography using topography
file. Runtime topography means the actual elevation values defined on AMR grid
cells during a simulation.

The output figures are saved to `<case folder>/_plots/topo`.

See `--help` for more arguments.

### 2-5. Total volume on the ground

```
$ geoclaw-landspill volumes <path to a case>
```

This command calculates total fluid volumes at each AMR grid level at each time
frame. The results are saved to a CSV file `<case folder>/_output/volumes.csv`.
The main use case of this volume data is to check the mass conservation.

------------------------------------------------------------------------
## 3. Docker usage

We provide two Docker images on 
[DockerHub](https://hub.docker.com/r/barbagroup/landspill).
Currently, end users have to use the image with tag `dev` because we haven't had
any format release.

Pull the Docker image through:

```
$ docker pull barbagroup/landspill:dev
```

To get into the shell of a Docker container:
```
$ docker run -it --name landspill barbagroup/landspill:dev
```
After getting into the shell, the example cases are under `landspill-examples`.
All *geoclaw-landspill* commands are available.

------------------------------------------------------------------------
## 4. Singularity usage

For many HPC clusters or supercomputers, Docker is not available due to
security concerns, and [Singularity](https://www.sylabs.io/singularity/) is the 
only container technology available. 

To pull the `dev` image and save to a local image file, do
```
$ singularity pull lanspill.sif library://barbagroup/geoclaw-landspill:dev
```

The minimum Singularity version tested is v3.4.

```
$ singularity run --app run landspill.sif utah_gasoline
```

The `--app run` means Singularity will apply the `run.py` script in the 
`landspill.sif` image to the case folder `utah_gasoline` on the host.

All utilities in the repository can be called by the same method. To see all
available commands for `--app <command>`, run
```
$ singularity run-help landspill.sif
```

------------------------------------------------------------------------
## 5. Contact

Pi-Yueh Chuang: pychuang@gwu.edu
