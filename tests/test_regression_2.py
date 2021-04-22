#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Regression test 2."""
# pylint: disable=redefined-outer-name
import os
import sys
import csv
import pathlib
import numpy
import pytest
import rasterio
import matplotlib
import matplotlib.pyplot
import gclandspill.__main__
import gclandspill.pyclaw


@pytest.fixture(scope="session")
def create_case(tmp_path_factory):
    """A pytest fixture to make a temp case available across different tests."""
    # pylint: disable=invalid-name

    # force to use only 4 threads
    os.environ["OMP_NUM_THREADS"] = "4"

    # to avoid wayland session or none-X environment
    matplotlib.use("agg")

    case_dir = tmp_path_factory.mktemp("regression-test-2")

    content = (
        "#! /usr/bin/env python\n"
        "import gclandspill\n"
        "def setrun():\n"
        "\trundata = gclandspill.data.ClawRunData()\n"
        "\trundata.clawdata.lower[:] = [0.0, 0.0]\n"
        "\trundata.clawdata.upper[:] = [152.0, 60.0]\n"
        "\trundata.clawdata.num_cells[:] = [38, 15]\n"
        "\trundata.clawdata.output_style = 1\n"
        "\trundata.clawdata.num_output_times = 5\n"
        "\trundata.clawdata.tfinal = 65\n"
        "\trundata.clawdata.output_t0 = True\n"
        "\trundata.clawdata.dt_initial = 0.6\n"
        "\trundata.clawdata.dt_max = 4.0\n"
        "\trundata.topo_data.topofiles.append([3, 'topo.asc'])\n"
        "\trundata.landspill_data.ref_mu = 0.6512\n"
        "\trundata.landspill_data.density = 800.\n"
        "\trundata.landspill_data.point_sources.n_point_sources = 1\n"
        "\trundata.landspill_data.point_sources.point_sources.append([[20., 30.], 1, [1800.], [0.5]])\n"
        "\trundata.landspill_data.darcy_weisbach_friction.type = 4\n"
        "\trundata.landspill_data.darcy_weisbach_friction.default_roughness = 0.0\n"
        "\trundata.landspill_data.darcy_weisbach_friction.filename = 'roughness.asc'\n"
        "\trundata.landspill_data.hydro_features.files.append('hydro.asc')\n"
        "\treturn rundata\n"
    )

    with open(case_dir.joinpath("setrun.py"), "w") as fileobj:
        fileobj.write(content)

    X, Y = numpy.meshgrid(numpy.linspace(-0.5, 152.5, 154), numpy.linspace(-0.5, 60.5, 62))

    # init
    elevation = numpy.zeros_like(X, dtype=numpy.float64)
    hydro = numpy.ones_like(X, dtype=numpy.float64) * -9999

    # inclined entrance
    elevation[X <= 60.] = (60. - X[X <= 60.]) * numpy.tan(numpy.pi/36.)

    # mountains and channels
    idx_base = (X <= 70.)
    idx_low = numpy.logical_and(idx_base, (X-70.)**2+(Y+20.)**2 <= 48.5**2)
    idx_high = numpy.logical_and(idx_base, (X-70.)**2+(Y-80.)**2 <= 48.5**2)
    elevation[idx_low] = numpy.sqrt(48.5**2-(X[idx_low]-70.)**2-(Y[idx_low]+20.)**2)
    elevation[idx_high] = numpy.sqrt(48.5**2-(X[idx_high]-70.)**2-(Y[idx_high]-80.)**2)

    idx_base = numpy.logical_and(X > 70., X <= 90)
    idx_low = numpy.logical_and(idx_base, Y <= 28.5)
    idx_high = numpy.logical_and(idx_base, Y >= 31.5)
    elevation[idx_low] = numpy.sqrt(48.5**2-(Y[idx_low]+20)**2)
    elevation[idx_high] = numpy.sqrt(48.5**2-(Y[idx_high]-80.)**2)

    idx_base = (X >= 90.)
    idx_low = numpy.logical_and(idx_base, (X-90.)**2+(Y+20.)**2 <= 48.5**2)
    idx_high = numpy.logical_and(idx_base, (X-90.)**2+(Y-80.)**2 <= 48.5**2)
    elevation[idx_low] = numpy.sqrt(48.5**2-(X[idx_low]-90.)**2-(Y[idx_low]+20.)**2)
    elevation[idx_high] = numpy.sqrt(48.5**2-(X[idx_high]-90.)**2-(Y[idx_high]-80.)**2)

    # pool
    idx_low = numpy.logical_and(X >= 124., X <= 144.)
    idx_high = numpy.logical_and(Y >= 16, Y <= 44)
    idx_base = numpy.logical_and(idx_low, idx_high)
    elevation[idx_base] = -1.0
    hydro[idx_base] = 10.

    # clip high elevation values, because we don't need them
    elevation[elevation > 20.] = 20.

    # lift the elevation to above sea level
    elevation += 10.0

    headers = \
        "ncols           {}\n".format(X.shape[1]) + \
        "nrows           {}\n".format(X.shape[0]) + \
        "xllcorner       {}\n".format(-1.0) + \
        "yllcorner       {}\n".format(-1.0) + \
        "cellsize        {}\n".format(1.0) + \
        "NODATA_value    {}\n".format(-9999)

    with open(case_dir.joinpath("topo.asc"), "w") as fileobj:
        fileobj.write(headers)
        for j in reversed(range(X.shape[0])):
            elevation[j, :].tofile(fileobj, " ")
            fileobj.write("\n")

    roughness = numpy.zeros_like(elevation)

    with open(case_dir.joinpath("roughness.asc"), "w") as fileobj:
        fileobj.write(headers)
        for j in reversed(range(X.shape[0])):
            roughness[j, :].tofile(fileobj, " ")
            fileobj.write("\n")

    with open(case_dir.joinpath("hydro.asc"), "w") as fileobj:
        fileobj.write(headers)
        for j in reversed(range(X.shape[0])):
            hydro[j, :].tofile(fileobj, " ")
            fileobj.write("\n")

    return case_dir


