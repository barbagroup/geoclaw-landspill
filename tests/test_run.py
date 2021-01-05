#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Test the subcommand `run`.
"""
import os
import sys
import re
import pytest
import gclandspill.__main__


class TestRun:
    """Test the subcommand `run`."""
    # pylint: disable=no-self-use

    def test_run_1(self, tmpdir):
        """Test if the executable can run and returns expected errors."""

        sys.argv = ["geoclaw-landspill", "run", str(tmpdir)]
        with pytest.raises(FileNotFoundError) as err:
            gclandspill.__main__.main()
        assert err.type == FileNotFoundError

    def test_run_2(self, tmpdir, capfd):
        """Test if the executable can run and returns expected errors."""

        _create_data_2(tmpdir)
        sys.argv = ["geoclaw-landspill", "run", str(tmpdir)]
        gclandspill.__main__.main()
        sys.stdout.flush()
        sys.stderr.flush()
        captured = capfd.readouterr()
        results = re.search(r"Done integrating to time\s+2.0+", captured.out)
        assert results is not None


_SETRUN_CONTENT = """#! /usr/bin/env python
import gclandspill
def setrun(prog="geoclaw"):
    rundata = gclandspill.clawutil.data.ClawRunData("geoclaw", 2)
    rundata.add_data(gclandspill.data.LandSpillData(), 'landspill_data')
    rundata.clawdata.num_dim = 2
    rundata.clawdata.lower[:] = [-1.0, -1.0]
    rundata.clawdata.upper[:] = [1.0, 1.0]
    rundata.clawdata.num_cells[:] = [50, 50]
    rundata.clawdata.num_eqn = 3
    rundata.clawdata.num_aux = 2
    rundata.clawdata.output_style = 2
    rundata.clawdata.output_times = [0., 1., 2.]
    rundata.clawdata.output_format = 'binary'
    rundata.clawdata.transverse_waves = 2
    rundata.clawdata.num_waves = 3
    rundata.clawdata.limiter = ['mc', 'mc', 'mc']
    rundata.clawdata.use_fwaves = True
    rundata.clawdata.source_split = 'godunov'
    rundata.clawdata.num_ghost = 2
    rundata.clawdata.bc_lower[:] = [1, 1]
    rundata.clawdata.bc_upper[:] = [1, 1]
    rundata.amrdata.amr_levels_max = 2
    rundata.amrdata.refinement_ratios_x = [4]
    rundata.amrdata.refinement_ratios_y = [4]
    rundata.amrdata.refinement_ratios_t = [4]
    rundata.amrdata.aux_type = ['center', 'center']
    rundata.geo_data.gravity = 9.81
    rundata.geo_data.coriolis_forcing = False
    rundata.geo_data.sea_level = 0.0
    rundata.geo_data.dry_tolerance = 1.e-4
    rundata.geo_data.friction_forcing = False
    rundata.refinement_data.wave_tolerance = 1.e-5
    rundata.refinement_data.speed_tolerance = [1e-8]
    rundata.refinement_data.variable_dt_refinement_ratios = True
    rundata.topo_data.topofiles.append([3, 'toy.asc'])
    rundata.landspill_data.update_tol = rundata.geo_data.dry_tolerance
    rundata.landspill_data.point_sources.n_point_sources = 1
    rundata.landspill_data.point_sources.point_sources.append([[0., 0.], 1, [10.], [1e-6]])
    rundata.landspill_data.darcy_weisbach_friction.type = 4
    rundata.landspill_data.darcy_weisbach_friction.dry_tol = 1e-4
    rundata.landspill_data.darcy_weisbach_friction.friction_tol = 1e6
    rundata.landspill_data.darcy_weisbach_friction.default_roughness = 0.0
    rundata.landspill_data.darcy_weisbach_friction.filename = "roughness.asc"
    rundata.landspill_data.evaporation.type = 1
    rundata.landspill_data.evaporation.coefficients = [1.38, 0.045]
    return rundata
"""


def _create_data_2(case_dir):
    """Create run data for TestBin.test_bin_run_2."""
    # pylint: disable=no-member, too-many-statements

    with open(os.path.join(case_dir, "setrun.py"), "w") as fileobj:
        fileobj.write(_SETRUN_CONTENT)

    with open(os.path.join(case_dir, "toy.asc"), "w") as fileobj:
        fileobj.write("ncols          4\n")
        fileobj.write("nrows          4\n")
        fileobj.write("xllcorner     -2.0\n")
        fileobj.write("yllcorner     -2.0\n")
        fileobj.write("cellsize       1.0\n")
        fileobj.write("NODATA_value  -9999\n")
        fileobj.write("\n")
        for _ in range(4):
            fileobj.write("0.0 0.0 0.0 0.0\n")

    with open(os.path.join(case_dir, "roughness.asc"), "w") as fileobj:
        fileobj.write("ncols          4\n")
        fileobj.write("nrows          4\n")
        fileobj.write("xllcorner     -2.0\n")
        fileobj.write("yllcorner     -2.0\n")
        fileobj.write("cellsize       1.0\n")
        fileobj.write("NODATA_value  -9999\n")
        fileobj.write("\n")
        for _ in range(4):
            fileobj.write("0.0 0.0 0.0 0.0\n")
