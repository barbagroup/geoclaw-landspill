#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Regression test 1."""
# pylint: disable=redefined-outer-name
import sys
import csv
import pathlib
import pytest
import rasterio
import matplotlib.pyplot
import gclandspill.__main__
import gclandspill.pyclaw


@pytest.fixture(scope="session")
def create_case(tmp_path_factory):
    """A pytest fixture to make a temp case available across different tests."""

    case_dir = tmp_path_factory.mktemp("regression-test-1")

    content = (
        "#! /usr/bin/env python\n"
        "import gclandspill\n"
        "def setrun(prog='geoclaw'):\n"
        "\trundata = gclandspill.clawutil.data.ClawRunData('geoclaw', 2)\n"
        "\trundata.add_data(gclandspill.data.LandSpillData(), 'landspill_data')\n"
        "\trundata.clawdata.num_dim = 2\n"
        "\trundata.clawdata.lower[:] = [-0.1, -0.1]\n"
        "\trundata.clawdata.upper[:] = [0.1, 0.1]\n"
        "\trundata.clawdata.num_cells[:] = [50, 50]\n"
        "\trundata.clawdata.num_eqn = 3\n"
        "\trundata.clawdata.num_aux = 2\n"
        "\trundata.clawdata.output_style = 2\n"
        "\trundata.clawdata.output_times = list(range(6))\n"
        "\trundata.clawdata.output_format = 'binary'\n"
        "\trundata.clawdata.dt_variable = True\n"
        "\trundata.clawdata.dt_initial = 1e-4\n"
        "\trundata.clawdata.dt_max = 0.01\n"
        "\trundata.clawdata.transverse_waves = 2\n"
        "\trundata.clawdata.num_waves = 3\n"
        "\trundata.clawdata.limiter = ['mc', 'mc', 'mc']\n"
        "\trundata.clawdata.use_fwaves = True\n"
        "\trundata.clawdata.source_split = 'godunov'\n"
        "\trundata.clawdata.num_ghost = 2\n"
        "\trundata.clawdata.bc_lower[:] = [1, 1]\n"
        "\trundata.clawdata.bc_upper[:] = [1, 1]\n"
        "\trundata.amrdata.amr_levels_max = 2\n"
        "\trundata.amrdata.refinement_ratios_x = [4]\n"
        "\trundata.amrdata.refinement_ratios_y = [4]\n"
        "\trundata.amrdata.refinement_ratios_t = [4]\n"
        "\trundata.amrdata.aux_type = ['center', 'center']\n"
        "\trundata.geo_data.gravity = 9.81\n"
        "\trundata.geo_data.coriolis_forcing = False\n"
        "\trundata.geo_data.sea_level = 0.0\n"
        "\trundata.geo_data.dry_tolerance = 1.e-4\n"
        "\trundata.geo_data.friction_forcing = False\n"
        "\trundata.refinement_data.wave_tolerance = 1.e-5\n"
        "\trundata.refinement_data.speed_tolerance = [1e-8]\n"
        "\trundata.refinement_data.variable_dt_refinement_ratios = True\n"
        "\trundata.topo_data.topofiles.append([3, 'toy.asc'])\n"
        "\trundata.landspill_data.update_tol = rundata.geo_data.dry_tolerance\n"
        "\trundata.landspill_data.point_sources.n_point_sources = 1\n"
        "\trundata.landspill_data.point_sources.point_sources.append([[0., 0.], 1, [3600.], [1.48e-6]])\n"
        "\trundata.landspill_data.darcy_weisbach_friction.type = 4\n"
        "\trundata.landspill_data.darcy_weisbach_friction.dry_tol = 1e-4\n"
        "\trundata.landspill_data.darcy_weisbach_friction.friction_tol = 1e6\n"
        "\trundata.landspill_data.darcy_weisbach_friction.default_roughness = 0.0\n"
        "\trundata.landspill_data.darcy_weisbach_friction.filename = 'roughness.asc'\n"
        "\trundata.landspill_data.evaporation.type = 1\n"
        "\trundata.landspill_data.evaporation.coefficients = [1.38, 0.045]\n"
        "\treturn rundata\n"
    )

    with open(case_dir.joinpath("setrun.py"), "w") as fileobj:
        fileobj.write(content)

    with open(case_dir.joinpath("toy.asc"), "w") as fileobj:
        fileobj.write("ncols          4\n")
        fileobj.write("nrows          4\n")
        fileobj.write("xllcorner     -2.0\n")
        fileobj.write("yllcorner     -2.0\n")
        fileobj.write("cellsize       1.0\n")
        fileobj.write("NODATA_value  -9999\n")
        fileobj.write("\n")
        for _ in range(4):
            fileobj.write("0.0 0.0 0.0 0.0\n")

    with open(case_dir.joinpath("roughness.asc"), "w") as fileobj:
        fileobj.write("ncols          4\n")
        fileobj.write("nrows          4\n")
        fileobj.write("xllcorner     -2.0\n")
        fileobj.write("yllcorner     -2.0\n")
        fileobj.write("cellsize       1.0\n")
        fileobj.write("NODATA_value  -9999\n")
        fileobj.write("\n")
        for _ in range(4):
            fileobj.write("0.0 0.0 0.0 0.0\n")

    return case_dir


