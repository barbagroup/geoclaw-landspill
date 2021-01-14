"""Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.
"""
# pylint: disable=no-member, too-many-statements
import gclandspill.data


def setrun():
    """Define the parameters used for running Clawpack.

    Returns
    -------
    rundata : gclandspill.data.ClawRunData
    """

    rundata = gclandspill.data.ClawRunData()

    # for convenience
    break_point = [-12459650., 4986000.]

    # lower and upper edges of computational domain
    rundata.clawdata.lower[0] = break_point[0]-400.
    rundata.clawdata.upper[0] = break_point[0]+400.
    rundata.clawdata.lower[1] = break_point[1]-400
    rundata.clawdata.upper[1] = break_point[1]+400

    # number of grid cells: coarsest grid
    rundata.clawdata.num_cells[0] = 200
    rundata.clawdata.num_cells[1] = 200

    # temporal data output
    rundata.clawdata.output_style = 1
    rundata.clawdata.num_output_times = 240
    rundata.clawdata.tfinal = 28800
    rundata.clawdata.output_t0 = True  # output at initial (or restart) time?

    # add a topography file; format [topotype, fname]
    rundata.topo_data.topofiles.append([3, '../common-files/utah-flat.asc'])

    # Land-spill module settings
    rundata.landspill_data.ref_mu = 332.  # cP @ 15 degree C
    rundata.landspill_data.ref_temperature = 15.
    rundata.landspill_data.ambient_temperature = 25.
    rundata.landspill_data.density = 9.266e2  # kg / m^3 @ 15 degree C; will overwrite rho in GeoClaw

    # Point sources
    rundata.landspill_data.point_sources.n_point_sources = 1
    rundata.landspill_data.point_sources.point_sources.append([break_point, 2, [1800., 12600.], [0.5, 0.1]])

    # Darcy-Weisbach friction
    rundata.landspill_data.darcy_weisbach_friction.type = 4
    rundata.landspill_data.darcy_weisbach_friction.default_roughness = 0.0
    rundata.landspill_data.darcy_weisbach_friction.filename = "roughness.txt"

    # add a hydrological feature raster file
    rundata.landspill_data.hydro_features.files.append("../common-files/utah-flat-hydro.asc")

    # Evaporation
    rundata.landspill_data.evaporation.type = 0
    rundata.landspill_data.evaporation.coefficients = [1.38, 0.045]

    return rundata
