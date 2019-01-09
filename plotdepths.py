#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Plot topography and flow depth
"""

import os
import sys
import datetime
import argparse
from pphelper import plot_depth
from matplotlib import pyplot
from clawpack.geoclaw import topotools


if __name__ == "__main__":

    # CMD argument parser
    parser = argparse.ArgumentParser(description="Plot depth on topography.")

    parser.add_argument('case', metavar='case', type=str,
                        help='the name of the case')

    parser.add_argument('--level', dest="level", action="store", type=int,
                        help='plot depth result at a specific AMR level \
                                (default: finest level)')

    parser.add_argument('--continue', dest="restart", action="store_true",
                        help='continue creating figures in existing _plot folder')

    parser.add_argument('--border', dest="border", action="store_true",
                        help='also plot the borders of grid patches')

    # process arguments
    args = parser.parse_args()

    # get case path
    casepath = os.path.abspath(args.case)

    # get the abs path of the repo
    repopath = os.path.dirname(os.path.abspath(__file__))

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

    # folder of plots
    plotdir = os.path.join(casepath, "_plots")
    if not os.path.isdir(plotdir):
        os.mkdir(plotdir)
    elif not args.restart:
        backup_plotdir = plotdir + "_" + \
            str(datetime.datetime.now().replace(microsecond=0))
        print("Moving existing _plot folder to {}".format(backup_plotdir))
        os.rename(plotdir, backup_plotdir)
        os.mkdir(plotdir)

    # load setup.py
    sys.path.insert(0, casepath) # add case folder to module search path
    import setrun # import the setrun.py

    rundata = setrun.setrun() # get ClawRunData object

    # computational domain
    x_crop_bg = rundata.clawdata.lower[0]
    x_crop_ed = rundata.clawdata.upper[0]
    y_crop_bg = rundata.clawdata.lower[1]
    y_crop_ed = rundata.clawdata.upper[1]

    # read topo file
    topofilename = os.path.join(casepath, rundata.topo_data.topofiles[0][-1])
    topo_raw = topotools.Topography()
    topo_raw.read(topofilename, topo_type=3)
    topo_crop = topo_raw.crop([x_crop_bg, x_crop_ed, y_crop_bg, y_crop_ed])

    # source points
    source_x = rundata.landspill_data.point_sources.point_sources[0][0][0]
    source_y = rundata.landspill_data.point_sources.point_sources[0][0][1]

    # number of frames
    if rundata.clawdata.output_style == 1:
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

    frame_bg = 0

    # process plot level
    if args.level is None:
        args.level = rundata.amrdata.amr_levels_max

    # read and plot solution with pyclaw
    for frameno in range(frame_bg, frame_ed):

        figpath = os.path.join(plotdir, "frame{:04d}.png".format(frameno))
        if os.path.isfile(figpath):
            print("Frame No. {} exists. Skip.".format(frameno))
            continue

        fig, ax = plot_depth(topo_crop, outputpath, frameno,
                            args.border, args.level)

        # plot point source
        line = ax.plot(source_x-x_crop_bg, source_y-y_crop_bg, 'r.', markersize=10)

        # label
        legend = ax.legend(line, ["source"])

        # save image
        fig.savefig(figpath, dpi=90)

        # clear
        pyplot.close(fig)
