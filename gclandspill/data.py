#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.


"""Classes representing parameters for geoclaw-landspill runs
"""
import os
import gclandspill.clawutil.data
# pylint: disable=no-member, attribute-defined-outside-init, fixme
# TODO: merge the friction models of GeoClaw and landspill
# TODO: merge dry_tol and dry_tolerance from GeoClaw and landspill


# Land-spill data
class LandSpillData(gclandspill.clawutil.data.ClawData):
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
        self.add_attribute("update_tol", 0.0)
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
        self.point_sources.write(os.path.join(base, self.point_sources_file))

        # output Darcy-Weisbach data
        self.data_write('darcy_weisbach_file',
                        description='File name of Darcy-Weisbach settings')
        self.darcy_weisbach_friction.write(os.path.join(base, self.darcy_weisbach_file))

        # output hydroological feature data
        self.data_write('hydro_feature_file',
                        description='File name of hydrological feature settings')
        self.hydro_features.write(os.path.join(base, self.hydro_feature_file))

        # output evaporation data
        self.data_write('evaporation_file',
                        description='File name of evaporation settings')
        self.evaporation.write(os.path.join(base, self.evaporation_file))

        # close the output file
        self.close_data_file()


# Point source data
class PointSourceData(gclandspill.clawutil.data.ClawData):
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
        for i, pts in enumerate(self.point_sources):
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
class DarcyWeisbachData(gclandspill.clawutil.data.ClawData):
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

        # friction_tol, the same as friction_tol in GeoClaw.
        self.add_attribute('friction_tol', 1e6)

        # dry_tol, the same as dry_tolerance in GeoClaw.
        self.add_attribute('dry_tol', 1e-6)

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
class HydroFeatureData(gclandspill.clawutil.data.ClawData):
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
        self.data_write('n_files', len(self.files),
                        description='Number of hydro files')

        # write file names line by line
        for i, single_file in enumerate(self.files):
            # relative path will be relative to the folder containing `out_file` (following how
            # geoclaw handles topo files)
            if not os.path.isabs(single_file):
                single_file = os.path.abspath(os.path.join(os.path.dirname(out_file), single_file))
            self.data_write('file {0}'.format(i), single_file)

        # close the output file
        self.close_data_file()


# Evaporation data
class EvaporationData(gclandspill.clawutil.data.ClawData):
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
        self.data_write('n_coefficients', len(self.coefficients),
                        description='Number of evaporation coefficients.')

        for i, coeff in enumerate(self.coefficients):
            self.data_write('C{}'.format(i), coeff,
                            description='Coefficient {}'.format(i))

        # close the output file
        self.close_data_file()

    def _check(self):
        """Check if the data are consistent"""

        assert isinstance(self.type, int), "Evaporation type should be an integer."
        assert self.type in [0, 1, 2], "Evaporation type should be in [0, 1, 2]"
