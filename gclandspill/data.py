#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.


"""Classes representing parameters for geoclaw-landspill runs.
"""
import os
from functools import reduce as _reduce
from gclandspill import clawutil as _clawutil
from gclandspill import _misc


class ClawRunData(_clawutil.data.ClawRunData):
    """A modified version of ClawRunData for geoclaw-landspill.

    This ClawRunData has an additional LandSpillData instance. Also, the following default values are modified:

        # core classical clawpack configuration
        self.clawdata.num_eqn = 2
        self.clawdata.num_waves = 3
        self.clawdata.num_aux = 2
        self.clawdata.output_format = 3  # binary
        self.clawdata.output_aux_components = "all"
        self.clawdata.output_aux_onlyonce = False
        self.clawdata.dt_initial = None
        self.clawdata.dt_max = 5.0
        self.clawdata.cfl_max = 0.95
        self.clawdata.steps_max = 100000
        self.clawdata.verbosity = 5
        self.clawdata.verbosity_regrid = 5
        self.clawdata.source_split = 1  # godunov
        self.clawdata.limiter = [4, 4, 4]  # use "mc" limiter for all equations
        self.clawdata.use_fwaves = True
        self.clawdata.bc_lower = [1, 1]
        self.clawdata.bc_upper = [1, 1]

        # AMRClaw configuration
        self.amrdata.amr_levels_max = 2
        self.amrdata.refinement_ratios_x = [4]
        self.amrdata.refinement_ratios_y = [4]
        self.amrdata.refinement_ratios_t = [4]
        self.amrdata.aux_type = ["center", "center"]  # aux variables are defined at cell centers
        self.amrdata.regrid_interval = 1
        self.amrdata.verbosity_regrid = 5

        # GeoClaw basic configuration
        self.geo_data.gravity = 9.81
        self.geo_data.coriolis_forcing = False
        self.geo_data.sea_level = -1000.
        self.geo_data.dry_tolerance = 1e-4
        self.geo_data.friction_forcing = False  # turned off in favor of Darcy-Weisbach friction

        # GeoClaw refinement mechanism
        self.refinement_data.wave_tolerance = 1.0e-5
        self.refinement_data.speed_tolerance = [1e-5] * 6
        self.refinement_data.variable_dt_refinement_ratios = True
    """

    def __init__(self):
        # pylint: disable=no-member
        super().__init__("geoclaw", 2)  # to first get attributes from geoclaw and with dimension 2

        # modify attributes for geoclaw-landspill
        self.pkg = "geoclaw-landspill"
        self.xclawcmd = "geoclaw-landspill-bin"

        # append a landspill data instance to the data object
        self.add_data(LandSpillData(), 'landspill_data')

        # core classical clawpack configuration
        self.clawdata.num_eqn = 3
        self.clawdata.num_waves = 3
        self.clawdata.num_aux = 2
        self.clawdata.output_format = 3  # binary
        self.clawdata.output_aux_components = "all"
        self.clawdata.output_aux_onlyonce = False
        self.clawdata.dt_initial = None
        self.clawdata.dt_max = 5.0
        self.clawdata.cfl_max = 0.95
        self.clawdata.steps_max = 100000
        self.clawdata.verbosity = 5
        self.clawdata.verbosity_regrid = 5
        self.clawdata.source_split = 1  # godunov
        self.clawdata.limiter = [4, 4, 4]  # use "mc" limiter for all equations
        self.clawdata.use_fwaves = True
        self.clawdata.bc_lower = [1, 1]
        self.clawdata.bc_upper = [1, 1]

        # AMRClaw configuration
        self.amrdata.amr_levels_max = 2
        self.amrdata.refinement_ratios_x = [4]
        self.amrdata.refinement_ratios_y = [4]
        self.amrdata.refinement_ratios_t = [4]
        self.amrdata.aux_type = ["center", "center"]  # aux variables are defined at cell centers
        self.amrdata.regrid_interval = 1
        self.amrdata.verbosity_regrid = 5

        # GeoClaw basic configuration
        self.geo_data.gravity = 9.81
        self.geo_data.coriolis_forcing = False
        self.geo_data.sea_level = -1000.
        self.geo_data.dry_tolerance = 1e-4
        self.geo_data.friction_forcing = False  # turned off in favor of Darcy-Weisbach friction

        # GeoClaw refinement mechanism
        self.refinement_data.wave_tolerance = 1.0e-5
        self.refinement_data.speed_tolerance = [1e-5] * 6
        self.refinement_data.variable_dt_refinement_ratios = True

    def write(self, out_dir=""):

        # check and set some automatically determined values
        self._check()

        super().write(out_dir)

    def _check(self):
        """Check and set some automatically determined values."""
        # pylint: disable=no-member

        # automatically determine dt_initial
        if self.clawdata.dt_initial is None:
            cell_area = \
                (self.clawdata.upper[0] - self.clawdata.lower[0]) * \
                (self.clawdata.upper[1] - self.clawdata.lower[1]) / \
                (self.clawdata.num_cells[0] * self.clawdata.num_cells[1])
            cell_area /= _reduce(lambda x, y: x*y, self.amrdata.refinement_ratios_x[:self.amrdata.amr_levels_max], 1)
            cell_area /= _reduce(lambda x, y: x*y, self.amrdata.refinement_ratios_y[:self.amrdata.amr_levels_max], 1)
            vrate = self.landspill_data.point_sources.point_sources[0][-1][0]

            self.clawdata.dt_initial = 0.3 * cell_area / vrate

        if self.landspill_data.update_tol is None:
            self.landspill_data.update_tol = self.geo_data.dry_tolerance

        if self.landspill_data.darcy_weisbach_friction.type != 0 and self.geo_data.friction_forcing:
            raise _misc.FrictionModelError("Both Manning and Darcy-Weisbach models are enabled.")

        if self.landspill_data.darcy_weisbach_friction.dry_tol is None:
            self.landspill_data.darcy_weisbach_friction.dry_tol = self.geo_data.dry_tolerance

        if self.landspill_data.darcy_weisbach_friction.friction_tol is None:
            self.landspill_data.darcy_weisbach_friction.friction_tol = self.geo_data.friction_depth


