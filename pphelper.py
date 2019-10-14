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
Helper functions for post-processing.
"""
import os
import numpy
from clawpack import pyclaw


def get_min_value(solution, field=0):
    """
    Get the minimum value in a field in a solution.
    """

    min_val = 1e38

    for state in solution.states:
        min_temp = state.q[field, :, :].min()
        if min_temp < min_val:
            min_val = min_temp

    return min_val

def get_max_value(solution, field=0):
    """
    Get the maximum value in a field in a solution.
    """

    max_val = 0.

    for state in solution.states:
        max_temp = state.q[field, :, :].max()
        if max_temp > max_val:
            max_val = max_temp

    return max_val

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

def plot_at_axes(solution, ax, field=0, border=False,
                 min_level=2, max_level=None, vmin=None, vmax=None,
                 threshold=1e-4, cmap="viridis"):
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
        vmin [in]: value of the minimum value of the colorbar.
        vmax [in]: value of the maximum value of the colorbar.
        threshold [in]: values below this threshold will be clipped off.
        cmap [in]: pyplot colorbar theme.

    Return:
        pyplot image object/handler, or None.
    """

    if vmin is None:
        vmin = get_min_value(solution, field)

    if vmax is None:
        vmax = get_max_value(solution, field)

    for state in solution.states:
        p = state.patch

        if p.level < min_level:
            continue

        if max_level is not None and max_level < p.level:
            continue

        x, dx = numpy.linspace(p.lower_global[0], p.upper_global[0],
                               p.num_cells_global[0]+1, retstep=True)
        y, dy = numpy.linspace(p.lower_global[1], p.upper_global[1],
                               p.num_cells_global[1]+1, retstep=True)
        assert numpy.abs(dx-p.delta[0]) < 1e-6, "{} {}".format(dx, p.delta[0])
        assert numpy.abs(dy-p.delta[1]) < 1e-6, "{} {}".format(dy, p.delta[1])

        im = ax.pcolormesh(
            x, y, numpy.ma.masked_less(state.q[field, :, :], threshold).T,
            shading='flat', edgecolors='None',
            vmin=vmin, vmax=vmax, cmap=cmap)

        if border:
            ax.plot([x[0], x[-1], x[-1], x[0], x[0]],
                    [y[0], y[0], y[-1], y[-1], y[0]], 'k-', lw=1)

    try:
        return im
    except UnboundLocalError:
        return None

def plot_topo(data, transform, res, topo_min=None, topo_max=None,
              shaded=True, colormap="terrain"):
    """Return a fig and ax object with topography."""
    from matplotlib import colors
    from matplotlib import pyplot
    import rasterio.plot

    # a new figure
    fig = pyplot.figure(0, (13, 8), 90)

    # create an axes at 1, 3, 1
    ax_topo = fig.add_axes([0.1, 0.125, 0.65, 0.75])

    # light source
    ls = colors.LightSource(315, 45)

    # min and max
    if topo_min is None:
        topo_min = data.mean() - 2 * data.std()
    if topo_max is None:
        topo_max = data.mean() + 2 * data.std()

    if shaded:
        # get shaded RGBA data
        shaded = ls.shade(
            data, blend_mode="overlay", vert_exag=3, dx=res[0], dy=res[1],
            vmin=topo_min, vmax=topo_max, cmap=pyplot.get_cmap(colormap))

        # convert from (row, column, band) to (band, row, column)
        shaded = rasterio.plot.reshape_as_raster(shaded)

        # show topography in cropped region
        rasterio.plot.show(shaded, ax=ax_topo, transform=transform, adjust=None)
    else:
        rasterio.plot.show(
            data[-1::-1, :], ax=ax_topo, transform=transform,
            vmin=topo_min, vmax=topo_max,
            origin="lower", cmap=pyplot.get_cmap(colormap))

    # x, y labels
    ax_topo.set_xlabel("x coordinates (m)")
    ax_topo.set_ylabel("y coordinates (m)")

    # get x, y limit
    xlim = ax_topo.get_xlim()
    ylim = ax_topo.get_ylim()

    # plot colorbar in a new axes for topography
    cbarax = fig.add_axes([0.775, 0.125, 0.03, 0.75])
    im = ax_topo.imshow(
        data, cmap=colormap, vmin=topo_min, vmax=topo_max, origin='lower')
    im.remove()
    cbar = pyplot.colorbar(im, cax=cbarax, ax=ax_topo)
    cbar.set_label("Elevation (m)")

    # reset the x, y lim
    ax_topo.set_xlim(xlim)
    ax_topo.set_ylim(ylim)

    return fig, ax_topo

