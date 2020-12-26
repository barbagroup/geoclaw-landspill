#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Functions related to post-processing.
"""
import os
import sys
import datetime
import pathlib
import argparse
from typing import Optional, Tuple, TypedDict

import numpy
import rasterio
import rasterio.merge
from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from gclandspill import pyclaw
from gclandspill._misc import import_setrun, check_folder, str_to_bool, process_path


class AMRLevelError(Exception):
    """An error to raise when the target AMR level does not exist."""
    pass  # pylint: disable=unnecessary-pass


class DatetimeCtrlParams(TypedDict):
    """A type definition for the `dict` controlling the timestamps."""
    apply_datetime_stamp = bool
    datetime_stamp = str
    calendar_type = str


def convert_to_netcdf(args: argparse.Namespace):
    """Convert simulation binary results to a multi-band NetCDF file.

    This function should be called by `main()`.

    Arguments
    ---------
    args : argparse.Namespace
        The CMD arguments parsed by `argparse` package.

    Returns
    -------
    Execution code. 0 means all good. Other values means something wrong.
    """

    # process case path
    args.case = pathlib.Path(args.case).expanduser().resolve()
    check_folder(args.case)

    # case's setrun data
    rundata = import_setrun(args.case).setrun()

    # process target AMR level
    if args.level is None:
        args.level = rundata.amrdata.amr_levels_max

    # process args.frame_ed
    if args.frame_ed is not None:
        args.frame_ed += 1  # plus 1 so can be used as the `end` in the `range` function
    elif rundata.clawdata.output_style == 1:  # if it's None, and the style is 1
        args.frame_ed = rundata.clawdata.num_output_times
        if rundata.clawdata.output_t0:
            args.frame_ed += 1
    elif rundata.clawdata.output_style == 2:  # if it's None, and the style is 2
        args.frame_ed = len(rundata.clawdata.output_times)
    elif rundata.clawdata.output_style == 3:  # if it's None, and the style is 3
        args.frame_ed = int(rundata.clawdata.total_steps / rundata.clawdata.output_step_interval)
        if rundata.clawdata.output_t0:
            args.frame_ed += 1

    # process args.soln_dir
    args.soln_dir = process_path(args.soln_dir, args.case, "_output")
    check_folder(args.soln_dir)

    # process args.dest_dir
    args.dest_dir = process_path(args.dest_dir, args.case, args.soln_dir)
    os.makedirs(args.dest_dir, exist_ok=True)  # make sure the folder exists

    # process the NetCDF filename
    args.filename = process_path(
        args.filename, args.dest_dir, "{}-depth-lvl{:02}.nc".format(args.case.stem, args.level))
    os.makedirs(args.filename.parent, exist_ok=True)  # make sure the parent folder exists

    # process args.extent
    if args.extent is None:  # get the minimum extent convering the solutions at all frames
        args.extent = get_soln_bounding_box(args.soln_dir, args.frame_bg, args.frame_ed, args.level)

    # process args.res
    if args.res is None:  # get the resolution of the finest AMR grid from solutions
        args.res = min(get_level_res(args.soln_dir, args.frame_bg, args.frame_ed, args.level))

    # process args.dry_rol
    if args.dry_tol is None:  # get the dry tolerance from setrun.py
        args.dry_tol = rundata.geo_data.dry_tolerance

    # process args.use_case_settings and timestamp information
    case_settings_file = args.case.joinpath("case_settings.txt")

    # default values to be used if not args.use_case_settings
    datetime_ctrl = {
        "apply_datetime_stamp": True,
        "datetime_stamp": str(datetime.datetime.now().replace(microsecond=0)),
        "calendar_type": "standard",
    }

    # ---------------------------------------------------------------------------------------------
    # Read the case settings file which stores optional case parameters addressing full
    # NetCDF CF reference date compliance metadata.
    # 6/28/2019 - G2 Integrated Solutions - JTT
    # ---------------------------------------------------------------------------------------------
    if args.use_case_settings:  # will overwrite default values in `datetime_ctrl`
        with open(case_settings_file, "r") as fileobj:
            for line in fileobj:
                key, val = line.split("=")
                datetime_ctrl[key.lower()] = val.rstrip()
        datetime_ctrl["apply_datetime_stamp"] = str_to_bool(datetime_ctrl["apply_datetime_stamp"])

    # default metadata for the NetCDF file
    metadata = {
        "title": args.filename.stem,
        "institution": "geoclaw-landspill",
        "source": "geoclaw-landspill",
        "reference": "https://github.com/barbagroup/geoclaw-landspill",
        "comment": "N/A"
    }

    # create a NetCDF file with metadata
    init_nc_file(args.filename, args.extent, args.res, datetime_ctrl, args.nodata, **metadata)

    # write solutions into the NetCDF file
    write_soln_to_nc(
        args.filename, args.soln_dir, args.frame_bg, args.frame_ed, args.level, args.dry_tol,
        args.extent, args.res, args.nodata
    )

    return 0


def get_soln_bounding_box(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the bounding box of the results of all time frames at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    extent : tuple/list
        [xmin, ymin, xmax, ymax] (i.e., [west, south, east, north])
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()
    extent = [float("inf"), float("inf"), -float("inf"), -float("inf")]

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4))
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=aux.is_file())

        # search through AMR grid patches in this solution
        for state in soln.states:
            if state.patch.level != level:
                continue

            extent[0] = min(extent[0], state.patch.lower_global[0])
            extent[1] = min(extent[1], state.patch.lower_global[1])
            extent[2] = max(extent[2], state.patch.upper_global[0])
            extent[3] = max(extent[3], state.patch.upper_global[1])

    return extent


def get_level_res(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the resolution of the grid at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    dx, dy : float
        Cell size at x and y direction.
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4))
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=aux.is_file())

        # search through AMR grid patches, if found desired dx & dy at the level, quit
        for state in soln.states:
            if state.patch.level == level:
                return state.patch.delta

    raise AMRLevelError("No solutions has AMR level {}".format(level))


def interpolate(
        soln: pyclaw.Solution, level: int, dry_tol: float,
        extent: Optional[Tuple[float, float, float, float]] = None,
        res: Optional[float] = None, nodata: int = -9999
):
    """Merge grid patches at a level and interpolate to a given extent with a given resolution.

    This interpolation relies on the concept of mosaic raster, so it has to read all patches at
    that level into memory and hence is memory intense.

    Arguments
    ---------
    soln : pyclaw.Solution
        The solution object from Clawpack.
    level : int
        The target level of AMR grid to be used.
    dry_tol : float
        A cutoff values so that all pixels having values smaller than it will have `nodata` value.
    extent : tuple/list of (xmin, ymin, xmas, ymax)
        The bounds of the outpur/interpolated domain.
    res : float
        The grid/raster resolution of the output domain. X and Y direction will have the same
        resolution.
    nodata : int
        The value indicating that a cell/pixel is masked.

    Returns
    -------
    dst : numpy.ndarray
        The interpolated data. The shape is (n_rows, n_cols). Also, the order of rows is that used
        by `pyplot.imshow`, not the one used by `pyplot.contour`.
    affine : rasterio.transform.Affine
        An affine object that can be passed to raster file writer. An affine object describes how to
        convert from images' row-col indices into real coordinates.
    """
    # pylint: disable=too-many-arguments

    # kwargs to be passed to in-memory rasters
    child_raster_props = {
        "driver": "GTiff", "count": 1, "dtype": numpy.float, "nodata": nodata,
        "crs": rasterio.crs.CRS.from_epsg(3857),
        "height": None, "width": None, "transform": None,
    }

    memfiles = []  # backend memory files
    child_rasters = []  # container to hold opened in-memory rasters

    for state in soln.states:
        if state.patch.level != level:
            continue  # skip patches not on target level

        child_raster_props["transform"] = rasterio.transform.from_origin(
            state.patch.lower_global[0], state.patch.upper_global[1],
            state.patch.delta[0], state.patch.delta[1]
        )
        child_raster_props["height"] = state.patch.num_cells_global[1]
        child_raster_props["width"] = state.patch.num_cells_global[0]

        memfiles.append(rasterio.io.MemoryFile())
        child_rasters.append(memfiles[-1].open(**child_raster_props))
        child_rasters[-1].write(state.q[0].T[::-1, :], 1)

    # make a mosaic raster and interpolate to output domain
    dst, affine = rasterio.merge.merge(
        datasets=child_rasters, bounds=extent, res=res, nodata=nodata, precision=15,
        resampling=rasterio.enums.Resampling.cubic_spline)

    # filter out dry cells
    dst = numpy.where(dst < dry_tol, nodata, dst)

    # close dataset/clear memory
    for memfile, raster in zip(memfiles, child_rasters):
        raster.close()
        memfile.close()

    return dst[0], affine


def init_nc_file(
        nc_file: os.PathLike, extent: Tuple[float, float, float, float],
        res: float, time_ctl: DatetimeCtrlParams, nodata: int, **meta: str):
    """Initialize a multi-band NetCDF raster file for holding solutions.

    This only initialize the metadata, attributes, and variables in the NetCDF file. The real values
    are not written yet. The convention used is CF-1.7.

    Arguments
    ---------
    nc_file : pathlike
        The path of the NetCDF file to create.
    extent : a tuple of (xmin, ymin, xmax, ymax)
        The extent/bounds of the raster in the NetCDF file.
    res : float
        The resolution of the raster.
    time_ctl : DatetimeCtrlParams
        A dictionary holding parameters to control the timestamps of the bands in the raster.
    nodata : int
        The value representing masked cells.
    **meta : keyword parameters
        The followling optional keys can present:
        `title` : str (default to the filename),
        `institution` : str (default to "geoclaw-landspill")
        `source` : str (default to "geoclaw-landspill")
        `reference` : str (default to "https://github.com/barbagroup/geoclaw-landspill")
        `comment` : str (default to "N/A")
    """

    # calculate information of the raster to be written into the nc file
    affine = rasterio.transform.from_origin(extent[0], extent[3], res, res)
    window = rasterio.windows.from_bounds(*extent, affine)

    print("Creating NC file: {}".format(nc_file))

    # create a NC file and root group
    root = Dataset(filename=nc_file, mode="w", encoding="utf-8", format="NETCDF4")

    # set up dimension
    root.createDimension("time", None)
    root.createDimension("x", window.width)
    root.createDimension("y", window.height)

    # create variables
    nc_mercator = root.createVariable("mercator", 'S1')
    nc_times = root.createVariable("time", numpy.float64, ("time",))
    nc_x = root.createVariable("x", numpy.float64, ("x",))
    nc_y = root.createVariable("y", numpy.float64, ("y",))
    nc_depth = root.createVariable(
        "depth", numpy.float64, ("time", "y", "x"),
        fill_value=nodata, zlib=True, complevel=9
    )

    # global attributes
    root.title = meta["title"] if "title" in meta else "N/A"
    root.institution = meta["institution"] if "institution" in meta else "N/A"
    root.source = meta["source"] if "source" in meta else "N/A"
    root.history = "Created " + str(datetime.datetime.now().replace(microsecond=0))
    root.reference = meta["reference"] if "reference" in meta else "N/A"
    root.comment = meta["comment"] if "comment" in meta else "N/A"
    root.Conventions = "CF-1.7"

    # variable: time
    # --------------
    # Modifed to apply datetime stamp reference date, if present in the case_settings.txt file
    # 6/28/2019 - G2 Integrated Solutions - JTT
    print("Apply datetime stamp = {}".format(time_ctl["apply_datetime_stamp"]))
    if time_ctl["apply_datetime_stamp"]:  # Datetime stamp is specified in case_settings.txt
        print("Datetime stamp = {}".format(time_ctl["datetime_stamp"]))
        print("Calendar type = {}".format(time_ctl["calendar_type"]))
        nc_times.units = "seconds since " + time_ctl["datetime_stamp"]
        nc_times.calendar = time_ctl["calendar_type"].lower().replace(" ", "_")
    else:  # stamp is not specified in case_settings.txt
        nc_times.units = "sec"

    nc_times.axis, nc_times.long_name = "T", "Simulation time"

    # variable: x
    # -----------
    nc_x.units = "m"
    nc_x.long_name = "X-coordinate in EPSG:3857 WGS 84"
    nc_x.standard_name = "projection_x_coordinate"
    nc_x[:] = rasterio.transform.xy(affine, [0]*int(window.width), range(0, int(window.width)))[0]

    # variable: y
    # -----------
    nc_y.units = "m"
    nc_y.long_name = "Y-coordinate in EPSG:3857 WGS 84"
    nc_y.standard_name = "projection_y_coordinate"
    nc_y[:] = rasterio.transform.xy(affine, range(0, int(window.height)), [0]*int(window.height))[1]

    # variable: depth (attributes only)
    # ---------------------------
    nc_depth.units = "m"
    nc_depth.long_name = "Plume depth"
    nc_depth.grid_mapping = "mercator"

    # variable mercator (hard-code the WKT because Esri and Osgeo have different WKT)
    nc_mercator.grid_mapping_name = "mercator"
    nc_mercator.long_name = "CRS definition"
    nc_mercator.longitude_of_projection_origin = 0.0
    nc_mercator.standard_parallel = 0.0
    nc_mercator.false_easting = 0.0
    nc_mercator.false_northing = 0.0
    nc_mercator.spatial_ref = \
        "PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\"," + \
        "GEOGCS[\"GCS_WGS_1984\"," + \
        "DATUM[\"D_WGS_1984\"," + \
        "SPHEROID[\"WGS_1984\",6378137.0,298.257223563]]," + \
        "PRIMEM[\"Greenwich\",0.0]," + \
        "UNIT[\"Degree\",0.017453292519943295]]," + \
        "PROJECTION[\"Mercator_Auxiliary_Sphere\"]," + \
        "PARAMETER[\"False_Easting\",0.0]," + \
        "PARAMETER[\"False_Northing\",0.0]," + \
        "PARAMETER[\"Central_Meridian\",0.0]," + \
        "PARAMETER[\"Standard_Parallel_1\",0.0]," + \
        "PARAMETER[\"Auxiliary_Sphere_Type\",0.0]," + \
        "UNIT[\"Meter\",1.0]]"
    nc_mercator.GeoTransform = "{} {} {} {} {} {}".format(*affine.to_gdal())

    print("Closing NC file {}".format(nc_file))
    root.close()


def write_soln_to_nc(
        nc_file: os.PathLike, soln_dir: os.PathLike, frame_bg: int, frame_ed: int,
        level: int, dry_tol: float, extent: Tuple[float, float, float, float],
        res: float, nodata: int
):
    """Write solutions of time frames to band data of an existing NetCDF raster file.

    This function will first interpolate the simulation results onto a new uniform grid/raster with
    the giiven `extent` and `res` (resolution), and then it writes the solutions on this uniform
    grid to the NetCDF raster file.

    Arguments
    ---------
    nc_file : os.PathLike
        The path to the target NetCDF raster file.
    soln_dir : os.PathLike
        The folder where Clawutil's solution files are.
    frame_bg, frame_ed : int
        The beginning and end frame numbers. The end frame number should be one larger than the real
        end because it will be used in `range` funtion directly.
    level : int
        The target AMR level.
    dry_tol : float
        Depth below `dry_tol` will be treated as dry cells and have value `nodata`.
    extent : Tuple[float, float, float, float]
        The extent/bound of solution raster. The format is [xmin, ymin, xmax, ymax].
    res : float
        The resolution of the output
    nodata : int
        The value indicating a cell being masked.
    """  # pylint: disable=too-many-arguments

    # open the provided NC file and get the root group
    root = Dataset(filename=nc_file, mode="r+", encoding="utf-8", format="NETCDF4")

    print("Frame No. ", end="")
    for band, fno in enumerate(range(frame_bg, frame_ed)):

        print("..{}".format(fno), end="")
        sys.stdout.flush()

        # determine whether to read aux
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4)).is_file()

        # read in solution data
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=aux)

        # write the time
        root["time"][band] = soln.state.t

        # write the depth values
        root["depth"][band, :, :] = interpolate(soln, level, dry_tol, extent, res, nodata)[0]

    print()
    root.close()