# Land-spill data
class LandSpillData(_clawutil.data.ClawData):
    """Data object describing land spill simulation configurations"""

    def __init__(self):
        """Constructor of LandSpillData class"""

        super().__init__()

        # Reference dynamic viscosity used in temperature-dependent viscosity
        self.add_attribute('ref_mu', 332.)  # unit: mPa-s (= cP = 1e-3kg/s/m)

        # Reference temperature at which the nu_ref is
        self.add_attribute('ref_temperature', 15.)  # unit: Celsius

        # Ambient temperature (Celsius)
        self.add_attribute('ambient_temperature', 25.)  # unit: Celsius

        # Density at ambient temperature
        self.add_attribute('density', 926.6)  # unit: kg / m^3

        # extra parameters to hack the AMR algorithms for landspill applications
        self.add_attribute("update_tol", None)
        self.add_attribute("refine_tol", 0.0)

        # add point source data
        self.add_attribute('point_sources_file', 'point_source.data')
        self.add_attribute('point_sources', PointSourceData())

        # add Darcy-Weisbach friction
        self.add_attribute('darcy_weisbach_file', 'darcy_weisbach.data')
        self.add_attribute('darcy_weisbach_friction', DarcyWeisbachData())

        # add hydrological features
        self.add_attribute('hydro_feature_file', 'hydro_feature.data')
        self.add_attribute('hydro_features', HydroFeatureData())

        # add evaporation model
        self.add_attribute('evaporation_file', 'evaporation.data')
        self.add_attribute('evaporation', EvaporationData())

    def write(self, out_file='landspill.data', data_source="setrun.py"):
        """Write out the data file to the path given"""

        # to make sure child data files are written to the same folder
        base = os.path.dirname(out_file)

        # open the output file
        self.open_data_file(out_file, data_source)

        self.data_write('ref_mu',
                        description='Reference dynamic viscosity (mPa-s)')
        self.data_write('ref_temperature',
                        description='Reference temperature for \
                            temperature-dependent viscosity (Celsius)')
        self.data_write('ambient_temperature',
                        description='Ambient temperature (Celsius)')
        self.data_write('density',
                        description='Density at ambient temperature (kg/m^3')

        # tolerance to control mesh refinement specifically to landspill applications
        self.data_write("update_tol")
        self.data_write("refine_tol")

        # output point sources data
        self.data_write('point_sources_file',
                        description='File name of point sources settings')
        self.point_sources.write(os.path.join(base, self.point_sources_file))  # pylint: disable=no-member

        # output Darcy-Weisbach data
        self.data_write('darcy_weisbach_file',
                        description='File name of Darcy-Weisbach settings')
        self.darcy_weisbach_friction.write(os.path.join(base, self.darcy_weisbach_file))  # pylint: disable=no-member

        # output hydroological feature data
        self.data_write('hydro_feature_file',
                        description='File name of hydrological feature settings')
        self.hydro_features.write(os.path.join(base, self.hydro_feature_file))  # pylint: disable=no-member

        # output evaporation data
        self.data_write('evaporation_file',
                        description='File name of evaporation settings')
        self.evaporation.write(os.path.join(base, self.evaporation_file))  # pylint: disable=no-member

        # close the output file
        self.close_data_file()


