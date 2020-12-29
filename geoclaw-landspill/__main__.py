#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Main function of geoclaw-landspill.
"""
import pathlib
import argparse
import subprocess
import gclandspill
from gclandspill._preprocessing import create_data
from gclandspill._postprocessing.netcdf import convert_to_netcdf
from gclandspill._postprocessing.plotdepth import plot_depth
from gclandspill._postprocessing.plottopo import plot_topo
from gclandspill._postprocessing.volumes import create_volume_csv


def main():
    """Main function of geoclaw-landspill."""
    # pylint: disable=too-many-statements

    # main CMD parser
    parser = argparse.ArgumentParser(
        description="""
        Hydrocarbon overland spill solver and utilities.\n
        Use `geoclaw-landspill <COMMAND> --help` to see the usage of each command.
        """,
        epilog="GitHub page: https://github.com/barbagroup/geoclaw-landspill"
    )

    parser.add_argument(
        "--version", action='version', version='%(prog)s {}'.format(gclandspill.__version__))

    # subparser group
    subparsers = parser.add_subparsers(dest="cmd", metavar="<COMMAND>", required=True)

    # `run` command
    # ----------------------------------------------------------------------------------------------
    parser_run = subparsers.add_parser(
        name="run", help="Run a simulation.", description="Run a simulation.")
    parser_run.add_argument(
        "case", action="store", type=pathlib.Path, metavar="CASE",
        help="The path to the target case directory."
    )
    parser_run.set_defaults(func=run)  # set the corresponding callback for the `run` command

    # `createnc` command
    # ----------------------------------------------------------------------------------------------
    parser_createnc = subparsers.add_parser(
        name="createnc", help="Convert simulation results to NetCDF file with CF convention.",
        description="Convert simulation results to NetCDF file with CF convention."
    )
    parser_createnc.add_argument(
        "case", action="store", type=pathlib.Path, metavar="CASE",
        help="The path to the target case directory."
    )
    parser_createnc.add_argument(
        '--level', dest="level", action="store", type=int,
        help='Use data from a specific AMR level (default: finest level)')
    parser_createnc.add_argument(
        '--frame-bg', dest="frame_bg", action="store", type=int, default=0, metavar="FRAMEBG",
        help='Customize beginning frame No. (default: 0)')
    parser_createnc.add_argument(
        '--frame-ed', dest="frame_ed", action="store", type=int, metavar="FRAMEED",
        help='Customize end frame No. (default: get from setrun.py)')
    parser_createnc.add_argument(
        '--soln-dir', dest="soln_dir", action="store", type=pathlib.Path, default="_output",
        metavar="SOLNDIR", help="""
            Customize the folder holding solution files. A relative path will be assumed to be
            relative to CASE. (default: _output)
        """)
    parser_createnc.add_argument(
        '--dest-dir', dest="dest_dir", action="store", type=pathlib.Path, metavar="DESTDIR",
        help="""
            Customize the folder to save output file. A relative path will be assumed to be
            relative to CASE. Ignored if FILENAME is an absolute path. (default: same as SOLNDIR)')
        """)
    parser_createnc.add_argument(
        '--filename', dest="filename", action="store", type=pathlib.Path,
        help="""
            Customize the output raster file name. A relative path will be assumed to be
            relative to DESTDIR. (default: case name + level)
        """)
    parser_createnc.add_argument(
        '--extent', dest="extent", action="store", nargs=4, type=float, default=None,
        metavar=("XMIN", "YMIN", "XMAX", "YMAX"),
        help='Customize the output raster extent (default: determine from solutions)')
    parser_createnc.add_argument(
        '--res', dest="res", action="store", type=float, default=None,
        help='Customize the output raster resolution (default: determine from solutions)')
    parser_createnc.add_argument(
        '--dry-tol', dest="dry_tol", action="store", type=float, default=None,
        help='Customize the dry tolerance (default: get from setrun.py)')
    parser_createnc.add_argument(
        '--nodata', dest="nodata", action="store", type=int, default=-9999,
        help='Customize the nodata value (default: -9999)')
    parser_createnc.add_argument(
        "--use-case-settings", dest="use_case_settings", action="store_true",
        help="Use the timestamp settings in case_settings.txt under CASE")
    parser_createnc.set_defaults(func=convert_to_netcdf)  # callback for the `createnc` command

    # `plotdepth` command
    # ----------------------------------------------------------------------------------------------
    parser_plotdepth = subparsers.add_parser(
        name="plotdepth", help="Plot depth and output to a PNG figure per time frame.",
        description="Plot depth and output to a PNG figure per time frame."
    )
    parser_plotdepth.add_argument(
        "case", action="store", type=pathlib.Path, metavar="CASE",
        help="The path to the target case directory."
    )
    parser_plotdepth.add_argument(
        '--nprocs', dest="nprocs", action="store", type=int,
        help='Number of processers to use. (default: all usable logical CPU cores)')
    parser_plotdepth.add_argument(
        '--level', dest="level", action="store", type=int,
        help='Use data from a specific AMR level (default: finest level)')
    parser_plotdepth.add_argument(
        '--frame-bg', dest="frame_bg", action="store", type=int, default=0, metavar="FRAMEBG",
        help='Customize beginning frame No. (default: 0)')
    parser_plotdepth.add_argument(
        '--frame-ed', dest="frame_ed", action="store", type=int, metavar="FRAMEED",
        help='Customize end frame No. (default: get from setrun.py)')
    parser_plotdepth.add_argument(
        '--soln-dir', dest="soln_dir", action="store", type=pathlib.Path, default="_output",
        metavar="SOLNDIR", help="""
            Customize the folder holding solution files. A relative path will be assumed to be
            relative to CASE. (default: _output)
        """)
    parser_plotdepth.add_argument(
        '--dest-dir', dest="dest_dir", action="store", type=pathlib.Path, metavar="DESTDIR",
        help="""
            Customize the folder to save figures. A relative path will be assumed to be relative to
            CASE. (default: <CASE>/_plots/depth/level<LEVEL>))
        """)
    parser_plotdepth.add_argument(
        '--extent', dest="extent", action="store", nargs=4, type=float, default=None,
        metavar=("XMIN", "YMIN", "XMAX", "YMAX"),
        help='Customize the output extent (default: determine from solutions)')
    parser_plotdepth.add_argument(
        '--dry-tol', dest="dry_tol", action="store", type=float, default=None, metavar="DRYTOL",
        help='Customize the dry tolerance (default: get from setrun.py)')
    parser_plotdepth.add_argument(
        '--cmax', dest="cmax", action="store", type=float,
        help='Maximum value in the depth colorbar (default: obtained from solution)')
    parser_plotdepth.add_argument(
        '--cmin', dest="cmin", action="store", type=float, default=0.,
        help='Minimum value in the depth colorbar (default: 0)')
    parser_plotdepth.add_argument(
        '--cmap', dest="cmap", action="store", type=str, default="viridis",
        help='Colormap name for depth plosts (default: viridis)')
    parser_plotdepth.add_argument(
        '--no-topo', dest="no_topo", action="store_true",
        help="If sepcified, don't plot the topography below the depth.")
    parser_plotdepth.add_argument(
        '--colorize', dest="colorize", action="store_true",
        help="If sepcified, use colorized colormap for topographic elevation.")
    parser_plotdepth.add_argument(
        "--topo-azdeg", action="store", type=int, default=45, metavar="TOPOAZDEG",
        help="""
            The azimuth (0-360 degrees clockwise from North) of the light source. Only works if
            the topography is shown in shaded mode. (Defaults: 45 degrees).
        """)
    parser_plotdepth.add_argument(
        "--topo-altdeg", action="store", type=int, default=25, metavar="TOPOALTDEG",
        help="""
            The altitude (0-90 degrees up from horizontal) of the light source. Only works if
            the topography is shown in shaded mode. (Defaults: 25 degrees).
        """)
    parser_plotdepth.add_argument(
        '--topo-cmax', action="store", type=float, metavar="TOPOCMAX",
        help='Maximum value in the elevation colorbar (default: obtained from solution)')
    parser_plotdepth.add_argument(
        '--topo-cmin', action="store", type=float, metavar="TOPOCMIN",
        help='Minimum value in the elevation colorbar (default:  obtained from solution)')
    parser_plotdepth.add_argument(
        '--border', dest="border", action="store_true",
        help='Also plot the borders of grid patches')
    parser_plotdepth.set_defaults(func=plot_depth)  # callback for the `plotdepth` command

    # `plottopo` command
    # ----------------------------------------------------------------------------------------------
    parser_plottopo = subparsers.add_parser(
        name="plottopo", help="Plot runtime topography and output to a PNG figure per time frame.",
        description="This plots the topography data on AMR grids during simulation runtime."
    )
    parser_plottopo.add_argument(
        "case", action="store", type=pathlib.Path, metavar="CASE",
        help="The path to the target case directory."
    )
    parser_plottopo.add_argument(
        '--nprocs', dest="nprocs", action="store", type=int,
        help='Number of processers to use. (default: all usable logical CPU cores)')
    parser_plottopo.add_argument(
        '--level', dest="level", action="store", type=int,
        help='Plot up to this level (default: finest level)')
    parser_plottopo.add_argument(
        '--frame-bg', dest="frame_bg", action="store", type=int, default=0, metavar="FRAMEBG",
        help='Customize beginning frame No. (default: 0)')
    parser_plottopo.add_argument(
        '--frame-ed', dest="frame_ed", action="store", type=int, metavar="FRAMEED",
        help='Customize end frame No. (default: get from setrun.py)')
    parser_plottopo.add_argument(
        '--soln-dir', dest="soln_dir", action="store", type=pathlib.Path, default="_output",
        metavar="SOLNDIR", help="""
            Customize the folder holding solution files. A relative path will be assumed to be
            relative to CASE. (default: _output)
        """)
    parser_plottopo.add_argument(
        '--dest-dir', dest="dest_dir", action="store", type=pathlib.Path, metavar="DESTDIR",
        help="""
            Customize the folder to save figures. A relative path will be assumed to be relative to
            CASE. (default: <CASE>/_plots/topo))
        """)
    parser_plottopo.add_argument(
        '--extent', dest="extent", action="store", nargs=4, type=float, default=None,
        metavar=("XMIN", "YMIN", "XMAX", "YMAX"),
        help='Customize the output extent (default: determine from solutions)')
    parser_plottopo.add_argument(
        '--cmax', dest="cmax", action="store", type=float,
        help='Maximum value of runtime elevation (default: determined from aux files)')
    parser_plottopo.add_argument(
        '--cmin', dest="cmin", action="store", type=float,
        help='Minimum value of runtime elevation (default: determined from aux files)')
    parser_plottopo.add_argument(
        '--cmap', dest="cmap", action="store", type=str, default="viridis",
        help='Colormap name for depth plosts (default: viridis)')
    parser_plottopo.add_argument(
        '--border', dest="border", action="store_true",
        help='Also plot the borders of grid patches')
    parser_plottopo.set_defaults(func=plot_topo)  # callback for the `plottopo` command

    # `volumes` command
    # ----------------------------------------------------------------------------------------------
    parser_volumes = subparsers.add_parser(
        name="volumes", help="Calculate the total volumes at each AMR level.",
        description="Calculate and return a CSV file for total volumes at all AMR levels."
    )
    parser_volumes.add_argument(
        "case", action="store", type=pathlib.Path, metavar="CASE",
        help="The path to the target case directory."
    )
    parser_volumes.add_argument(
        '--frame-bg', dest="frame_bg", action="store", type=int, default=0, metavar="FRAMEBG",
        help='Customize beginning frame No. (default: 0)')
    parser_volumes.add_argument(
        '--frame-ed', dest="frame_ed", action="store", type=int, metavar="FRAMEED",
        help='Customize end frame No. (default: get from setrun.py)')
    parser_volumes.add_argument(
        '--soln-dir', dest="soln_dir", action="store", type=pathlib.Path, default="_output",
        metavar="SOLNDIR", help="""
            Customize the folder holding solution files. A relative path will be assumed to be
            relative to CASE. (default: _output)
        """)
    parser_volumes.add_argument(
        '--dest-dir', dest="dest_dir", action="store", type=pathlib.Path, metavar="DESTDIR",
        help="""
            Customize the folder to save output file. A relative path will be assumed to be
            relative to <CASE>. Ignored if <FILENAME> is an absolute path. (default: same as
            <SOLNDIR>)')
        """)
    parser_volumes.add_argument(
        '--filename', dest="filename", action="store", type=pathlib.Path,
        help="""
            Customize the output CSV file name. A relative path will be assumed to be
            relative to <DESTDIR>. (default: volumes.csv)
        """)
    parser_volumes.set_defaults(func=create_volume_csv)  # callback for the `volumes` command

    # parse the cmd
    # ----------------------------------------------------------------------------------------------
    args = parser.parse_args()

    # execute the corresponding subcommand and return code
    return args.func(args)


def run(args: argparse.Namespace):
    """Run a simulation using geoclaw-landspill Fortran binary.

    This function should be called by `main()`.

    Arguments
    ---------
    args : argparse.Namespace
        The CMD arguments parsed by `argparse` package.

    Returns
    -------
    Execution code. 0 means all good. Other values means something wrong.
    """

    # process path
    args.case = args.case.expanduser().resolve()
    assert args.case.is_dir()

    # the output folder of simulation results of this run
    args.output = args.case.joinpath("_output")

    # create *.data files, topology files, and hydrological file
    create_data(args.case, args.output)

    # get the Fortran solver binary
    solver = pathlib.Path(gclandspill.__file__).parents[1].joinpath("bin", "geoclaw-landspill-bin")

    if not solver.is_file():
        raise FileNotFoundError("Couldn't find solver at {}".format(solver))

    # execute the solver
    result = subprocess.run(solver, capture_output=False, cwd=str(args.output), check=True)

    return result.returncode


if __name__ == "__main__":
    import sys
    sys.exit(main())
