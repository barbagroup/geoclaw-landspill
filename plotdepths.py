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
import numpy
import matplotlib
from matplotlib import pyplot
from clawpack.geoclaw import topotools
from clawpack import pyclaw


def get_max_depth(solution):
    """
    """

    max_depth = 0.

    for state in solution.states:
        max_temp = state.q[0, :, :].max()
        if max_temp > max_depth:
            max_depth = max_temp

    return max_depth

def get_max_AMR_level(solution):
    """
    Get the max AMR level in a solution object.
    """

    max_level = 1

    for state in solution.states:
        p = state.patch

        if p.level > max_level:
            max_level = p.level

    return max_level

def get_level_ncells_volumes(solution):
    """
    Get level-wise numbers of cells and fluid volumes.
    """

    max_level = get_max_AMR_level(solution)

    ncells = numpy.zeros(max_level, dtype=numpy.int)
    volumes = numpy.zeros(max_level, dtype=numpy.float64)

    for state in solution.states:
        p = state.patch
        level = p.level

        ncells[level-1] += p.num_cells_global[0] * p.num_cells_global[1]
        volumes[level-1] += (numpy.sum(state.q[0, :, :]) * p.delta[0] * p.delta[1])

    return ncells, volumes

def plot_at_axes(solution, ax, min_level=2, max_level=None,
                 shift=[0., 0.], vmin=0, vmax=None, dry_tol=1e-4,
                 cmap=pyplot.cm.viridis):
    """
    Plot fluid depth
    """

    if vmax is None:
        vmax = get_max_depth(solution)

    for state in solution.states:
        p = state.patch

        if p.level < min_level:
            continue

        if max_level is not None:
            if p.level > max_level:
                continue

        x, dx = numpy.linspace(p.lower_global[0], p.upper_global[0],
                               p.num_cells_global[0]+1, retstep=True)
        y, dy = numpy.linspace(p.lower_global[1], p.upper_global[1],
                               p.num_cells_global[1]+1, retstep=True)
        assert numpy.abs(dx-p.delta[0]) < 1e-6, "{} {}".format(dx, p.delta[0])
        assert numpy.abs(dy-p.delta[1]) < 1e-6, "{} {}".format(dy, p.delta[1])

        x -= shift[0]
        y -= shift[1]

        im = ax.pcolormesh(
            x, y, numpy.ma.masked_less(state.q[0, :, :], dry_tol).T,
            shading='flat', edgecolors='None',
            vmin=vmin, vmax=vmax, cmap=cmap)

    try:
        return im
    except UnboundLocalError:
        return None

def plot_topo(topo, topo_min=None, topo_max=None, colormap=pyplot.cm.terrain):
    """Return a fig and ax object with topography."""

    # a new figure
    fig = pyplot.figure(0, (13, 8), 90)

    # create an axes at 1, 3, 1
    ax_topo = fig.add_axes([0.1, 0.125, 0.65, 0.75])

    # light source
    ls = matplotlib.colors.LightSource(315, 45)

    # min and max
    if topo_min is None:
        topo_min = topo.Z.mean() - 2 * topo.Z.std()
    if topo_max is None:
        topo_max = topo.Z.mean() + 2 * topo.Z.std()

    # show topography in cropped region
    ax_topo.imshow(
        ls.shade(
            topo.Z, blend_mode='overlay', vert_exag=3,
            dx=1, dy=1, vmin=topo_min, vmax=topo_max, cmap=colormap),
        origin='lower')

    # set x and y ticks
    xticks = numpy.arange(topo.X.min()-topo.delta[0]/2, topo.X.max()+topo.delta[0]/2+49, 50)
    xticks_loc = (xticks-xticks[0])/(topo.X.max()-topo.X.min()+topo.delta[0])*topo.Z.shape[1]
    ax_topo.set_xticks(xticks_loc)
    ax_topo.set_xticklabels(xticks, rotation=-45, ha="left")

    yticks = numpy.arange(topo.Y.min()-topo.delta[1]/2, topo.Y.max()+topo.delta[1]/2+49, 50)
    yticks_loc = (yticks-yticks[0])/(topo.Y.max()-topo.Y.min()+topo.delta[1])*topo.Z.shape[0]
    ax_topo.set_yticks(yticks_loc)
    ax_topo.set_yticklabels(yticks)

    # x, y labels
    ax_topo.set_xlabel("x coordinates (m)")
    ax_topo.set_ylabel("y coordinates (m)")


    # plot colorbar in a new axes for topography
    cbarax = fig.add_axes([0.775, 0.125, 0.03, 0.75])
    im = ax_topo.imshow(topo.Z, cmap=colormap,
                        vmin=topo_min, vmax=topo_max, origin='lower')
    im.remove()
    cbar = pyplot.colorbar(im, cax=cbarax, ax=ax_topo)
    cbar.set_label("Elevation (m)")

    return fig, ax_topo