def plot_depth(data, transform, res, solndir, fno, border=False, level=1,
               shaded=True, dry_tol=1e-5, vmin=None, vmax=None):
    """Plot depth on topography."""
    from matplotlib import pyplot

    # a new figure and topo ax
    fig, ax = plot_topo(data, transform, res, shaded=shaded)

    # empty solution object
    soln = pyclaw.Solution()

    # aux path
    auxpath = os.path.join(solndir, "fort.a"+"{}".format(fno).zfill(4))

    # read
    soln.read(fno, solndir, file_format="binary", read_aux=os.path.isfile(auxpath))

    print("Plotting frame No. {}, T={} secs ({} mins)".format(
        fno, soln.state.t, int(soln.state.t/60.)))

    # plot
    im = plot_at_axes(soln, ax, field=0, border=border,
                      min_level=level, max_level=level,
                      vmin=vmin, vmax=vmax,
                      threshold=dry_tol)

    # plot colorbar in a new axes for depth
    cbarax = fig.add_axes([0.875, 0.125, 0.03, 0.75])
    if im is None:
        im = ax.pcolormesh([0, data.shape[1]], [0, data.shape[0]], [[0]])
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

def plot_soln_topo(topodata, extent, solndir, fno, color_lims=[None, None],
                   border=False, level=1):
    """Plot the topology from solution (instead of from topo file)"""
    from matplotlib import pyplot
    import rasterio.plot

    # empty solution object
    soln = pyclaw.Solution()

    # path
    auxpath = os.path.join(solndir, "fort.a"+"{}".format(fno).zfill(4))

    # read
    soln.read(fno, solndir, file_format="binary", read_aux=os.path.isfile(auxpath))

    print("Plotting frame No. {}, T={} secs ({} mins)".format(
        fno, soln.state.t, int(soln.state.t/60.)))

    # colormap min & max
    if color_lims[0] is None:
        color_lims[0] = topodata.mean() - 2 * topodata.std()

    if color_lims[1] is None:
        color_lims[1] = topodata.mean() + 2 * topodata.std()

    # a new figure
    fig = pyplot.figure(0, (11, 8), 90)

    # figure title
    fig.suptitle("Elevation data in AMR grid patches, "
                 "T = {} (mins)".format(int(soln.state.t/60.)),
                 x=0.5, y=0.9, fontsize=16,
                 horizontalalignment="center",
                 verticalalignment="bottom")

    # create an axes at 1, 3, 1
    ax = fig.add_axes([0.1, 0.125, 0.75, 0.75])

    # coordinate limit
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])

    # plot colorbar in a new axes for elevation
    cbarax = fig.add_axes([0.875, 0.125, 0.03, 0.75])
    im = ax.imshow(
        topodata, extent=extent, cmap="terrain",
        vmin=color_lims[0], vmax=color_lims[1], origin='lower')
    im.remove()
    cbar = pyplot.colorbar(im, cax=cbarax, ax=ax)
    cbar.set_label("Elevation (m)")

    # plot each patch on level 1
    for state in soln.states:
        plot_single_patch_topo(
            ax, state, 1, os.path.isfile(auxpath), color_lims,
            (level == 1 and border))

    # if the target level is one, exit the function now
    if level == 1:
        return fig, ax

    # plot each patch on target level
    for state in soln.states:
        plot_single_patch_topo(
            ax, state, level, os.path.isfile(auxpath), color_lims, border)

    return fig, ax

def plot_single_patch_topo(ax, state, level, aux, color_lims, border):
    """Plot elevation data of a single AMR grid patch."""
    import rasterio

    p = state.patch

    if p.level != level:
        return

    trans = rasterio.transform.from_origin(
        p.lower_global[0], p.upper_global[1], p.delta[0], p.delta[1])

    if aux:
        data = state.aux[0, :, :].T
    else:
        data = state.q[3, :, :].T - state.q[0, :, :].T

    rasterio.plot.show(
        data, ax=ax, transform=trans, adjust=None,
        vmin=color_lims[0], vmax=color_lims[1],
        origin="lower", cmap="terrain")

    if border:
        ax.plot(
            [p.lower_global[0], p.upper_global[0], p.upper_global[0],
             p.lower_global[0], p.lower_global[0]],
            [p.lower_global[1], p.lower_global[1], p.upper_global[1],
             p.upper_global[1], p.lower_global[1]],
            'k-', lw=1)

    return ax

def get_bounding_box(solndir, bg, ed, level):
    """
    Get the bounding box of the result at a specific level.

    Return:
        [xleft, xright, ybottom, ytop]
    """

    xleft = None
    xright = None
    ybottom = None
    ytop = None

    for fno in range(bg, ed):

        # aux path
        auxpath = os.path.join(solndir, "fort.a"+"{}".format(fno).zfill(4))

        # solution
        soln = pyclaw.Solution()
        soln.read(fno, solndir, file_format="binary", read_aux=os.path.isfile(auxpath))

        # search through AMR grid patched in this solution
        for state in soln.states:
            p = state.patch

            if p.level != level:
                continue

            if xleft is None or xleft > p.lower_global[0]:
                xleft = p.lower_global[0]

            if ybottom is None or ybottom > p.lower_global[1]:
                ybottom = p.lower_global[1]

            if xright is None or xright < p.upper_global[0]:
                xright = p.upper_global[0]

            if ytop is None or ytop < p.upper_global[1]:
                ytop = p.upper_global[1]

    # finally, return
    return [xleft, xright, ybottom, ytop]
