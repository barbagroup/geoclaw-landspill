#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
########################################################################################################################
# Copyright © 2019 The George Washington University and G2 Integrated Solutions, LLC.
# All Rights Reserved.
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
#               J. Tracy Thorleifson <tracy.thorleifson@g2-is.com>
#
# Licensed under the BSD-3-Clause License (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at: https://opensource.org/licenses/BSD-3-Clause
#
# BSD-3-Clause License:
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#    following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
#    promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
########################################################################################################################

"""
Write to NetCDF4 file with CF convention
"""

import os
import sys
import numpy
import netCDF4
import datetime
import argparse


def get_state_interpolator(state, field=0):
    """
    Get a Scipy interpolation object for a field on a AMR grid.
    """
    import scipy.interpolate

    # the underlying patch in this state object
    p = state.patch

    # x, y arrays and also dx, dy for checking
    x, dx = numpy.linspace(p.lower_global[0]+p.delta[0]/2.,
                           p.upper_global[0]-p.delta[0]/2.,
                           p.num_cells_global[0], retstep=True)
    y, dy = numpy.linspace(p.lower_global[1]+p.delta[1]/2.,
                           p.upper_global[1]-p.delta[1]/2.,
                           p.num_cells_global[1], retstep=True)
    assert numpy.abs(dx-p.delta[0]) < 1e-6, "{} {}".format(dx, p.delta[0])
    assert numpy.abs(dy-p.delta[1]) < 1e-6, "{} {}".format(dy, p.delta[1])

    # get the interpolation object
    kx = ky = 3

    if x.size <= 3:
        kx = x.size - 1

    if y.size <= 3:
        ky = y.size - 1

    interp = scipy.interpolate.RectBivariateSpline(
        x, y, state.q[field, :, :],
        [p.lower_global[0], p.upper_global[0], p.lower_global[1], p.upper_global[1]],
        kx=kx, ky=ky)

    return interp

def interpolate(solution, x_target, y_target,
                field=0, shift=[0., 0.], level=1,
                clip=True, clip_less=1e-7, nodatavalue=-9999.):
    """
    Do the interpolation.
    """

    # allocate space for interpolated results
    values = numpy.zeros((y_target.size, x_target.size), dtype=numpy.float64)

    # loop through all AMR grids
    for state in solution.states:

        p = state.patch

        # only do subsequent jobs if this is at the target level
        if p.level != level:
            continue

        # get the indices of the target coordinates that are inside this patch
        xid = numpy.where((x_target>=p.lower_global[0])&(x_target<=p.upper_global[0]))[0]
        yid = numpy.where((y_target>=p.lower_global[1])&(y_target<=p.upper_global[1]))[0]

        # get interpolation object
        interpolator = get_state_interpolator(state, field)

        # if any target coordinate located in thie patch, do interpolation
        if xid.size and yid.size:
            values[yid[:, None], xid[None, :]] = \
                interpolator(x_target[xid]-shift[0], y_target[yid]-shift[1]).T

    # apply nodatavalue to a threshold
    if clip:
        values[values<clip_less] = nodatavalue

    return values