# Point source data
class PointSourceData(_clawutil.data.ClawData):
    """Data object describing point sources"""

    def __init__(self):
        """Constructor of PointSourceData class"""

        super().__init__()

        # number of point sources
        self.add_attribute('n_point_sources', 0)

        # a list of point sources
        self.add_attribute('point_sources', [])

    def write(self, out_file='point_source.data', data_source="setrun.py"):
        """Write out the data file to the path given"""

        # check data consistency
        self._check()

        # open the output file
        self.open_data_file(out_file, data_source)

        # write number of point sources
        self.data_write('n_point_sources', description='Number of point sources')

        # write point sources
        for i, pts in enumerate(self.point_sources):  # pylint: disable=no-member
            self.data_write()  # a blank line
            self.data_write("id", i, description="ID of this point source")
            self.data_write("coord", pts[0], description="coordinates")
            self.data_write("n_times", pts[1], description="number of time segments")
            self.data_write("end_times", pts[2], description="end times of segments")
            self.data_write("vol_rates", pts[3], description="volumetric rates of segments")

        # close the output file
        self.close_data_file()

    def _check(self):
        """Check if the data are consistent"""
        # pylint: disable=no-member

        # check if the number of data set match n_point_sources
        assert self.n_point_sources == len(self.point_sources),  \
            "The number of point sources is not consistent with point source data."

        # check the records of point sources
        for i, pts in enumerate(self.point_sources):
            assert len(pts) == 4, "There should be 4 records in the data of " \
                "the {}-th point source.".format(i)
            assert isinstance(pts[0], list), "The coordinate of the {}-th " \
                "point source is not a Python list.".format(i)
            assert len(pts[0]) == 2, "The coordinate of the {}-th point " \
                "is not in the format of [x, y].".format(i)
            assert isinstance(pts[1], int), "The 2nd record in the data of " \
                "the {}-th point source should be an integer for the number " \
                "of time segments.".format(i)
            assert isinstance(pts[2], list), "The end times of the time segments " \
                "of the {}-th point source is not a Python list.".format(i)
            assert len(pts[2]) == pts[1], "The number of end times does not " \
                "match the integer provided for the {}-th point source.".format(i)
            assert sorted(pts[2]) == pts[2], "The list of end times is not " \
                "sorted in an ascending order."
            assert isinstance(pts[3], list), "The volumetric rates of the time " \
                "segments of the {}-th point source is not a Python list.".format(i)
            assert len(pts[3]) == pts[1], "The number of volumetric rates does " \
                "not match the integer provided for the {}-th point source.".format(i)


