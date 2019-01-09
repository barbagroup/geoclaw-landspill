#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Helper functions for post-processing.
"""

import os
import numpy
import matplotlib
from matplotlib import pyplot
from clawpack.geoclaw import topotools
from clawpack import pyclaw


def get_max_depth(solution):
    """
    Get the maximum dpeth.
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

def plot_at_axes(solution, ax, field=0, border=False,
                 min_level=2, max_level=None, shift=[0., 0.],
                 vmin=0, vmax=None, threshold=1e-4,
                 cmap=pyplot.cm.viridis):
    """Plot solution.

    Plot a field in the q array of a solution object.

    Args:
        solution [in]: pyClaw solution object.
        ax [inout]: matplotlib axes object.
        field [in]: target field to be plot:
                    0 - depth;
                    1 - hu conservative field;
                    2 - hv conservative field;
                    3 - eta (elevation + depth)
        border [in]: a boolean indicating whether to plot grid patch borders.
        min_levle [in]: the minimum level of AMR grid to be plotted.
        max_levle [in]: the maximum level of AMR grid to be plotted.
        shift [in]: size-2 1D list of the linear shifting in x and y direction.
        vmin [in]: value of the minimum value of the colorbar.
        vmax [in]: value of the maximum value of the colorbar.
        threshold [in]: values below this threshold will be clipped off.
        cmap [in]: pyplot colorbar theme.

    Return:
        pyplot image object/handler, or None.
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
            x, y, numpy.ma.masked_less(state.q[field, :, :], threshold).T,
            shading='flat', edgecolors='None',
            vmin=vmin, vmax=vmax, cmap=cmap)

        if border:
            ax.plot([x[0], x[-1], x[-1], x[0], x[0]],
                    [y[0], y[0], y[-1], y[-1], y[0]], 'k-', lw=2)

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
    xticks = xticks.round(2)
    xticks_loc = (xticks-xticks[0])/(topo.X.max()-topo.X.min()+topo.delta[0])*topo.Z.shape[1]
    ax_topo.set_xticks(xticks_loc)
    ax_topo.set_xticklabels(xticks, rotation=-45, ha="left")

    yticks = numpy.arange(topo.Y.min()-topo.delta[1]/2, topo.Y.max()+topo.delta[1]/2+49, 50)
    yticks = yticks.round(2)
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

def plot_depth(topo, solndir, fno, border=False, level=1):
    """Plot depth on topography."""

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
    im = plot_at_axes(soln, ax, field=0, border=border,
                      min_level=level, max_level=level,
                      shift=[topo.X.min()-topo.delta[0]/2,
                             topo.Y.min()-topo.delta[1]/2],
                      threshold=1e-5)

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
    fig.suptitle("Topography and depth near rupture point, "
                 "T = {} (mins)".format(int(soln.state.t/60.)),
                 x=0.5, y=0.9, fontsize=16,
                 horizontalalignment="center",
                 verticalalignment="bottom")

    return fig, ax
