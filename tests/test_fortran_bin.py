#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Test geoclaw-landspill-bin.
"""
import os
import re
import subprocess
from pathlib import Path
import gclandspill


exe = Path(gclandspill.__file__).parent.joinpath("bin", "geoclaw-landspill-bin")


def create_data():
    """Create run data for TestBin.test_bin_run_2."""
    # pylint: disable=no-member, too-many-statements

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
    rundata.write()

    with open("toy.asc", "w") as fileobj:
        fileobj.write("ncols          4\n")
        fileobj.write("nrows          4\n")
        fileobj.write("xllcorner     -2.0\n")
        fileobj.write("yllcorner     -2.0\n")
        fileobj.write("cellsize       1.0\n")
        fileobj.write("NODATA_value  -9999\n")
        fileobj.write("\n")
        for _ in range(4):
            fileobj.write("0.0 0.0 0.0 0.0\n")

    with open("roughness.asc", "w") as fileobj:
        fileobj.write("ncols          4\n")
        fileobj.write("nrows          4\n")
        fileobj.write("xllcorner     -2.0\n")
        fileobj.write("yllcorner     -2.0\n")
        fileobj.write("cellsize       1.0\n")
        fileobj.write("NODATA_value  -9999\n")
        fileobj.write("\n")
        for _ in range(4):
            fileobj.write("0.0 0.0 0.0 0.0\n")


def test_bin_exist():
    """Test if the binary geoclaw-landspill-bin exists at the correct path."""
    assert exe.is_file()


def test_bin_executable():
    """Test if the binary geoclaw-landspill-bin is executable."""
    assert os.access(exe, os.X_OK)


def test_bin_run_1(tmpdir):
    """Test if the executable can run and returns expected errors."""
    cwd = os.getcwd()
    os.chdir(tmpdir)
    results = subprocess.run([exe], capture_output=True, check=True)
    assert results.stdout == b"*** in opendatafile, file not found:claw.data\n"
    os.chdir(cwd)


def test_bin_run_2(tmpdir):
    """Test if the executable can run up to the desired final time."""
    cwd = os.getcwd()
    os.chdir(tmpdir)
    create_data()
    results = subprocess.run([exe], capture_output=True, check=True)
    results = re.search(r"Done integrating to time\s+2.0+", results.stdout.decode("utf-8"))
    assert results is not None
    os.chdir(cwd)
