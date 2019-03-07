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
import scipy.interpolate
import matplotlib
from matplotlib import pyplot
from clawpack.geoclaw import topotools
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
                 min_level=2, max_level=None, vmin=None, vmax=None,
                 threshold=1e-4, cmap=pyplot.cm.viridis):
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
              colormap=pyplot.cm.terrain):
    """Return a fig and ax object with topography."""
    import rasterio.plot

    # a new figure
    fig = pyplot.figure(0, (13, 8), 90)

    # create an axes at 1, 3, 1
    ax_topo = fig.add_axes([0.1, 0.125, 0.65, 0.75])

    # light source
    ls = matplotlib.colors.LightSource(315, 45)

    # min and max
    if topo_min is None:
        topo_min = data.mean() - 2 * data.std()
    if topo_max is None:
        topo_max = data.mean() + 2 * data.std()

    # get shaded RGBA data
    shaded = ls.shade(
        data, blend_mode="overlay", vert_exag=3, dx=res[0], dy=res[1],
        vmin=topo_min, vmax=topo_max, cmap=pyplot.cm.terrain)

    # convert from (row, column, band) to (band, row, column)
    shaded = rasterio.plot.reshape_as_raster(shaded)

    # show topography in cropped region
    rasterio.plot.show(shaded, ax=ax_topo, transform=transform, adjust=None)

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
               dry_tol=1e-5, vmin=None, vmax=None):
    """Plot depth on topography."""

    # a new figure and topo ax
    fig, ax = plot_topo(data, transform, res)

    # empty solution object
    soln = pyclaw.Solution()

    # aux path
    auxpath = os.path.join(solndir, "fort.a"+"{}".format(fno).zfill(4))

    # read
    soln.read(fno, solndir, file_format="binary", read_aux=os.path.isfile(auxpath))

    # calculate total volume at each grid level
    ncells, volumes = get_level_ncells_volumes(soln)

    print("Plotting frame No. {}, T={} secs ({} mins)".format(
        fno, soln.state.t, int(soln.state.t/60.)))

    print("\tFrame No. {}: N Cells: {}; Fluid volume: {}".format(
        fno, ncells, volumes))

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

def plot_soln_topo(topo, solndir, fno, border=False, level=1, shaded=False):
    """Plot the topology from solution (instead of from topo file)"""

    # a new figure
    fig = pyplot.figure(0, (11, 8), 90)

    # create an axes at 1, 3, 1
    ax = fig.add_axes([0.1, 0.125, 0.75, 0.75])

    # empty solution object
    soln = pyclaw.Solution()

    # path
    auxpath = os.path.join(solndir, "fort.a"+"{}".format(fno).zfill(4))

    # read
    soln.read(fno, solndir, file_format="binary", read_aux=os.path.isfile(auxpath))

    print("Plotting frame No. {}, T={} secs ({} mins)".format(
        fno, soln.state.t, int(soln.state.t/60.)))

    # colormap min & max
    topo_min = topo.Z.mean() - 2 * topo.Z.std()
    topo_max = topo.Z.mean() + 2 * topo.Z.std()

    # shift of physical coordinates to image pixel coordinates
    shift = [topo.X.min()-topo.delta[0]/2, topo.Y.min()-topo.delta[1]/2]

    # light source object
    ls = matplotlib.colors.LightSource(315, 45)

    # plot each patch on level 1
    for state in soln.states:
        p = state.patch

        if p.level != 1:
            continue

        x = numpy.linspace(p.lower_global[0], p.upper_global[0],
                           p.num_cells_global[0]+1, retstep=True)[0] - shift[0]
        y = numpy.linspace(p.lower_global[1], p.upper_global[1],
                           p.num_cells_global[1]+1, retstep=True)[0] - shift[1]

        if os.path.isfile(auxpath):
            data = state.aux[0, :, :]
        else:
            data = state.q[3, :, :] - state.q[0, :, :]

        if shaded:
            im = ax.imshow(
                ls.shade(data.T, blend_mode='soft', vert_exag=3,
                         dx=p.delta[0], dy=p.delta[1],
                         vmin=topo_min, vmax=topo_max,
                         cmap=pyplot.cm.terrain),
                origin='lower',
                extent=[x[0], x[-1], y[0], y[-1]])
        else:
            im = ax.pcolormesh(
                x, y, data.T,
                shading='flat', edgecolors='None',
                vmin=topo_min, vmax=topo_max, cmap=pyplot.cm.terrain)

        if level == 1 and border:
            ax.plot([x[0], x[-1], x[-1], x[0], x[0]],
                    [y[0], y[0], y[-1], y[-1], y[0]], 'k-', lw=1)

    # plot each patch on target level
    if level != 1:
        for state in soln.states:
            p = state.patch

            if p.level != level:
                continue

            x = numpy.linspace(p.lower_global[0], p.upper_global[0],
                               p.num_cells_global[0]+1, retstep=True)[0] - shift[0]
            y = numpy.linspace(p.lower_global[1], p.upper_global[1],
                               p.num_cells_global[1]+1, retstep=True)[0] - shift[1]

            if os.path.isfile(auxpath):
                data = state.aux[0, :, :]
            else:
                data = state.q[3, :, :] - state.q[0, :, :]

            if shaded:
                im = ax.imshow(
                    ls.shade(data.T, blend_mode='soft', vert_exag=3,
                             dx=p.delta[0], dy=p.delta[1],
                             vmin=topo_min, vmax=topo_max,
                             cmap=pyplot.cm.terrain),
                    origin='lower',
                    extent=[x[0], x[-1], y[0], y[-1]])
            else:
                im = ax.pcolormesh(
                    x, y, data.T,
                    shading='flat', edgecolors='None',
                    vmin=topo_min, vmax=topo_max, cmap=pyplot.cm.terrain)

            if border:
                ax.plot([x[0], x[-1], x[-1], x[0], x[0]],
                        [y[0], y[0], y[-1], y[-1], y[0]], 'k-', lw=1)

    ax.set_xlim(0, topo.Z.shape[1])
    ax.set_ylim(0, topo.Z.shape[0])

    xticks_loc = ax.get_xticks()
    xticks = numpy.array(
        [i/topo.Z.shape[1]*(topo.extent[1]-topo.extent[0])+topo.extent[0]
         for i in xticks_loc]).round(2)
    ax.set_xticklabels(xticks, rotation=-45, ha="left")

    yticks_loc = ax.get_yticks()
    yticks = numpy.array(
        [i/topo.Z.shape[0]*(topo.extent[3]-topo.extent[2])+topo.extent[1]
         for i in yticks_loc]).round(2)
    ax.set_yticklabels(yticks)

    # plot colorbar in a new axes for elevation
    cbarax = fig.add_axes([0.875, 0.125, 0.03, 0.75])
    im = ax.imshow(topo.Z, cmap=pyplot.cm.terrain,
                   vmin=topo_min, vmax=topo_max, origin='lower')
    im.remove()
    cbar = pyplot.colorbar(im, cax=cbarax, ax=ax)
    cbar.set_label("Elevation (m)")

    # figure title
    fig.suptitle("Elevation data in AMR grid patches, "
                 "T = {} (mins)".format(int(soln.state.t/60.)),
                 x=0.5, y=0.9, fontsize=16,
                 horizontalalignment="center",
                 verticalalignment="bottom")

    return fig, ax

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