def plot_soln(topo, solndir, fno):
    """Plot solutions."""

    # a new figure and topo ax
    fig, ax = plot_topo(topo)

    # empty solution object
    soln = pyclaw.Solution()

    # path
    auxpath = os.path.join(solndir, "fort.a"+"{}".format(fno).zfill(4))

    # determine whether to read aux
    if os.path.isfile(auxpath):
        aux = True
    else:
        aux = False

    # read
    soln.read(fno, solndir, file_format="binary", read_aux=aux)

    # calculate total volume at each grid level
    ncells, volumes = get_level_ncells_volumes(soln)

    print("Plotting frame No. {}, T={} secs ({} mins)".format(
        fno, soln.state.t, int(soln.state.t/60.)))

    print("\tFrame No. {}: N Cells: {}; Fluid volume: {}".format(
        fno, ncells, volumes))

    # plot
    im = plot_at_axes(soln, ax, min_level=2,
                      shift=[topo.X.min()-topo.delta[0]/2,
                             topo.Y.min()-topo.delta[1]/2],
                      dry_tol=1e-5)

    ax.set_xlim(0, topo.Z.shape[1])
    ax.set_ylim(0, topo.Z.shape[0])

    # plot colorbar in a new axes for depth
    cbarax = fig.add_axes([0.875, 0.125, 0.03, 0.75])
    if im is None:
        im = ax.pcolormesh([0, topo.Z.shape[1]], [0, topo.Z.shape[0]], [[0]])
        im.remove()
        cbar = pyplot.colorbar(im, cax=cbarax, ax=ax)
        cbar.ax.set_yticklabels([0]*len(cbar.ax.get_yticks()))
    else:
        cbar = pyplot.colorbar(im, cax=cbarax, ax=ax)
    cbar.set_label("Depth (m)")

    # figure title
    fig.suptitle("Topography and depth near breakage point, "
                 "T = {} (mins)".format(int(soln.state.t/60.)),
                 x=0.5, y=0.9, fontsize=16,
                 horizontalalignment="center",
                 verticalalignment="bottom")

    return fig, ax


if __name__ == "__main__":

    # help message
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("Usage:")
        print("\tpython plotdepths.py case_folder_name")
        sys.exit(0)

    # get case path
    case = sys.argv[1]
    casepath = os.path.abspath(case)

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

    # read and plot solution with pyclaw
    for frameno in range(frame_bg, frame_ed):

        figpath = os.path.join(plotdir, "frame{:04d}.png".format(frameno))
        if os.path.isfile(figpath):
            print("Frame No. {} exists. Skip.".format(frameno))
            continue

        fig, ax = plot_soln(topo_crop, outputpath, frameno)

        # plot point source
        line = ax.plot(source_x-x_crop_bg, source_y-y_crop_bg, 'r.', markersize=10)

        # label
        legend = ax.legend(line, ["source"])

        # save image
        fig.savefig(figpath, dpi=90)

        # clear
        pyplot.close(fig)
