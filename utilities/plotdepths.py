#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Plot topography and flow depth.
"""

import os
import sys
import datetime
import argparse
import multiprocessing

def plotting_task(inputs):
    """A single task to create a single plot for multi-threading."""
    from matplotlib import pyplot
    from pphelper import plot_depth

    # unroll parameters
    plot_dir, no, topo, soln_dir, opts, point = inputs

    fig_path = os.path.join(plot_dir, "depth{:04d}.png".format(no))
    if os.path.isfile(fig_path):
        print("Depth frame No. {} exists. Skip.".format(no))
        return

    figH, axH = plot_depth(
        topo, soln_dir, no, opts.border, opts.level, opts.dry_tol,
        opts.cmin, opts.cmax)

    # plot point source
    lineH = axH.plot(
        point[0]*topo.Z.shape[1]/(topo.extent[1]-topo.extent[0]),
        point[1]*topo.Z.shape[0]/(topo.extent[3]-topo.extent[2]),
        'r.', markersize=10)

    # label
    axH.legend(lineH, ["source"])

    # save image
    figH.savefig(fig_path, dpi=90)

    # clear
    pyplot.close(figH)

if __name__ == "__main__":

    # CMD argument parser
    parser = argparse.ArgumentParser(description="Plot depth on topography.")

    parser.add_argument(
        'case', metavar='case', type=str, help='the name of the case')

    parser.add_argument(
        '--level', dest="level", action="store", type=int,
        help='plot depth result at a specific AMR level (default: finest level)')

    parser.add_argument(
        '--dry-tol', dest="dry_tol", action="store", type=float,
        help='tolerance for dry state (default: obtained from setrun.py)')

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

    parser.add_argument(
        '--nprocs', dest="nprocs", action="store", type=int,
        help='plot depth result at a specific AMR level (default: half system threads)')

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
    from pphelper import TopographyMod, get_bounding_box

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

    # process dry_tol
    if args.dry_tol is None:
        args.dry_tol = rundata.geo_data.dry_tolerance

    # number of processes
    if args.nprocs is None:
        args.nprocs = 1

    # find bounding box we're going to use for plots
    x_crop_bg, x_crop_ed, y_crop_bg, y_crop_ed = \
        get_bounding_box(outputpath, frame_bg, frame_ed, args.level)

    Dx = (x_crop_ed - x_crop_bg) * 0.1
    Dy = (y_crop_ed - y_crop_bg) * 0.1
    x_crop_bg -= Dx
    x_crop_ed += Dx
    y_crop_bg -= Dy
    y_crop_ed += Dy

    # read topo file
    topofilename = os.path.join(casepath, rundata.topo_data.topofiles[0][-1])
    topo_raw = TopographyMod()
    topo_raw.read(topofilename, topo_type=3)
    topo_crop = topo_raw.crop([x_crop_bg, x_crop_ed, y_crop_bg, y_crop_ed])

    # source points; assume only one point source
    source_x = rundata.landspill_data.point_sources.point_sources[0][0][0]
    source_y = rundata.landspill_data.point_sources.point_sources[0][0][1]

    # folder of plots
    plotdir = os.path.join(casepath, "_plots/depths/level{:02}".format(args.level))
    if not os.path.isdir(plotdir):
        os.makedirs(plotdir)
    elif not args.restart:
        backup_plotdir = str(datetime.datetime.now().replace(microsecond=0))
        backup_plotdir = backup_plotdir.replace("-", "").replace(" ", "_").replace(":", "")
        backup_plotdir = plotdir + "_" + backup_plotdir
        print("Moving existing _plot/depths folder to {}".format(backup_plotdir))
        os.rename(plotdir, backup_plotdir)
        os.mkdir(plotdir)

    # location of the point in raster plots
    point_loc = [source_x-topo_crop.extent[0], source_y-topo_crop.extent[2]]

    # arg list for multiprocessing
    arglist = []

    # prepare arglist
    for frameno in range(frame_bg, frame_ed):
        arglist.append((plotdir, frameno, topo_crop, outputpath, args, point_loc))

    # multiprocesses
    p = multiprocessing.Pool(args.nprocs)
    result = p.map(plotting_task, arglist)
