"""Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""
# pylint: disable=no-member, too-many-statements
import functools
from gclandspill.clawutil import data
from gclandspill.data import LandSpillData


def setrun(claw_pkg: str = 'geoclaw'):
    """Define the parameters used for running Clawpack.

    Arguments
    ---------
    claw_pkg : str
        Expected to be "geoclaw" for this setrun.

    Returns
    -------
    rundata : clawutil.ClawRunData
    """

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    num_dim = 2
    rundata = data.ClawRunData(claw_pkg, num_dim)

    # GeoClaw specific parameters:
    rundata = setgeo(rundata)

    # AmrClaw specific parameters:
    rundata = setamr(rundata)

    # an alias to object holding standard Clawpack parameters
    clawdata = rundata.clawdata

    # number of space dimensions:
    clawdata.num_dim = num_dim

    # lower and upper edge of computational domain:
    clawdata.lower[0] = -12460209.5-400.
    clawdata.upper[0] = -12460209.5+400.
    clawdata.lower[1] = 4985137.4-400
    clawdata.upper[1] = 4985137.4+400

    # number of grid cells: coarsest grid
    clawdata.num_cells[0] = 200
    clawdata.num_cells[1] = 200

    # number of equations in the system: continuity eq. and x, y momemtums
    clawdata.num_eqn = 3

    # number of auxiliary variables: elevation and hydrological data
    clawdata.num_aux = 2

    # index of aux array corresponding to capacity function, if there is one:
    clawdata.capa_index = 0

    # initial time:
    clawdata.t0 = 0.0

    # restart from checkpoint file of a previous run?
    clawdata.restart = False               # True to restart from prior results
    clawdata.restart_file = 'fort.chk00006'  # File to use for restart data

    # temporal data output style
    clawdata.output_style = 1

    if clawdata.output_style == 1:  # equally spaced times up to tfinal
        clawdata.num_output_times = 240
        clawdata.tfinal = 28800
        clawdata.output_t0 = True  # output at initial (or restart) time?
    elif clawdata.output_style == 2:  # a list of output times
        clawdata.output_times = [0., 1800.]
    elif clawdata.output_style == 3:  # every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 80
        clawdata.total_steps = 4000
        clawdata.output_t0 = True

    # output data format
    clawdata.output_format = 'binary'

    # which veriable to output
    clawdata.output_q_components = 'all'  # could be list such as [True,True]

    # which aux data to output
    clawdata.output_aux_components = 'all'  # could be list

    # whether to output aux data only at t0
    clawdata.output_aux_onlyonce = False

    # print information up to this AMR level
    clawdata.verbosity = 3

    # use veriable time step size based on CFL
    clawdata.dt_variable = 1

    # data required to calculate a proper initial time step size
    cell_area = \
        (clawdata.upper[0] - clawdata.lower[0]) * (clawdata.upper[1] - clawdata.lower[1]) / \
        (clawdata.num_cells[0] * clawdata.num_cells[1])
    cell_area /= functools.reduce(
        lambda x, y: x*y, rundata.amrdata.refinement_ratios_x[:rundata.amrdata.amr_levels_max], 1)
    cell_area /= functools.reduce(
        lambda x, y: x*y, rundata.amrdata.refinement_ratios_y[:rundata.amrdata.amr_levels_max], 1)
    vrate = rundata.landspill_data.point_sources.point_sources[0][-1][0]

    # initial time step for variable dt.
    clawdata.dt_initial = 0.3 * cell_area / vrate

    # max time step allowed if variable dt
    clawdata.dt_max = 4.0

    # desired CFL if variable dt, and max CFL allowed without retaking a step with a smaller dt
    clawdata.cfl_desired = 0.9
    clawdata.cfl_max = 0.95

    # maximum number of time steps allowed between two output times:
    clawdata.steps_max = 100000

    # order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 2

    # use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'

    # 2 or 'all' => corner transport of 2nd order corrections too
    clawdata.transverse_waves = 2

    # number of waves in the Riemann solution:
    clawdata.num_waves = 3

    # list of limiters to use for each wave family:
    clawdata.limiter = ['mc', 'mc', 'mc']

    # use f-wave version of algorithms
    clawdata.use_fwaves = True

    # src_split == 1 or 'godunov' ==> Godunov (1st order) splitting used,
    clawdata.source_split = 'godunov'

    # number of ghost cells (usually 2)
    clawdata.num_ghost = 2

    # BC: 1 => extrapolation (non-reflecting outflow)
    clawdata.bc_lower[0] = 1
    clawdata.bc_upper[0] = 1
    clawdata.bc_lower[1] = 1
    clawdata.bc_upper[1] = 1

    # checkout mechanism selection
    clawdata.checkpt_style = 0

    if clawdata.checkpt_style == 0:  # do not checkpoint at all
        pass
    elif clawdata.checkpt_style == 1:  # checkpoint only at tfinal.
        pass
    elif clawdata.checkpt_style == 2:  # specify a list of checkpoint times.
        clawdata.checkpt_times = [0.1, 0.15]
    elif clawdata.checkpt_style == 3:  # checkpoint every checkpt_interval timesteps (on Level 1)
        clawdata.checkpt_interval = 5

    return rundata


def setamr(rundata: data.ClawRunData):
    """Set AmrClaw specific runtime parameters."""

    try:
        amrdata = rundata.amrdata
    except AttributeError as err:
        raise AttributeError("This rundata has no amrdata attribute") from err

    # max number of refinement levels:
    amrdata.amr_levels_max = 2

    # List of refinement ratios at each level (length at least mxnest-1)
    amrdata.refinement_ratios_x = [4]
    amrdata.refinement_ratios_y = [4]
    amrdata.refinement_ratios_t = [4]

    # aux variables are defined at cell centers
    amrdata.aux_type = ['center', 'center']

    # use flag2refine routine to flag refinement (rather than using richardson error)
    amrdata.flag_richardson = False
    amrdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    amrdata.regrid_interval = 1

    # width of buffer zone around flagged points
    amrdata.regrid_buffer_width = 1

    # clustering alg. cutoff for (# flagged pts) / (total # of cells refined)
    amrdata.clustering_cutoff = 0.80000

    # print info about each regridding up to this level:
    amrdata.verbosity_regrid = 0

    #  ----- For developers -----
    # Toggle debugging print statements:
    amrdata.dprint = False      # print domain flags
    amrdata.eprint = False      # print err est flags
    amrdata.edebug = False      # even more err est flags
    amrdata.gprint = False      # grid bisection/clustering
    amrdata.nprint = False      # proper nesting output
    amrdata.pprint = False      # proj. of tagged points
    amrdata.rprint = False      # print regridding summary
    amrdata.sprint = False      # space/memory output
    amrdata.tprint = False      # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting

    # customize regions of refinement
    # rundata.regiondata.regions.append([minlevel, maxlevel, t1, t2, x1, x2, y1, y2])

    # gauges
    # rundata.gaugedata.gauges.append([gaugeno, x, y, t1, t2])

    return rundata


def setgeo(rundata: data.ClawRunData):
    """Set GeoClaw specific runtime parameters."""

    try:
        geo_data = rundata.geo_data
    except AttributeError as err:
        raise AttributeError("This rundata has no geo_data attribute") from err

    # == Physics ==
    geo_data.gravity = 9.81
    geo_data.coordinate_system = 1
    geo_data.earth_radius = 6367.5e3

    # == Forcing Options
    geo_data.coriolis_forcing = False

    # == Algorithm and Initial Conditions ==
    geo_data.sea_level = 0.0
    geo_data.dry_tolerance = 1.e-4
    geo_data.friction_forcing = False
    geo_data.manning_coefficient = 0.035
    geo_data.friction_depth = 1.e6

    # Refinement data
    refinement_data = rundata.refinement_data
    refinement_data.wave_tolerance = 1.e-5
    refinement_data.speed_tolerance = [1e-8]
    refinement_data.variable_dt_refinement_ratios = True

    # for topography, append lines of the form [topotype, fname]
    topo_data = rundata.topo_data
    topo_data.topofiles.append([3, '../common-files/salt_lake_2.asc'])

    # for moving topography, append lines of the form: [topotype, fname]
    # dtopo_data = rundata.dtopo_data

    # for qinit perturbations, append lines of the form: [fname]
    rundata.qinit_data.qinit_type = 0
    rundata.qinit_data.qinitfiles = []

    # for fixed grids append lines of the form
    # [t1, t2, noutput, x1, x2, y1, y2, xpoints, ypoints, ioutarrivaltimes, ioutsurfacemax]
    # fixedgrids = rundata.fixed_grid_data

    # Land-spill module settings
    rundata.add_data(LandSpillData(), 'landspill_data')
    landspill = rundata.landspill_data
    landspill.ref_mu = 0.6512 # cP @ 15 degree C
    landspill.ref_temperature = 15.
    landspill.ambient_temperature = 25.
    landspill.density = 800. # kg / m^3 @ 15 degree C; will overwrite rho in GeoClaw

    # extra parameters
    landspill.update_tol = geo_data.dry_tolerance
    landspill.refine_tol = 0.0

    # Point sources
    ptsources_data = landspill.point_sources
    ptsources_data.n_point_sources = 1
    ptsources_data.point_sources.append(
        [[-12460209.5, 4985137.4], 2, [1800., 12600.], [0.5, 0.1]])

    # Darcy-Weisbach friction
    darcy_weisbach_data = landspill.darcy_weisbach_friction
    darcy_weisbach_data.type = 4
    darcy_weisbach_data.dry_tol = 1e-4
    darcy_weisbach_data.friction_tol = 1e6
    darcy_weisbach_data.default_roughness = 0.0
    darcy_weisbach_data.filename = "roughness.txt"

    # hydrological features
    hydro_feature_data = landspill.hydro_features
    hydro_feature_data.files.append("../common-files/hydro2.asc")

    # Evaporation
    evaporation_data = landspill.evaporation
    evaporation_data.type = 0
    evaporation_data.coefficients = [13.2, 0.21]

    return rundata
