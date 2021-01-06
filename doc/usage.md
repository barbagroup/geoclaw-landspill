# Usage

`geoclaw-landspill` is the top-level executable. It has several subcommands. To
see the subcommands:
```
$ geoclaw-landspill --help
```

-----------------
## Run a case

To run a case, execute

```
$ geoclaw-landspill run <path to a case folder>
```

Interested users can find example cases in directory `cases`.

A case folder must have at least a `setrun.py` that configures the simulation.
The usage of `setrun.py` follows the convention of GeoClaw and Clawpack-related
projects.

The command `run` automatically downloads topography (in the US) and
hydrology data from the USGS database if it can not find specified files.
For example, running the `utah-flat-maya` case under `cases` downloads
topography and hydrology files, `utah-flat.asc` and `utah-flat-hydro.asc`,
into the folder `common-files`.

The solver runs with OpenMP-parallelization. By default, the number of threads
involved in a run is system-dependent. Users can explicitly control how many
threads to use for a simulation by environment variable `OMP_NUM_THREADS`. See
OpenMP's documentation. For example, to run `utah-flat-maya` with 4 threads:

```
$ OMP_NUM_THREADS=4 geoclaw-landspill run <path to utah-flat-maya>
```

Raw simulation results are under folder `<case folder>/_output`. If running a
case multiple times, old `_output` folders are renamed automatically to
`_output.<timestamp>` to avoid losing old results.

Use the following commands to generate GIS-software-readable raster files or to
produce quick visualizations.

------------------------------------------------
## Create NetCDF raster files with CF convention

```
$ geoclaw-landspill createnc <path to a case>
```

This subcommand converts raw simulation results to a CF-compliant temporal NetCDF
raster file. At least QGIS and ArcGIS are able to read this file format. The
resulting NetCDF file will be at `<case folder>/_output/<case name>-level<XX>.nc`.
Only the results at one AMR level are used. The default level is the finest AMR
level. Use flag `--level=<number>` to create raster files for other AMR levels.

To see more parameters to control the conversion, use
```
$ geoclaw-landspill createnc --help
```

--------------------------------------
## Create quick Visualization of depth

```
$ geoclaw-landspill plotdepth <path to a case>
```

This subcommand creates flow depth contours for all time frames. Figures are
saved to `<case folder>/_plots/depth/level<xx>`. By default, only the results on
the finest AMR grid level are plotted.

There are several parameters to fine-tune the output images, including plotting
the depth data on a satellite image (such as the one shown in README). See
`--help` for more arguments.

-----------------------------------------------------
## Visualize elevation data used by runtime AMR grids

```
$ geoclaw-landspill plottopo <path to a case>
```

`plottopo` plots the runtime topography on AMR grids at each time frame of a 
simulation. This is different from plotting the topography using a topography
file. Runtime topography means the actual elevation values defined on AMR grid
cells during a simulation.

The output figures are saved to `<case folder>/_plots/topo`.

See `--help` for more arguments.

## Calculate total volume above ground

```
$ geoclaw-landspill volumes <path to a case>
```

This subcommand calculates total fluid volumes at each AMR grid level at each
time frame. The results are saved to a CSV file `<case folder>/_output/volumes.csv`.
The main use case of this volume data is to check the mass conservation.