if __name__ == "__main__":

    # get the abs path of the repo
    repopath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # path to clawpack
    claw_dir = os.path.join(repopath, "solver", "clawpack")

    # set CLAW environment variable to satisfy some Clawpack functions' need
    os.environ["CLAW"] = claw_dir

    # make clawpack searchable
    sys.path.insert(0, claw_dir)

    from clawpack import pyclaw
    from pphelper import get_bounding_box

    # CMD argument parser
    parser = argparse.ArgumentParser(
        description="Create a NC file with CF convention.")

    parser.add_argument(
        'case', metavar='case', type=str, help='the name of the case')

    parser.add_argument(
        '--level', dest="level", action="store", type=int,
        help='use data from a specific AMR level (default: finest level)')

    parser.add_argument(
        '--frame-bg', dest="frame_bg", action="store", type=int,
        help='customized start frame no. (default: 0)')

    parser.add_argument(
        '--frame-ed', dest="frame_ed", action="store", type=int,
        help='customized end frame no. (default: get from setrun.py)')

    # process arguments
    args = parser.parse_args()

    # get case path
    casepath = os.path.abspath(args.case)

    # check case dir
    if not os.path.isdir(casepath):
        print("Error: case folder {} does not exist.".format(casepath),
              file=sys.stderr)
        sys.exit(1)

    # check setup.py
    setrunpath = os.path.join(casepath, "setrun.py")
    if not os.path.isfile(setrunpath):
        print("Error: case folder {} does not have setrun.py.".format(casepath),
              file=sys.stderr)
        sys.exit(1)

    # check soln dir
    outputpath = os.path.join(casepath, "_output")
    if not os.path.isdir(outputpath):
        print("Error: output folder {} does not exist.".format(outputpath),
              file=sys.stderr)
        sys.exit(1)

    """
    Read the case settings file which stores optional case parameters addressing full
    NetCDF CF reference date compliance metadata.
    6/28/2019 - G2 Integrated Solutions - JTT
    """
    case_settings_file = os.path.join(casepath, "case_settings.txt")
    if not os.path.isfile(case_settings_file):
        print("Error: case folder {} does not have case_settings.txt.".format(casepath),
              file=sys.stderr)
        sys.exit(1)
    case_settings_dict = {}
    with open(case_settings_file) as f:
        for line in f:
            (key, val) = line.split("=")
            case_settings_dict[key] = val.rstrip()

    apply_datetime_stamp = case_settings_dict.get("APPLY_DATETIME_STAMP")
    datetime_stamp = case_settings_dict.get("DATETIME_STAMP")
    calendar_type = case_settings_dict.get("CALENDAR_TYPE")

    # load setup.py
    sys.path.insert(0, casepath) # add case folder to module search path
    import setrun # import the setrun.py

    rundata = setrun.setrun() # get ClawRunData object

    # computational domain
    x_domain_bg = rundata.clawdata.lower[0]
    x_domain_ed = rundata.clawdata.upper[0]
    y_domain_bg = rundata.clawdata.lower[1]
    y_domain_ed = rundata.clawdata.upper[1]

    # number of frames
    if args.frame_ed is not None:
        frame_ed = args.frame_ed + 1
    elif rundata.clawdata.output_style == 1:
        frame_ed = rundata.clawdata.num_output_times
        if rundata.clawdata.output_t0:
            frame_ed += 1
    elif rundata.clawdata.output_style == 2:
        frame_ed = len(rundata.clawdata.output_times)
    elif rundata.clawdata.output_style == 3:
        frame_ed = int(rundata.clawdata.total_steps /
                       rundata.clawdata.output_step_interval)
        if rundata.clawdata.output_t0:
            frame_ed += 1

    # starting frame no.
    if args.frame_bg is not None:
        frame_bg = args.frame_bg
    else:
        frame_bg = 0

    # process target level
    if args.level is None:
        args.level = rundata.amrdata.amr_levels_max

    # NC file path and name
    ncfilename = os.path.join(
        casepath, "{}_level{:02}.nc".format(
            os.path.basename(args.case), args.level))

    # find bounding box we're going to use for NC data
    xleft, xright, ybottom, ytop = \
        get_bounding_box(outputpath, frame_bg, frame_ed, args.level)

    # get the resolution at the target level
    dx = (x_domain_ed - x_domain_bg) / rundata.clawdata.num_cells[0]
    dx /= numpy.prod(rundata.amrdata.refinement_ratios_x[:args.level])
    dy = (y_domain_ed - y_domain_bg) / rundata.clawdata.num_cells[1]
    dy /= numpy.prod(rundata.amrdata.refinement_ratios_y[:args.level])

    # get the target coordinates based on dx, dy w/ flexibility of rounding err
    x = numpy.arange(xleft+dx/2., xright+dx/2, dx)
    y = numpy.arange(ybottom+dy/2., ytop+dy/2, dy)

    # revise the upper limit
    xright = x[-1]
    ytop = y[-1]

    # get the number of cells in the bounding box
    nx = x.size
    ny = y.size

    # dry tolerance
    threshold = rundata.geo_data.dry_tolerance


    # create a NC file and root group
    print("Creating NC file: {}".format(ncfilename))
    print("Apply datetime stamp = {}".format(apply_datetime_stamp))
    if apply_datetime_stamp == "True":
        print("Datetime stamp = {}".format(datetime_stamp))
        print("Calendar type = {}".format(calendar_type))
    rootgrp = netCDF4.Dataset(
        filename=ncfilename, mode="w",
        encoding="utf-8", format="NETCDF4")

    # set up dimension
    nc_ntime = rootgrp.createDimension("time", None)
    nc_nx = rootgrp.createDimension("x", nx)
    nc_ny = rootgrp.createDimension("y", ny)

    # create variables
    nc_times = rootgrp.createVariable("time", numpy.float64, ("time",))
    nc_x = rootgrp.createVariable("x", numpy.float64, ("x",))
    nc_y = rootgrp.createVariable("y", numpy.float64, ("y",))
    nc_depth = rootgrp.createVariable(
        "depth", numpy.float64, ("time", "y", "x"),
        fill_value=-9999., zlib=True, complevel=9)
    nc_mercator = rootgrp.createVariable("mercator", 'S1')

    # global attributes
    rootgrp.title = args.case
    rootgrp.institution = "G2 Integrated Solutions, LLC"
    rootgrp.source = "N/A"
    rootgrp.history = "Created " + str(datetime.datetime.now().replace(microsecond=0))
    rootgrp.reference = ""
    rootgrp.comment = ""
    rootgrp.Conventions = "CF-1.7"

    # variable: time
    # Modifed to apply datetime stamp reference date, if present in the case_settings.txt file
    # 6/28/2019 - G2 Integrated Solutions - JTT
    if not apply_datetime_stamp == "True":  # Datetime stamp is not specified in case_settings.txt
        nc_times.units = "sec"
    else:  # Datetime stamp is specified in case_settings.txt
        nc_times.units = "seconds since " + datetime_stamp
        nc_times.calendar = calendar_type.lower().replace(" ", "_")
    nc_times.axis = "T"
    nc_times.long_name = "Simulation time"

    # variable: x
    nc_x.units = "m"
    nc_x.long_name = "X-coordinate in EPSG:3857 WGS 84"
    nc_x.standard_name = "projection_x_coordinate"
    nc_x[:] = x

    # variable: y
    nc_y.units = "m"
    nc_y.long_name = "Y-coordinate in EPSG:3857 WGS 84"
    nc_y.standard_name = "projection_y_coordinate"
    nc_y[:] = y

    # variable attributes: depth
    nc_depth.units = "m"
    nc_depth.long_name = "Plume depth"
    nc_depth.grid_mapping = "mercator"

    # variable attributes: mercator
    nc_mercator.grid_mapping_name = "mercator"
    nc_mercator.long_name = "CRS definition"
    nc_mercator.longitude_of_projection_origin =0.0
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
    nc_mercator.GeoTransform = "{} {} 0 {} 0 {}".format(xleft, dx, ytop, -dy)

    # interpolate solution and write to NC file
    for fno in range(frame_bg, frame_ed):

        print("Frame No.", fno)

        # determine whether to read aux
        auxpath = os.path.join(outputpath, "fort.a"+"{}".format(fno).zfill(4))
        if os.path.isfile(auxpath):
            aux = True
        else:
            aux = False
        if os.path.isfile("./_output/fort.a" + "{}".format(fno).zfill(4)):
            aux = True

        soln = pyclaw.Solution()
        soln.read(fno, outputpath, file_format="binary", read_aux=aux)

        nc_times[fno-frame_bg] = soln.state.t
        nc_depth[fno-frame_bg, :, :] = interpolate(
            soln, x, y, level=args.level, nodatavalue=-9999.)

    print("Closing NC file {}".format(ncfilename))
    rootgrp.close()