def get_state_interpolator(state, field=0):
    """
    Get a Scipy interpolation object for a field on a AMR grid.
    """

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

class TopographyMod(topotools.Topography):
    """A Topography class without lambda."""
    def __init__(self, path=None, topo_func=None, topo_type=None,
                 unstructured=False):
        r"""Topography initialization routine.

        See :class:`Topography` for more info.

        """

        self.path = path
        self.topo_func = topo_func
        self.topo_type = topo_type

        self.unstructured = unstructured
        self.no_data_value = -9999

        # Data storage for only calculating array shapes when needed
        self._z = self._Z = self._x = self._X = self._y = self._Y = None
        self._extent = None
        self._delta = None

    def coordinate_transform(self, x, y):
        return (x, y)

    def crop(self, filter_region=None, coarsen=1):
        r"""Crop region to *filter_region*

        Create a new Topography object that is identical to this one but cropped
        to the region specified by filter_region

        :TODO:
         - Currently this does not work for unstructured data, could in principle
         - This could be a special case of in_poly although that routine could
           leave the resulting topography as unstructured effectively.
        """

        if self.unstructured:
            raise NotImplemented("*** Cannot currently crop unstructured topo")

        if filter_region is None:
            # only want to coarsen, so this is entire region:
            filter_region = [self.x[0],self.x[-1],self.y[0],self.y[-1]]

        # Find indices of region
        region_index = [None, None, None, None]
        region_index[0] = (self.x >= filter_region[0]).nonzero()[0][0]
        region_index[1] = (self.x <= filter_region[1]).nonzero()[0][-1] + 1
        region_index[2] = (self.y >= filter_region[2]).nonzero()[0][0]
        region_index[3] = (self.y <= filter_region[3]).nonzero()[0][-1] + 1
        newtopo = TopographyMod()

        newtopo._x = self._x[region_index[0]:region_index[1]:coarsen]
        newtopo._y = self._y[region_index[2]:region_index[3]:coarsen]

        # Force regeneration of 2d coordinate arrays and extent if needed
        newtopo._X = None
        newtopo._Y = None
        newtopo._extent = None

        # Modify Z array as well
        newtopo._Z = self._Z[region_index[2]:region_index[3]:coarsen,
                          region_index[0]:region_index[1]:coarsen]

        newtopo.unstructured = self.unstructured
        newtopo.topo_type = self.topo_type

        # print "Cropped to %s by %s array"  % (len(newtopo.x),len(newtopo.y))
        return newtopo
