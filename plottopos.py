#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
########################################################################################################################
# Copyright © 2019 The George Washington University.
# All Rights Reserved.
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
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
Plot the actual elevation data in AMR grid patches.
"""

import os
import sys
import datetime
import argparse
import rasterio
from matplotlib import pyplot


if __name__ == "__main__":

    # CMD argument parser
    parser = argparse.ArgumentParser(
        description="Plot elevations on AMR grid patches.")

    parser.add_argument(
        'case', metavar='case', type=str, help='the name of the case')

    parser.add_argument(
        '--level', dest="level", action="store", type=int,
        help='plot depth result at a specific AMR level (default: finest level)')

    parser.add_argument(
        '--cmax', dest="cmax", action="store", type=float,
        help='maximum value in the depth colorbar (default: obtained from solution)')

    parser.add_argument(
        '--cmin', dest="cmin", action="store", type=float,
        help='minimum value in the depth colorbar (default:  obtained from solution)')

    parser.add_argument(
        '--frame-bg', dest="frame_bg", action="store", type=int,
        help='customized start farme no. (default: 0)')

    parser.add_argument(
        '--frame-ed', dest="frame_ed", action="store", type=int,
        help='customized end farme no. (default: get from setrun.py)')

    parser.add_argument(
        '--continue', dest="restart", action="store_true",
        help='continue creating figures in existing _plot folder')

    parser.add_argument(
        '--border', dest="border", action="store_true",
        help='also plot the borders of grid patches')

    # process arguments
    args = parser.parse_args()

    # get case path
    casepath = os.path.abspath(args.case)

    # get the abs path of the repo
    repopath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

    # path to clawpack
    claw_dir = os.path.join(repopath, "solver", "clawpack")

    # set CLAW environment variable to satisfy some Clawpack functions' need
    os.environ["CLAW"] = claw_dir

    # make clawpack searchable
    sys.path.insert(0, claw_dir)

    # import utilities
    from pphelper import plot_soln_topo, get_bounding_box

    # load setup.py
    sys.path.insert(0, casepath) # add case folder to module search path
    import setrun # import the setrun.py

    rundata = setrun.setrun() # get ClawRunData object

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

    # process plot level
    if args.level is None:
        args.level = rundata.amrdata.amr_levels_max

    # find bounding box we're going to use for plots
    x_crop_bg, x_crop_ed, y_crop_bg, y_crop_ed = get_bounding_box(
        outputpath, frame_bg, frame_ed, rundata.amrdata.amr_levels_max)

    Dx = (x_crop_ed - x_crop_bg) * 0.1
    Dy = (y_crop_ed - y_crop_bg) * 0.1
    x_crop_bg -= Dx
    x_crop_ed += Dx
    y_crop_bg -= Dy
    y_crop_ed += Dy

    # read topo file
    topofilename = os.path.join(casepath, rundata.topo_data.topofiles[0][-1])
    raster = rasterio.open(topofilename)

    # adjust cropping bounds
    if x_crop_bg < raster.bounds.left:
        x_crop_bg = raster.bounds.left

    if y_crop_bg < raster.bounds.bottom:
        y_crop_bg = raster.bounds.bottom

    if x_crop_ed > raster.bounds.right:
        x_crop_ed = raster.bounds.right

    if y_crop_ed > raster.bounds.top:
        y_crop_ed = raster.bounds.top

    # window/extent object enclosing the cropped region
    window = raster.window(x_crop_bg, y_crop_bg, x_crop_ed, y_crop_ed)

    # read the cropped data
    topodata = raster.read(1, window=window)

    # source points; assume only one point source
    try:
        source = rundata.landspill_data.point_sources.point_sources[0][0]
    except:
        source = None

    # close the raster file
    raster.close()

    # create an extent list
    extent = [x_crop_bg, x_crop_ed, y_crop_bg, y_crop_ed]

    # folder of plots
    plotdir = os.path.join(casepath, "_plots/topos/level{:02}".format(args.level))
    if not os.path.isdir(plotdir):
        os.makedirs(plotdir)
    elif not args.restart:
        backup_plotdir = str(datetime.datetime.now().replace(microsecond=0))
        backup_plotdir = backup_plotdir.replace("-", "").replace(" ", "_").replace(":", "")
        backup_plotdir = plotdir + "_" + backup_plotdir
        print("Moving existing _plot/topos folder to {}".format(backup_plotdir))
        os.rename(plotdir, backup_plotdir)
        os.mkdir(plotdir)

    # read and plot solution with pyclaw
    for frameno in range(frame_bg, frame_ed):

        figpath = os.path.join(plotdir, "topo{:04d}.png".format(frameno))
        if os.path.isfile(figpath):
            print("Topo frame No. {} exists. Skip.".format(frameno))
            continue

        fig, ax = plot_soln_topo(
            topodata, extent, outputpath, frameno, [args.cmin, args.cmax],
            args.border, args.level)

        # plot point source
        if source is not None:
            line = ax.plot(source[0], source[1], 'r.', markersize=10)
            ax.legend(line, ["source"]) # label

        # save image
        fig.savefig(figpath, dpi=90)

        # clear
        pyplot.close(fig)