def test_no_setrun(tmpdir):
    """Test expected error raised when no setrun.py exists."""
    sys.argv = ["geoclaw-landspill", "run", str(tmpdir)]
    with pytest.raises(FileNotFoundError) as err:
        gclandspill.__main__.main()
    assert err.type == FileNotFoundError


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
    ref.read(frame, pathlib.Path(__file__).parent.joinpath("data", "regression-2"), "binary",  read_aux=True)

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

    ref_file = pathlib.Path(__file__).parent.joinpath("data", "regression-2", "regression-2.nc")
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
    sys.argv = ["geoclaw-landspill", "plotdepth", "--border", "--nprocs", "1", str(case_dir)]
    gclandspill.__main__.main()
    plot_dir = case_dir.joinpath("_plots", "depth", "level02")

    assert plot_dir.is_dir()

    for i in range(6):
        file_path = plot_dir.joinpath("frame0000{}.png".format(i))
        assert file_path.is_file(), "{} not found".format(file_path)


@pytest.mark.skipif(matplotlib.__version__ != "3.3.3", reason="only check against matplotlib v3.3.3")
@pytest.mark.parametrize("frame", list(range(6)))
def test_depth_png(create_case, frame):
    """Test if the RGB values of created figures match."""
    case_dir = create_case

    filename = "frame{:05d}.png".format(frame)
    ref = matplotlib.pyplot.imread(pathlib.Path(__file__).parent.joinpath("data", "regression-2", "depth", filename))
    img = matplotlib.pyplot.imread(case_dir.joinpath("_plots", "depth", "level02", filename))
    assert img.shape == ref.shape
    assert img == pytest.approx(ref)


def test_plottopo(create_case):
    """Test if the plottopo succeeded."""
    case_dir = create_case
    sys.argv = ["geoclaw-landspill", "plottopo", "--border", "--nprocs", "1", str(case_dir)]
    gclandspill.__main__.main()
    plot_dir = case_dir.joinpath("_plots", "topo")

    assert plot_dir.is_dir()

    for i in range(6):
        file_path = plot_dir.joinpath("frame0000{}.png".format(i))
        assert file_path.is_file(), "{} not found".format(file_path)


@pytest.mark.skipif(matplotlib.__version__ != "3.3.3", reason="only check against matplotlib v3.3.3")
@pytest.mark.parametrize("frame", list(range(6)))
def test_topo_png(create_case, frame):
    """Test if the RGB values of created topo figures match."""
    case_dir = create_case

    filename = "frame{:05d}.png".format(frame)
    ref = matplotlib.pyplot.imread(pathlib.Path(__file__).parent.joinpath("data", "regression-2", "topo", filename))
    img = matplotlib.pyplot.imread(case_dir.joinpath("_plots", "topo", filename))
    assert img.shape == ref.shape
    assert img == pytest.approx(ref)


def test_volumes(create_case):
    """Test subcommand volumes and the values."""
    case_dir = create_case

    # execute the subcommand
    sys.argv = ["geoclaw-landspill", "volumes", str(case_dir)]
    gclandspill.__main__.main()

    file_1 = pathlib.Path(__file__).parent.joinpath("data", "regression-2", "volumes.csv")
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
    file_1 = pathlib.Path(__file__).parent.joinpath("data", "regression-2", "evaporated_fluid.dat")
    file_2 = case_dir.joinpath("_output", "evaporated_fluid.dat")

    with open(file_1, "r") as ref, open(file_2, "r") as result:
        val_1 = float(ref.read())
        val_2 = float(result.read())
        assert val_2 == pytest.approx(val_1)


def test_removed_fluid(create_case):
    """Test the value in test_removed_fluid.csv."""
    case_dir = create_case

    file_1 = pathlib.Path(__file__).parent.joinpath("data", "regression-2", "removed_fluid.csv")
    file_2 = case_dir.joinpath("_output", "removed_fluid.csv")

    with open(file_1, "r") as ref, open(file_2, "r") as result:
        reader_1 = csv.reader(ref)
        reader_2 = csv.reader(result)

        for line_1, line_2 in zip(reader_1, reader_2):
            line_1 = [float(i) for i in line_1]
            line_2 = [float(i) for i in line_2]
            assert line_2 == pytest.approx(line_1)
