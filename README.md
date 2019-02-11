geoclaw-landspill-cases
==========================

This repo contains a collection of land-spill simulation cases and utilities.

------------------------------------------------------------------------
## I. Setting up


#### Option A: Using Docker image

If choosing to use Docker image, the docker image is located at DockerHub
`barbagroup/landspill:applications`. Everything needed is in the image.

1. Pull the image through:  
   `$ docker pull barbagroup/landspill:applications`
2. Create a container with the image and log into a bash shell:  
   `$ docker run -it --name landspill barbagroup/landspill:applications /bin/bash`
3. The repo is at `~/geoclaw-landspill-cases`. There is already a compiled
   solver in `bin` folder and required topography files in `common_files`.

#### Option B: Manually setting up the environment

1. Download [Clawpack v5.5.0](https://github.com/clawpack/clawpack/releases/tag/v5.5.0)
   and set it up according to Clawpack instruction.
2. Grab the landspill-version GeoClaw and replace the original `geoclaw`
   inside Clawpack. There has yet no release of the landspill-version
   GeoClaw. The latest development version can be found
   [here](https://github.com/piyueh/geoclaw).
3. Set the following environment variables:
  1. `CLAW`: the path to Clawpack
  2. `FC`: Fortran compiler. Only gfortran 8 and Intel Fortran 19.0.0.117
     have been tested. *Note: the default compilation flags are for gfortran,
     so `FFLAGS` will have to be modified if using Intel Fortran or other
     Fortran compilers.*
  3. `PYTHONPATH`: prepend `${CLAW}` to original `${PYTHONPATH}`.
4. Download/pull this repo.
5. Install the prerequisites (see the next subsection)
6. Go to the folder of this repo and set it up through `$ python setup.py`.
   This will download required data and compile a binary executable for
   the solver.

#### Prerequisites

1. [rasterio](https://github.com/mapbox/rasterio) (optional): used for automatic
   downloading of topography files.
2. [netCDF4](http://unidata.github.io/netcdf4-python/) (optional): used in the
   script `createnc.py`.
3. [numpy](http://www.numpy.org/) (required)
4. [scipy](https://www.scipy.org/) (optional): used in the script `createnc.py`.
5. [matplotlit](https://matplotlib.org/) (optiona): used in `plotdepths.py` and
   `plottopos.py`.

For users using [Anaconda](https://www.anaconda.com/), the following commands
are for installing the prerequisites in shell (Linux) or CMD (Windows):

```
$ conda install numpy
$ conda install scipy
$ conda install matplotlib
$ conda install rasterio
$ conda install netcdf4
```

------------------------------------------------------------------------
## II. Running a case

Use the python script `run.py` to run a case in this repo. Usage:
```
$ python run.py case
```
Currently, there are nine cases:
1. utah_gasoline
2. utah_gasoline_no_evaporation
3. utah_hill_maya
4. utah_hydrofeatures_gasoline
5. utah_hydrofeatures_gasoline_no_evaporation
6. utah_hydrofeatures_maya
7. utah_hydrofeatures_maya_no_evaporation
8. utah_maya
9. utah_maya_no_evaporation

------------------------------------------------------------------------
## III. Visualizing depth results with `matplotlib`

Use the python script `plotdepths.py` to visualize depth results at each
output time. Usage:
```
$ python plotdepths.py [-h] [--level LEVEL] [--continue] [--border] case
```
Arguments and Options:
```
positional arguments:
  case           the name of the case

optional arguments:
  -h, --help     show this help message and exit
  --level LEVEL  plot depth result at a specific AMR level (default: finest level)
  --continue     continue creating figures in the existing _plot folder
  --border       also plot the borders of grid patches
```
The plots will be in under `[case]/_plots/depth/level[xx]`. For example,
if plotting the results from ***utah_hill_maya*** and without specifying a
specific AMR level, then the plots will be in `utah_hill_maya/_plots/depth/level05`.

------------------------------------------------------------------------
## IV. Creating a NetCDF file with CF convention

The Python script `createnc.py` can be used to create a NetCDF file with 
temporal depth data for a case. Usage:
```
$ python createnc.py [-h] [--level LEVEL] [--frame-bg FRAME_BG] [--frame-ed FRAME_ED] case
```
Arguments and Options:
```
positional arguments:
  case                 the name of the case

optional arguments:
  -h, --help           show this help message and exit
  --level LEVEL        use data from a specific AMR level (default: finest level)
  --frame-bg FRAME_BG  customized start farme no. (default: 0)
  --frame-ed FRAME_ED  customized end farme no. (default: get from setrun.py)
```

The resulting NetCDF file will be `[case]/[case]_level[XX].nc`. For example,
if creating a NetCDF file from ***utah_hill_maya*** and without sepcifying
a specific AMR level, then the NetCDF file will be `utah_hill_maya/utah_hill_maya_level05.nc`.