# Darcy-Weisbach data
class DarcyWeisbachData(_clawutil.data.ClawData):
    """Data object describing Darcy-Weisbach friction model"""

    def __init__(self):
        """Constructor of DarcyWeisbachData class"""

        super().__init__()

        # type of the friction coefficients
        # 0: trun off the feature and return control to GeoClaw's Manning friction
        # 1: constant coefficient everywhere
        # 2: block-wise constants
        # 3: cell-wise coefficients
        # 4: three-regime coefficient model
        # 5: Churchill's coefficient model
        # 6: two-regime coefficient model: laminar + Colebrook-White
        self.add_attribute('type', 0)

        # friction_tol, the same as the friction_depth in GeoClaw.
        self.add_attribute('friction_tol', None)

        # dry_tol, the same as dry_tolerance in GeoClaw.
        self.add_attribute('dry_tol', None)

        # single constant coefficient.
        self.add_attribute('coefficient', 0.25)

        # default coefficient; only meaningful for type 2 and 3
        self.add_attribute('default_coefficient', 0.25)

        # number of blocks; only meaningful for type 2
        self.add_attribute('n_blocks', 0)

        # blocks' corners; only meaningful for type 2
        self.add_attribute('xlowers', [])
        self.add_attribute('xuppers', [])
        self.add_attribute('ylowers', [])
        self.add_attribute('yuppers', [])

        # coefficients; only meaningful for type 2
        self.add_attribute('coefficients', [])

        # filename; only meaningful for type 3, 4, 5, 6
        self.add_attribute('filename', '')

        # default_roughness; only meaningful for type 4, 5, 6
        self.add_attribute('default_roughness', 0.0)

    def write(self, out_file='darcy_weisbach.data', data_source="setrun.py"):
        """Write out the data file to the path given"""
        # pylint: disable=access-member-before-definition, attribute-defined-outside-init, no-member

        # check data consistency
        self._check()

        # process the absolute path to the filename (even though it's not used in type 1 & 2)
        # Relative path will be relative to the folder containing `out_file` (following how geoclaw
        # handles topo files)
        if not os.path.isabs(self.filename):
            self.filename = os.path.abspath(os.path.join(os.path.dirname(out_file), self.filename))

        # open the output file
        self.open_data_file(out_file, data_source)

        # write number of point sources
        self.data_write('type', description='Type of Darcy-Weisbach coefficient')

        # if this deature is disabled, close the file and return
        if self.type == 0:
            self.close_data_file()
            return

        # for other non-zero options
        self.data_write('friction_tol', description='Same meanining as the ' +
                        'friction_depth in original GeoClaw setting.')
        self.data_write('dry_tol', description='Same meaning as the ' +
                        'dry_tolerance in original GeoClaw setting.')

        if self.type == 1:
            self.data_write('coefficient',
                            description="Darcy-Weisbach coefficient")
        elif self.type == 2:
            self.data_write('default_coefficient',
                            description="coefficient for uncovered areas")
            self.data_write('n_blocks',
                            description="number of blocks")
            self.data_write('xlowers',
                            description="x lower coords for blocks")
            self.data_write('xuppers',
                            description="x upper coords for blocks")
            self.data_write('ylowers',
                            description="x lower coords for blocks")
            self.data_write('yuppers',
                            description="x upper coords for blocks")
            self.data_write('coefficients',
                            description="coefficients in blocks")
        elif self.type == 3:
            self.data_write('filename',
                            description="Escri ASCII file for coefficients")
            self.data_write('default_coefficient',
                            description="coefficient for cells not covered by the file")
        elif self.type in [4, 5, 6]:
            self.data_write('filename',
                            description="Escri ASCII file for roughness")
            self.data_write('default_roughness',
                            description="roughness for cells not covered by the file")

        # close the output file
        self.close_data_file()

    def _check(self):
        """Check if the data are consistent"""
        # pylint: disable=no-member

        assert isinstance(self.type, int), "Type should be an integer."

        # 0: this feature disabled
        if self.type == 0:
            return

        # common data for non-zero options
        assert isinstance(self.friction_tol, float), \
            "friction_tol shoudl be a floating number."
        assert isinstance(self.dry_tol, float), \
            "dry_toll shoudl be a floating number."

        # non-zero options
        if self.type == 1:
            assert isinstance(self.default_coefficient, float), \
                "default_coefficient shoudl be a floating number."
        elif self.type == 2:
            assert isinstance(self.n_blocks, int), \
                "n_blocks shoudl be a floating number."
            assert isinstance(self.xlowers, list), \
                "xlowers shoudl be a list."
            assert len(self.xlowers) == self.n_blocks, \
                "the length of xlowers shoudl be n_blocks."
            assert isinstance(self.xuppers, list), \
                "xuppers shoudl be a list."
            assert len(self.xuppers) == self.n_blocks, \
                "the length of xuppers shoudl be n_blocks."
            assert isinstance(self.ylowers, list), \
                "ylowers shoudl be a list."
            assert len(self.ylowers) == self.n_blocks, \
                "the length of ylowers shoudl be n_blocks."
            assert isinstance(self.yuppers, list), \
                "yuppers shoudl be a list."
            assert len(self.yuppers) == self.n_blocks, \
                "the length of yuppers shoudl be n_blocks."
            assert isinstance(self.coefficients, list), \
                "coefficients shoudl be a list."
            assert len(self.coefficients) == self.n_blocks, \
                "the length of coefficients shoudl be n_blocks."
        elif self.type in [3, 4, 5, 6]:
            assert isinstance(self.filename, str), \
                "filename should be a string."
            assert self.filename != "", \
                "filename can not be empty."

            if self.type == 3:
                assert isinstance(self.default_coefficient, float), \
                    "default_coefficient shoudl be a float"
            else:
                assert isinstance(self.default_roughness, float), \
                    "default_roughness shoudl be a float"
        else:
            raise ValueError("Type values outside [0, 5] not allowed.")


