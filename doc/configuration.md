Configuration file: `setrun.py`
===============================

A simulation case folder must at least contains a `setrun.py`, which describes
the configurations of a simulation. `setrun.py` defines a function called
`setrun` that accepts no argument and returns an instance of
`gclandspill.data.ClawRunData`. For those familiar with Clawpack's ecosystem,
`gclandspill.data.ClawRunData` is a modified version of
`clawpack.clawutil.data.ClawRunData`. Our modified `ClawRunData` has some
default settings configured to meet *geoclaw-landspill*'s needs. Also, it has
additional settings for landspill simulations.

The basic working function `setrun` looks like:

```python
import gclandspill

def setrun():
    """Whatever docstring."""

    rundata = gclandspill.data.ClawRunData()

    <...setting up rundata...>

    return rundata
```

For those unfamiliar with Clawpack/GeoClaw, roughly speaking, there are four
parts in the `rundata` object that needs to be configured: core solver, AMR
(adaptive mesh refinement), GeoClaw-specific, and landspill-specific
configurations. The core solver, AMR, and GeoClaw configurations are described
in the official Clawpack documentation:

* Core solver: [Specifying classic run-time parameters in setrun.py](http://www.clawpack.org/setrun.html)
* AMR: [Specifying AMRClaw run-time parameters in setrun.py](http://www.clawpack.org/setrun_amrclaw.html)
* GeoClaw: [Specifying GeoClaw parameters in setrun.py](http://www.clawpack.org/setrun_geoclaw.html)

This document covers only required settings and also settings specific for
landspill. To better understand how a `setrun.py` looks like, please see the
`setrun.py` in examples under the `cases` folder.

--------------------------------------------
## I. Settings in core solver, AMR, and GeoClaw

Most settings in the core solver, AMR, and GeoClaw are tuned to work with
*geoclaw-landspill*, so end-users usually don't need to configure them. Here we
list some settings in these three parts that users must configure:

* `rundata.clawdata.lower[:]`: A list of two `float` representing *xmin* and
  *ymin*, respectively. In other words, lower boundaries in x and y.

* `rundata.clawdata.upper[:]`: A list of two `float` representing *xmax* and
  *ymax*, respectively. In other words, upper boundaries in x and y.

* `rundata.clawdata.num_cells[:]`: A list of two `int` representing the numbers
  of cells at the coarsest AMR level in the x and y direction.

* `rundata.topo_data.topofiles`: A list of two-element lists. For each of the
  two-element lists, the first element is an `int` indicating the topography
  file's format. The topography file is specified in the second element. If a
  relative path is used for the topography file, it must be relative to the
  case's folder. Usually, the format is `3`, which means it's an
  [Esri ASCII format raster](https://en.wikipedia.org/wiki/Esri_grid) file.
  See [Topography data](https://www.clawpack.org/topo.html#topo) for other
  acceptable raster formats.

* `rundata.clawdata.output_style`: An `int` specifying which output style to
  use for saving temporal results. Each style comes with different follow-up
  settings that need to be set:

  * `1`: Output a fixed number of frames at equally spaced times up to a final
    time.
    * `rundata.clawdata.num_output_times`: an `int`; total number of frames
    * `rundata.clawdata.tfinal`: a `float`; time of the last frame
    * `rundata.clawdata.output_t0`: a `bool`; whether to additionally output the
      initial state
  * `2`: Specify a list of times.
    * `rundata.clawdata.output_times`: a list of `float`; output at these times
  * `3`: Specify a number of time steps, and output every this number of time
    steps up to a given number of total steps.
    * `rundata.clawdata.output_step_interval`: an `int`; output every this
      number of steps
    * `rundata.clawdata.total_steps`: an `int`; output until the total number of
      steps reaches this value
    * `rundata.clawdata.output_t0`: a `bool` indicating whether to also output
      the initial state

--------------------------------------
## II. Settings specific for landspill

### i. Basic

* `rundata.landspill_data.ref_mu`: Reference dynamic viscosity at
  `ref_temperature`. The default is the viscosity of Maya crude oil. Unit: cP
  (i.e., mPa-s, or 1e-3 kg/s-m). (default: 332.0)

* `rundata.landspill_data.ref_temperature`: The temperature at which the
  `ref_mu` is measured. Unit: Celsius. (default: 15.0)

* `rundata.landspill_data.ambient_temperature`: The ambient temperature in
  simulation. The solver adjusts the viscosity and density based on this
  temperature. Unit: Celsius. (default: 25.0)

* `rundata.landspill_data.density`: The density measured at `ref_temperature`.
  The default is the density of Maya crude oil. Unit: kg/m^3. (default: 926.6)

### ii. Point sources

A point source is used to mimic a rupture point along a pipeline. It provides
fluid inflow into a computational domain. The inflow profile can be a
multi-stage constant rate.

* `rundata.landspill_data.point_source.n_point_sources`: An `int` indicating how
  many point sources. ***NOTE: currently only cases with one point source are
  well tested.*** (default: 0)

* `rundata.landspill_data.point_source.point_sources`: A list of four-element
  lists. Each four-element list describes a point source. (default: [])
  * The first element is a length-2 list of x and y coordinates of the point
    source.
  * The second element is the number of stages in the multi-stage inflow rate.
  * The third element is a list indicating the end time of each stage.
  * The fourth element is a list providing the volumetric rate of each stage.

  For example, if there is one single point source located at x=10, y=11. and if
  it has three stages of inflow profile (excluding when the rate is zero):
  * 1 m^3/sec when time &lt; 60 seconds
  * 0.5 m^3/sec when time &ge; 60 and &lt; 1800 seconds
  * 0.1 m^3/sec when time &ge; 1800 and &lt; 7200 seconds
  * 0 m^3/sec after 7200 seconds

  Then the corresponding configuration is

  ```python
  rundata.landspill_data.point_source.n_point_sources = 1
  rundata.landspill_data.point_source.point_sources = [
     [[10., 11.], 3, [60., 1800., 7200.], [1., 0.5, 0.1]]
  ]
  ```

### iii. Darcy-Weisbach friction model

In Darcy-Weisbach friction model, the friction coefficient can be calculated
by several different models. We implemented some of them. The type of models to
use is controlled by:

* `rundata.landspill_data.darcy_weisbach_friction.type`: (default: 0)

Each type has its own set of follow-up parameters.

* type is `0`: No Darcy-Weisbach friction.

* type is `1`: Use a constant friction coefficient everywhere. The only
follow-up parameter is
`rundata.landspill_data.darcy_weisbach_friction.coefficient` (default: 0.25).

* type is `2`: Block-wise constant coefficients. Users specify several blocks in
  a computational domain, and each block has a constant coefficient.  Available
  parameters are:

    * `rundata.landspill_data.darcy_weisbach_friction.n_blocks`: Number of blocks.
      (default: 0) 
    * `rundata.landspill_data.darcy_weisbach_friction.xlowers`: The lower boundaries
      in x direction of all blocks. (default: [])
    * `rundata.landspill_data.darcy_weisbach_friction.ylowers`: The lower boundaries
      in y direction of all blocks. (default: [])
    * `rundata.landspill_data.darcy_weisbach_friction.xuppers`: The upper boundaries
      in x direction of all blocks. (default: [])
    * `rundata.landspill_data.darcy_weisbach_friction.yuppers`: The upper boundaries
      in y direction of all blocks. (default: [])
    * `rundata.landspill_data.darcy_weisbach_friction.coefficients`: The
      coefficients in all blocks. (default: [])
    * `rundata.landspill_data.darcy_weisbach_friction.default_coefficient`: Regions
      that are not covered by blocks will have this value. (default: 0.25)

* type is `3`: Cell-wise coefficients. The coefficients are set through a raster
  file in Esri ASCII format.

    * `rundata.landspill_data.darcy_weisbach_friction.filename`: the name of the
      raster file for friction coefficients. (default: "")
    * `rundata.landspill_data.darcy_weisbach_friction.default_coefficient`: the
      coefficient for regions not covered by the raster file. (default: 0.25)

* type is `4`: Three-regime coefficient model. The coefficient is determined
in each cell based on whether the cell is laminar, transient, or turbulent
flow. See reference [1]. 

    * `rundata.landspill_data.darcy_weisbach_friction.filename`: the name of the
      raster file for surface roughness. (default: "")
    * `rundata.landspill_data.darcy_weisbach_friction.default_roughness`: the
      surface roughness for regions not covered by the raster file. (default:
      0.0)

* type is `5`: Churchill's coefficient model. See reference [2].

    * `rundata.landspill_data.darcy_weisbach_friction.filename`: the name of the
      raster file for surface roughness. (default: "")
    * `rundata.landspill_data.darcy_weisbach_friction.default_roughness`: the
      surface roughness for regions not covered by the raster file. (default:
      0.0)

* type is `6`: Two-regime coefficient. Similar to the three-regime model but
ignore transient flow regime.

    * `rundata.landspill_data.darcy_weisbach_friction.filename`: the name of the
      raster file for surface roughness. (default: "")
    * `rundata.landspill_data.darcy_weisbach_friction.default_roughness`: the
      surface roughness for regions not covered by the raster file. (default:
      0.0)

Usually, type `4` or `5` is used because they consider the surface roughness.

### iv. In-land waterbodies

*geoclaw-landspill* is able to records how much fluid volume flowing into
in-land waterbodies and at what locations. Users have to provide rasterized
hydrology data to enable this feature.

* `rundata.landspill_data.hydro_features.files`: A list of filenames. If
  relative paths are provided, they are assumed to be relative to the case
  folder. (default: [])

***Note: using multiple files has not been widely tested. It's recommended to
combine all data into one single raster file.***

Usually, hydrology data are vector data, such as those obtained from the USGS
database. Users can burn the vector data into raster files using
[`gdal_rasterize`](https://gdal.org/programs/gdal_rasterize.html).
Alternatively, users can specify a filename without actually providing the file.
*geoclaw-landspill* automatically downloads and rasterize hydrology data in this
case.

### v. Evaporation model

*geoclaw-landspill* implements Fingas' 1996 model, including the natural log
model and square root model. See reference [3].

* `rundata.landspill_data.evaporation.type`: The type of evaporation models to
  use. (default: 0)

  * `0`: No evaporation.
  * `1`: Fingas' natural log model
  * `2`: Fingas' square root model

* `rundata.landspill_data.evaporation.coefficients`: a list of `float` for model
  coefficients. Currently, we only have Fingas' models, so this variable should
  be a list of two `float`. See reference [3] for coefficients of a variety of
  oils.

-------------------------------------------------------------------
## III. Optional settings affecting stability, accuracy, and performance

The following optional settings are commonly used to control numerical
stability, accuracy, or/and performance:

* `rundata.clawdata.dt_initial`: This determines the size of the first time
  step. By default, it is automatically determined by the following
  formula:

  ```
  dt_initial = 0.3 * (cell size at the finest AMR grid) / (inflow rate)
  ```

  This makes the cell containing the first point source to have a depth of 0.3
  meters at the end of the first time step. Currently, the coefficient, 0.3, is
  hard-coded. This may give some trouble to simulations under small scales.
  For example, if the inflow rate of a point source is 1e-6 m^3 / sec, and if
  the finest cell size is 1e-4 m^2, this formula returns a `dt_initial` of 30
  seconds, which is apparently too big for a problem at this scale. In this
  case, users may want to manually set `dt_initial`.

* `rundata.clawdata.dt_max`: The maximum time step size allowed during a
  simulation. By default, the solver adjusts time step sizes based on flow
  conditions. Users sometimes may want to limit or increase how big a step size
  can be. (default: 5.0)

* `rundata.clawdata.cfl_desired`: The desired Courant–Friedrichs–Lewy (CFL)
  number. The solver adjusts time step sizes to make the resulting CFL numbers
  below this value. (default: 0.9)

* `rundata.clawdata.cfl_max`: The maximum allowed CFL number. If a CFL number is
  larger than this value, it triggers the solver to adjust time step sizes.
  (default: 0.95)

* `rundata.refinement_data.variable_dt_refinement_ratios`: Whether to use
  GeoClaw's adaptive time-step refinement mechanism. When AMR refines a coarse
  cell into several smaller cells, the smaller cells need smaller time step
  sizes. The time step sizes' refinement ratios can be fixed values or
  automatically determined by the GeoClaw solver. (default: True)

* `rundata.amrdata.amr_levels_max`: The number of AMR levels to be used. By
  default, *geoclaw-landspill* uses two levels: the coarse level for dry
  regions and the fine level for wet regions. (default: 2)

* `rundata.amrdata.refinement_ratios_x`: The refinement ratio between each two
  consecutive AMR levels in the x direction. (default: [4])

* `rundata.amrdata.refinement_ratios_y`: The refinement ratio between each two
  consecutive AMR levels in the y direction. (default: [4])

* `rundata.amrdata.refinement_ratios_t`: The refinement ratio between each two
  consecutive AMR levels in time step sizes. This only have effect when
  `rundata.refinement_data.variable_dt_refinement_ratios` is `False`. (default:
  [4])

* `rundata.geo_data.dry_tolerance`: The solver considers cells with depth below
  this value to be dry cells. (default: 1.e-4)

* `rundata.landspill_data.update_tol`: Affect how a coarse cell should
  distribute the depth to its children cells. This setting affects the
  conservation of mass. (default: the same as the `dry_tolerance`)

* `rundata.landspill_data.refine_tol`: By default, as long as there's fluid in a
  cell, it is refined by AMR (even if the depth is smaller than `dry_tolerance`.
  The behavior can be changed with this variable. (default: 0.0)

------------
## Reference

[1] B. C. Yen, “Open Channel Flow Resistance,” Journal of Hydraulic Engineering,
vol. 128, no. 1, pp. 20–39, Jan. 2002, doi: 10.1061/(ASCE)0733-9429(2002)128:1(20).

[2] S. W. Churchill, “Friction-factor equation spans all fluid flow regimes,”
Chem. Eng., vol. 84, no. 24, pp. 91–92, 1977

[3] M. F. Fingas, “Modeling evaporation using models that are not boundary-layer
regulated,” Journal of Hazardous Materials, vol. 107, no. 1–2, pp. 27–36, Feb.
2004, doi: 10.1016/j.jhazmat.2003.11.007.
