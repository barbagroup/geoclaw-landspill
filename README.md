geoclaw-landspill-cases
==========================

This repository contains a collection of land-spill simulation cases and 
utilities. It helps the reproducibility of our research, and in the meanwhile,
provides utility tools to ease the workflow of overland flow simulation with
GeoClaw. In addition, the Docker image provided by this repository can help
Windows user run simulations with GeoClaw, which does not officially support
Windows. And the Singularity image makes running GeoClaw on HPC clusters easier.
Most supercomputers and HPC clusters do not support Docker, and Singularity is
the only option.

The solver used for overland flow simulations is a modified version of 
[GeoClaw](http://www.clawpack.org/geoclaw.html). Currently, this modified 
version has not yet been merged back into the upstream. And the source code of 
the modified version can be found [here](https://github.com/barbagroup/geoclaw).

## Content
1. [Setting up](#1-setting-up)
    1. [Prerequisites](#1-1-prerequisites)
    2. [Steps](#1-2-steps)
2. [Running a case](#2-running-a-case)
3. [Other utilities](#3-other-utilities)
4. [Docker usage](#4-docker-usage)
5. [Singularity usage](#5-singularity-usage)
6. [Contact](#6-contact)

------------------------------------------------------------------------
## 1. Setting up

The recommended way to run cases or use utilities in this repository is 
through [Docker](#4-docker-usage) images or [Singularity](#5-singularity-usage) 
images. But in case both Docker and Singularity are not available, follow the 
instruction in this section to set up the environment in Linux.

### 1-1. Prerequisites

1. Python >= 3.6
2. gfortran >= 8
3. [numpy](http://www.numpy.org/) >= 1.15.4
4. [requests](http://docs.python-requests.org/en/master/) >= 2.21.0
5. [rasterio](https://github.com/mapbox/rasterio) >= 1.0.18
6. [scipy](https://www.scipy.org/) >= 1.2.0: (optional) required by `createnc.py`.
7. [matplotlib](https://matplotlib.org/) >= 3.0.2: (optiona) required by `plotdepths.py` and `plottopos.py`.
8. [netCDF4](http://unidata.github.io/netcdf4-python/) >= 1.4.2: (optional) required by `createnc.py`.

The easiest way to get `gfortran` >= 8 is through the package manager in Linux.
For Arch Linux, do

```
# pacman -S gcc-fortran
```

For Ubuntu Bionic, use:

```
# apt-get install gfortran-8
```

Regarding the Python dependencies, for users using 
[Anaconda](https://www.anaconda.com/), use the following commands to install 
the Python prerequisites:

```
$ conda install numpy=1.15.4
$ conda install requests=2.21.0
$ conda install rasterio=1.0.18
$ conda install scipy=1.2.0
$ conda install matplotlib=3.0.2
$ conda install netcdf4=1.4.2
```

Or with `pip` (for Python 3):

```
$ pip install -I \
    numpy==1.15.4 \
    requests==2.21.0 \
    rasterio==1.0.18 \
    scipy==1.2.0 \
    matplotlib==3.0.2 \
    netcdf4==1.4.2
```

### 1-2. Steps

1. Clone this repositroy or download the tarbal of the latest release.
2. Make sure all prerequisites are available.
3. Go to the repository folder.
3. Run `$ python setup.py`.

------------------------------------------------------------------------
## 2. Running a case

Currently, there are nine cases, all under the subfolder `cases`:

1. utah_gasoline
2. utah_gasoline_no_evaporation
3. utah_hill_maya
4. utah_hydrofeatures_gasoline
5. utah_hydrofeatures_gasoline_no_evaporation
6. utah_hydrofeatures_maya
7. utah_hydrofeatures_maya_no_evaporation
8. utah_maya
9. utah_maya_no_evaporation

Users can use the Python script `run.py` under the folder `utilities` to run 
these cases. The usage of this script is

```
$ python run.py <path to the case>
```

For example, if a user is currently under the repository folder 
`geoclaw-landspill-cases`, and he/she wants to run the example case `utah_maya`
in the folder `cases`, then do

```
$ python utilities/run.py cases/utah_maya
```

The script `run.py` is executable, so the user can execute it directly:

```
$ utilities/run.py cases/utah_maya
```

The script `run.py` can automatically download topography data and hydrologic
data from the USGS database. So after running a case with `run.py`, users should find
the topography and hydrologic data files at the path specified in the case setup.
For example, in the `utah_maya` case, the `utah_maya/setrun.py` specifies that
the topography file is `cases/common-files/salt_lake_1.asc`. But `run.py` can
not find `cases/common-files/salt_lake_1.asc`, so it will try to download the 
topography data from the USGS database according to the extent set in the 
`utah_maya/setrun.py`, and it will save the data to `cases/common-files/salt_lake_1.asc`.
The hydrologic data follows the same rule. If in the future a user creates 
his/her own simulation case without providing topography/hydrology data, 
the `run.py` will do the same. Currently, the `run.py` can only automatically 
download data for the regions inside the US.

To control how many CPU cores are used for a simulation, set the environment
variable `OMP_NUM_THREADS`. For example, to use only 4 cores for the `utah_maya`
case, do
```
$ export OMP_NUM_THREADS=4
$ python utilities/run.py cases/utah_maya
```

Or simply
```
$ OMP_NUM_THREADS=4 python utilities/run.py cases/utah_maya
```

After the simulation, the result files will be in `<case folder>/_output`.

------------------------------------------------------------------------
## 3. Other utilities

The repository provides some other utilities for post-processing.

### 3-1. NetCDF raster files with CF convention

The Python script `createnc.py` can be used to create a NetCDF file with 
temporal depth data for a case. Usage:
```
$ python createnc.py [-h] [--level LEVEL] [--frame-bg FRAME_BG]
                     [--frame-ed FRAME_ED]
                     case
```

Arguments and Options:
```
positional arguments:
  case                 the name of the case

optional arguments:
  -h, --help           show this help message and exit
  --level LEVEL        use data from a specific AMR level (default: finest level)
  --frame-bg FRAME_BG  customized start frame no. (default: 0)
  --frame-ed FRAME_ED  customized end frame no. (default: get from setrun.py)
```

The resulting NetCDF file will be `<case folder>/<case name>_level<XX>.nc`.
For example, if creating a NetCDF file from `utah_hill_maya` and without
sepcifying a specific AMR level, then the NetCDF file will be
`utah_hill_maya/utah_hill_maya_level02.nc`.

### 3-2. Visualization of depth

Use the python script `plotdepths.py` to visualize depth results at each
output time. Usage:
```
$ python plotdepths.py [-h] [--level LEVEL] [--dry-tol DRY_TOL] [--cmax CMAX]
                       [--cmin CMIN] [--frame-bg FRAME_BG] [--frame-ed FRAME_ED]
                       [--continue] [--border] [--nprocs NPROCS]
                       case
```


Arguments and Options:
```
positional arguments:
  case                 the name of the case

optional arguments:
  -h, --help           show this help message and exit
  --level LEVEL        plot depth result at a specific AMR level (default: finest level)
  --dry-tol DRY_TOL    tolerance for dry state (default: obtained from setrun.py)
  --cmax CMAX          maximum value in the depth colorbar (default: obtained from solution)
  --cmin CMIN          minimum value in the depth colorbar (default: obtained from solution)
  --frame-bg FRAME_BG  customized start frame no. (default: 0)
  --frame-ed FRAME_ED  customized end frame no. (default: obtained from setrun.py)
  --continue           continue creating figures in existing _plot folder
  --border             also plot the borders of grid patches
  --nprocs NPROCS      number of CPU threads used for plotting (default: 1)
```

The plots will be in under `<case folder>/_plots/depth/level<xx>`. For example,
if plotting the results of `utah_hill_maya` and without specifying a
specific AMR level, then the plots will be in `utah_hill_maya/_plots/depth/level02`.

### 3-3. Visualization of elevation data used by AMR grids

To see how elevation data is evaluated on AMR grids, use the script `plottopos.py`:

```
$ python plottopos.py [-h] [--level LEVEL] [--cmax CMAX] [--cmin CMIN]
                      [--frame-bg FRAME_BG] [--frame-ed FRAME_ED] [--continue]
                      [--border]
                      case
```

And the arguments:

```
positional arguments:
  case                 the name of the case

optional arguments:
  -h, --help           show this help message and exit
  --level LEVEL        plot depth result at a specific AMR level (default: finest level)
  --cmax CMAX          maximum value in the depth colorbar (default: obtained from solution)
  --cmin CMIN          minimum value in the depth colorbar (default: obtained from solution)
  --frame-bg FRAME_BG  customized start farme no. (default: 0)
  --frame-ed FRAME_ED  customized end farme no. (default: obtained from setrun.py)
  --continue           continue creating figures in existing _plot folder
  --border             also plot the borders of grid patches
```

The topography plots generated from this script are different from the topography
file (the DEM file). The elevation values in these plots are the values in the 
AMR solution files. The purpose of these plots is to examine the correctness
of the elevation data used in simulations.

### 3-4. Total volume on the ground

The script `calculatevolume.py` can be used to calculate the total fluid volume
on the ground at different time frame and different AMR level. It creates a CSV
file called `total_volume.csv` under the case folder.

```
$ python calculatevolume.py [-h] [--frame-bg FRAME_BG] [--frame-ed FRAME_ED] case
```

Arguments:

```
positional arguments:
  case                 the name of the case

optional arguments:
  -h, --help           show this help message and exit
  --frame-bg FRAME_BG  customized start frame no. (default: 0)
  --frame-ed FRAME_ED  customized end frame no. (default: get from setrun.py)
```

------------------------------------------------------------------------
## 4. Docker usage

We provide two Docker images on 
[DockerHub](https://hub.docker.com/r/barbagroup/landspill).
The first image is the one based on Ubuntu Bionic, which should work on the majority
of the systems. The second one is based on Ubuntu Trusty, which is for the systems
with old Linux kernels (like kernel 2.6 on old clusters at many universities).

Pull the Docker image through:
```
$ docker pull barbagroup/landspill:bionic
```
or
```
$ docker pull barbagroup/landspill:trusty
```

To get into the shell of a Docker container:
```
$ docker run -it --name landspill barbagroup/landspill:bionic
```
After getting into the shell, the example cases are under `landspill-examples`.
All executable utility Python scripts are in the `PATH` environment variable.

For example, to run the simulation of the case `utah_maya` with 4 CPU cores, and 
suppose the current directory is the home directory, do
```
$ OMP_NUM_THREADS=4 run.py landspill-examples/utah_maya 
```

Or to generate depth plots of `utah_maya` after simulation, for example, do:
```
$ plotdepths.py landspill-examples/utah_maya
```

To exit the shell of the Docker container, simply execute `exit` in the shell.

------------------------------------------------------------------------
## 5. Singularity usage

For many HPC clusters or supercomputers, Docker is not available due to
security concerns, and [Singularity](https://www.sylabs.io/singularity/) is the 
only container technology available. Similar to the Docker images, we provide 
two Singularity images on [SingularityHub](https://singularity-hub.org/collections/2381). 
The first one is based on Ubuntu Bionic, and the second is based on Ubuntu Trusty.
The Trusty version is specifically for the machines with old Linux kernels.

As an example usage, to pull the Bionic image and save to a local image file, do
```
$ singularity pull lanspill.sif shub://barbagroup/geoclaw-landspill-cases:bionic
```

Note, the Singularity version used is v3.1. If using older Singularity,
like those with v2.x, the Singularity commands may be different. For example, 
with Singularity v2.5.2, the command to do the same thing is
```
$ singularity pull -n landspill.sif shib://barbagroup/geoclaw-landspill-cases:bionic
```
Here we assume the Singularity version is at least v3.1. For those who use older
Singularity, please consult the Singularity manual for the usage.

An advantage of Singularity is that it will map and bind the current directory
on the host to a Singularity container automatically. That means, if a user has
a simulation case on the host, with a Singularity image, he/she can launch the
simulation directly from the host machine without logging into the container.

For example, suppose we are now on the host machine and has a simulation case
`utah_gasoline` under the current directory. To run the simulation with the
Singularity image we just downloaded, do
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
## 6. Contact

Pi-Yueh Chuang: pychuang@gwu.edu