# Hydrologic feature data
class HydroFeatureData(_clawutil.data.ClawData):
    """Data object describing hydrologic features"""

    def __init__(self):
        """Constructor of HydroFeatureData class"""

        super().__init__()

        # a list of files of hydro features
        self.add_attribute('files', [])

    def write(self, out_file='hydro_feature.data', data_source="setrun.py"):
        """Write out the data file to the path given"""

        # open the output file
        self.open_data_file(out_file, data_source)

        # write number of files
        self.data_write('n_files', len(self.files),  # pylint: disable=no-member
                        description='Number of hydro files')

        # write file names line by line
        for i, single_file in enumerate(self.files):  # pylint: disable=no-member
            # relative path will be relative to the folder containing `out_file` (following how
            # geoclaw handles topo files)
            if not os.path.isabs(single_file):
                single_file = os.path.abspath(os.path.join(os.path.dirname(out_file), single_file))
            self.data_write('file {0}'.format(i), single_file)

        # close the output file
        self.close_data_file()


# Evaporation data
class EvaporationData(_clawutil.data.ClawData):
    """Data object describing evaporation"""

    def __init__(self):
        """Constructor of EvaporationData class"""

        super().__init__()

        # type of evaporation model
        # 0: no evaporation
        # 1: Fingas 1996 model, natural log law
        # 2: Fingas 1996 model, square root law
        self.add_attribute('type', 0)

        # a list of model coefficients
        self.add_attribute('coefficients', [])

    def write(self, out_file='evaporation.data', data_source="setrun.py"):
        """Write out the data file to the path given"""

        # check data consistency
        self._check()

        # open the output file
        self.open_data_file(out_file, data_source)

        # write model type
        self.data_write('type', description='Evaporation type')

        # number of coefficients
        self.data_write('n_coefficients', len(self.coefficients),  # pylint: disable=no-member
                        description='Number of evaporation coefficients.')

        for i, coeff in enumerate(self.coefficients):  # pylint: disable=no-member
            self.data_write('C{}'.format(i), coeff,
                            description='Coefficient {}'.format(i))

        # close the output file
        self.close_data_file()

    def _check(self):
        """Check if the data are consistent"""

        assert isinstance(self.type, int), "Evaporation type should be an integer."  # pylint: disable=no-member
        assert self.type in [0, 1, 2], "Evaporation type should be in [0, 1, 2]"  # pylint: disable=no-member