def test_run(create_case):
    """Test if the run succeeded."""
    case_dir = create_case
    sys.argv = ["geoclaw-landspill", "run", str(case_dir)]
    gclandspill.__main__.main()
    out_dir = case_dir.joinpath("_output")

    assert out_dir.is_dir()

    for prefix in ["b", "q", "t"]:
        for i in range(6):
            file_path = out_dir.joinpath("fort.{}{:04d}".format(prefix, i))
            assert file_path.is_file(), "{} not found".format(file_path)
    file_path = out_dir.joinpath("evaporated_fluid.dat")
    file_path = out_dir.joinpath("volumes.csv")


@pytest.mark.parametrize("frame", list(range(6)))
def test_raw_result(create_case, frame):
    """Test if the values of simulation results match."""
    case_dir = create_case

    ref = gclandspill.pyclaw.Solution()
    ref.read(frame, pathlib.Path(__file__).parent.joinpath("data", "regression-1"), "binary",  read_aux=False)

    soln = gclandspill.pyclaw.Solution()
    soln.read(frame, case_dir.joinpath("_output"), "binary",  read_aux=False)

    assert soln.state.t == pytest.approx(ref.state.t), "Frame {} does not match.".format(frame)
    assert len(soln.states) == len(ref.states), "Frame {} does not match.".format(frame)

    for this, that in zip(soln.states, ref.states):
        assert this.q.shape == that.q.shape, "Frame {} does not match.".format(frame)
        assert this.q == pytest.approx(that.q), "Frame {} does not match.".format(frame)


def test_createnc(create_case):
    """Test if the createnc succeeded."""
    case_dir = create_case
    sys.argv = ["geoclaw-landspill", "createnc", str(case_dir)]
    gclandspill.__main__.main()

    assert case_dir.joinpath("_output", "{}-depth-lvl02.nc".format(case_dir.name)).is_file()


def test_netcdf(create_case):
    """Test if the resulting NetCDF file matches the reference solution."""
    case_dir = create_case

    ref_file = pathlib.Path(__file__).parent.joinpath("data", "regression-1", "regression-1.nc")
    raster_file = case_dir.joinpath("_output", "{}-depth-lvl02.nc".format(case_dir.name))

    with rasterio.open(ref_file, "r") as ref, rasterio.open(raster_file, "r") as raster:
        assert str(raster.crs) == str(ref.crs)
        assert list(raster.bounds) == pytest.approx(list(ref.bounds))
        assert list(raster.transform) == pytest.approx(list(ref.transform))
        assert raster.count == ref.count
        assert raster.nodatavals == pytest.approx(ref.nodatavals)
        assert raster.block_shapes == pytest.approx(ref.block_shapes)
        assert raster.read().shape == pytest.approx(ref.read().shape)


def test_plotdepth(create_case):
    """Test if the plotdepth succeeded."""
    case_dir = create_case
    sys.argv = ["geoclaw-landspill", "plotdepth", "--no-topo", "--nprocs", "1", str(case_dir)]
    gclandspill.__main__.main()
    plot_dir = case_dir.joinpath("_plots", "depth", "level02")

    assert plot_dir.is_dir()

    for i in range(6):
        file_path = plot_dir.joinpath("frame0000{}.png".format(i))
        assert file_path.is_file(), "{} not found".format(file_path)


@pytest.mark.parametrize("frame", list(range(6)))
def test_png(create_case, frame):
    """Test if the RGB values of created figures match."""
    case_dir = create_case

    filename = "frame{:05d}.png".format(frame)
    ref = matplotlib.pyplot.imread(pathlib.Path(__file__).parent.joinpath("data", "regression-1", filename))
    img = matplotlib.pyplot.imread(case_dir.joinpath("_plots", "depth", "level02", filename))
    assert img.shape == ref.shape
    assert img == pytest.approx(ref)


def test_volumes(create_case):
    """Test subcommand volumes and the values."""
    case_dir = create_case

    # execute the subcommand
    sys.argv = ["geoclaw-landspill", "volumes", str(case_dir)]
    gclandspill.__main__.main()

    file_1 = pathlib.Path(__file__).parent.joinpath("data", "regression-1", "volumes.csv")
    file_2 = case_dir.joinpath("_output", "volumes.csv")

    with open(file_1, "r") as ref, open(file_2, "r") as result:
        reader_1 = csv.reader(ref)
        reader_2 = csv.reader(result)

        for line_1, line_2 in zip(reader_1, reader_2):
            try:
                line_1 = [float(i) for i in line_1]
                line_2 = [float(i) for i in line_2]
            except ValueError as err:
                if str(err) == "could not convert string to float: 'frame'":
                    pass
            assert line_2 == pytest.approx(line_1)


def test_evaporated_fluid(create_case):
    """Test the value in evaporated_fluid.dat."""
    case_dir = create_case
    file_1 = pathlib.Path(__file__).parent.joinpath("data", "regression-1", "evaporated_fluid.dat")
    file_2 = case_dir.joinpath("_output", "evaporated_fluid.dat")

    with open(file_1, "r") as ref, open(file_2, "r") as result:
        val_1 = float(ref.read())
        val_2 = float(result.read())
        assert val_2 == pytest.approx(val_1)
